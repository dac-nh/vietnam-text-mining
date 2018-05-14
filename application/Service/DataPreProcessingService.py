##
# 09/04/2018
# Created by Dac
##

# Load all files
import datetime
import glob
import json
import os
import re

##
# FUNCTIONS
##
import pandas as pd
from gensim.models import Word2Vec
# Training gensim model
from nltk import ngrams

# remove punctuation
import application.Repository.GeneralRepository as GeneralRepository
import application.Service.WordProcessing as WordProcessing


def transform_row(row):
    # Xóa số dòng ở đầu câu
    row = re.sub(r"^[0-9\.]+", "", row)

    # Xóa dấu chấm, phẩy, hỏi ở cuối câu
    row = re.sub(r"[\.,\?]+$", "", row)

    # Xóa tất cả dấu chấm, phẩy, chấm phẩy, chấm thang, ... trong câu
    row = row.replace(",", " ").replace(".", " ") \
        .replace(";", " ").replace("“", " ") \
        .replace(":", " ").replace("”", " ") \
        .replace('"', " ").replace("'", " ") \
        .replace("!", " ").replace("?", " ")

    row = row.strip()
    return row


# word embeddings
def to_ngram(string, n=1):
    """
    To ngram
    :param string: list string
    :param n: number of elements in a words
    :return result: list of words
    """
    result = []
    gram_str = list(ngrams(string.split(), n))
    stopwords = []  # stopwords

    # 7/4/2018: Dac: read file stopwords
    stopwords_file = open("Library/stored/stopwords-nlp-vi.txt", "r", encoding='UTF-8')
    if stopwords_file.mode == 'r':
        lines = stopwords_file.readlines()
        for line in lines:
            stopwords.append(line.replace('\n', ''))

    # 7/4/2018: Dac: remove all words that contained in stopwords
    for gram in gram_str:
        word = " ".join(gram).lower()
        if word not in stopwords:
            result.append(word)
    return result


# Generate word2vec model from date and to date
def generate_word2vec_model(category, from_date, to_date='0'):
    """
    Generate word2vec model from date and to date
    :param category:
    :param from_date: > from date
    :param to_date: <= to_date
    """
    print('Generating Word2Vec Model Of Category: {0}'.format(category))
    path = "Library/Model/" + category + "/word2vec_model"  # model path
    try:
        # Query data from Neo4j
        results = GeneralRepository.get_paper_by_category_and_date(category, from_date, to_date)

        train_data = []
        for element in results:
            sentences = json.loads(element[0]['sentence'])
            for sentence in sentences:
                train_data.append(sentence)

        try:
            if os.path.exists(path):
                # update model
                model = Word2Vec.load(path)
                model.build_vocab(sentences=train_data, update=True)  # update vocabulary
                model.train(sentences=train_data)  # train data

                model.save(path)  # save model to file
            else:
                # generate new model
                model = Word2Vec(train_data, size=100, window=10, min_count=3, workers=4, sg=1)
                os.makedirs("Library/Model/" + category)  # create folder
                model.save(path)  # save model to file

        except Exception as e:
            print("[Model Processing] Failed Word2Vec with error: {0}".format(e.args[0]))
    except Exception as e:
        print("[Model Processing] Retrieving Data from Neo4j failed with error: {0}".format(e.args[0]))

    print('Generating Word2Vec Model Of Category: {0} Successfully'.format(category))
    return path


# Data analyzing
def data_analyzing(path, category_nodes, last_processed_date):
    """
    Data Analyzing is using to store paper and date.
    :param last_processed_date:  get the previous processed date
    :param path: path to root folder
    :param category_nodes: array of each category node
    :return: the last processed paper
    """
    print('Analyzing Data process\n')
    current_date = ""

    # 2018-04-24: Dac: prepare data to write to time_log
    start_time = datetime.datetime.now()  # Start time for writing log file
    paper_num = 0  # number of papers
    date_num = 0

    # Loop all date
    for date_of_paper_path in glob.glob(path.pop() + '/*'):  # date of paper
        # 2018-04-24: Dac: update paper_num
        date_num += 1

        current_date = os.path.basename(date_of_paper_path)  # get current processing date
        # skip all processed date
        if current_date <= last_processed_date:
            print('Date {0} has been processed. PASS!'.format(current_date))
            continue

        print('Processing papers in date ' + current_date)

        # save current date into neo4j
        current_date_node = GeneralRepository.create_date_node(current_date)
        if current_date_node:
            current_date_node = current_date_node['data']

        # Loop all category in date
        for category_path in glob.glob(date_of_paper_path + '/*'):  # category of paper
            current_category = os.path.basename(category_path)  # get current processing category

            # Loop each paper of category in date
            for paper in glob.glob(category_path + '/*'):  # each paper processing
                # 2018-04-24: Dac: update paper_num
                paper_num += 1

                paper_name = os.path.basename(paper)
                df = {}
                try:
                    # extract sentence in paper
                    df = pd.read_csv(paper, sep="/", names=["row"]).dropna()
                    df["row"] = df.row.apply(transform_row)
                    df["1gram"] = df.row.apply(lambda t: to_ngram(t, 1))
                    # df["2gram"] = df.row.apply(lambda t: to_ngram(t, 2))
                    df["context"] = df["1gram"]  # + df["2gram"]

                    # Get paper title
                    paper_title = df["row"].get(0)

                    # Store all sentences in train_data
                    paper_sentences_in_array = []
                    for sentence in df.context.tolist():
                        paper_sentences_in_array.append(sentence)

                    paper_sentences = json.dumps(
                        paper_sentences_in_array)  # Json to string use json.loads(paper_sentences)

                    # Save to database
                    result_create_paper_node = GeneralRepository.create_paper_node(paper_title, paper,
                                                                                   paper_sentences,
                                                                                   category_nodes,
                                                                                   current_category,
                                                                                   current_date_node)
                    if not result_create_paper_node['code']:
                        print('[data_analyzing] Failed at create_paper_node\n')
                except Exception as e:
                    print('[DATA ANALYZING] Failed processing at paper: ' + paper_name)

    # 2018-04-24: Dac: prepare data to write to time_log
    end_time = datetime.datetime.now()  # Stop time for writing log file
    pre_processing_time_log = '{0}\t\t\t{1}\t\t\t{2}\t\t\t{3} ms'.format(datetime.datetime.now().strftime("%Y-%m-%d"),
                                                                         date_num, paper_num,
                                                                         (end_time - start_time).total_seconds() * 1000)

    result = {'last_processed_date': current_date, 'pre_processing_time_log': pre_processing_time_log}
    print('Analyzing Data successfully\n')
    return result


##
# MAIN
##

def generate_word_2_vec():
    """
    Pre Processing
    :return: code, pre_processing_time_log
    """
    # Enable logging
    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # Get list category in database
    category_nodes = GeneralRepository.get_category_in_neo4j()  # list category nodes

    # read file
    root_folder = glob.glob("preprocessing_data")

    # analyzing data
    last_processed_date = open("Library/stored/last_processing.txt", "r", encoding='UTF-8').readlines().pop()
    result_data_analyzing = data_analyzing(root_folder, category_nodes, last_processed_date)

    # generate word2vec model
    # 2018-04-24: Dac: prepare data to write to time_log
    start_time = datetime.datetime.now()
    for category in category_nodes.keys():
        category_nodes[category].set('model', generate_word2vec_model(category, last_processed_date))
    end_time = datetime.datetime.now()

    # writing last processed date to file
    if last_processed_date < result_data_analyzing['last_processed_date']:
        f = open("Library/stored/last_processing.txt", "a+")
        f.write('\n' + result_data_analyzing['last_processed_date'])
        f.close()

    # 2018-04-24: Dac: update pre_processing_time_log
    pre_processing_time_log = result_data_analyzing['pre_processing_time_log'] + '\t\t\t{0} ms'.format(
        (end_time - start_time).total_seconds() * 1000)  # update generate_word2vec time

    result = {}
    result['code'] = True
    result['pre_processing_time_log'] = pre_processing_time_log

    return result


# 2018-04-24: Dac: writing to time_log_pre_processing
pre_processing_time_log = generate_word_2_vec()['pre_processing_time_log']
pre_processing_time_log += WordProcessing.run()['pre_processing_time_log']

f = open("Library/stored/time_log_pre_processing.txt", "a+")
f.write('\n' + pre_processing_time_log)
f.close()
