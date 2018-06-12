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
import application.Library.Constant.GeneralConstant as GeneralConstant
import application.Repository.GeneralRepository as GeneralRepository


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
    stopwords_file = open(GeneralConstant.VN_STOP_WORD_PATH(), "r", encoding='UTF-8')
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
    path = "..\\Library\\Model\\" + category + "\\word2vec_model"  # model path
    try:
        # Query data from Neo4j
        results = GeneralRepository.get_papers_by_category_and_date(category, from_date, to_date)

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
                model.train(sentences=train_data, total_examples=model.corpus_count)  # train data

                model.save(path)  # save model to file
            else:
                # generate new model
                model = Word2Vec(train_data, size=100, window=10, min_count=3, workers=4, sg=1)
                os.makedirs("..\\Library\\Model\\" + category)  # create folder
                model.save(path)  # save model to file
            print('Generating Word2Vec Model Of Category: {0} Successfully'.format(category))
        except Exception as e:
            print("[Model Processing] Failed Word2Vec with error: {0}".format(e.args[0]))
    except Exception as e:
        print("[Model Processing] Retrieving Data from Neo4j failed with error: {0}".format(e.args[0]))
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
    result = {}
    result['code'] = GeneralConstant.RESULT_FALSE()
    current_date = ""
    # 2018-04-24: Dac: prepare data to write to time_log
    start_time = datetime.datetime.now()  # Start time for writing log file
    paper_num = 0  # number of papers
    date_num = 0
    # Loop all date
    for date_of_paper_path in glob.glob(path.pop() + '\\*'):  # date of paper
        # 2018-04-24: Dac: update paper_num
        date_num += 1
        current_date = os.path.basename(date_of_paper_path)  # get current processing date
        # skip all processed date
        if current_date <= last_processed_date:
            print('Date {0} has been processed. PASS!'.format(current_date))
            continue
        print('Processing papers of date ' + current_date)
        # save current date into neo4j
        current_date_node = GeneralRepository.create_date_node(current_date)
        if current_date_node:
            current_date_node = current_date_node['data']
        # Loop all category in date
        for category_path in glob.glob(date_of_paper_path + '\\*'):  # category of paper
            current_category = os.path.basename(category_path)  # get current processing category
            print('\tProcessing papers of category ' + current_category)
            # Loop each paper of category in date
            for processed_paper in glob.glob(category_path + '\\*'):  # each paper processing
                # 2018-04-24: Dac: update paper_num
                paper_num += 1
                paper_name = os.path.basename(processed_paper)
                print('\t\tProcessing paper ' + paper_name)
                try:
                    # extract sentence in paper
                    df = pd.read_csv(processed_paper, sep="/", names=["row"]).dropna()
                    df["row"] = df.row.apply(transform_row)
                    df["1gram"] = df.row.apply(lambda t: to_ngram(t, 1))
                    # df["2gram"] = df.row.apply(lambda t: to_ngram(t, 2))
                    df["context"] = df["1gram"]  # + df["2gram"]
                    # Get paper title and paper path
                    # 2018-06-05: Dac: Point to the original content paper
                    original_paper = processed_paper.replace(GeneralConstant.PROCESSED_DATA_PATH(),
                                                             GeneralConstant.ORIGINAL_DATA_PATH())
                    if not os.path.isfile(original_paper):  # if this paper does not exist in OriginalData
                        print('[data_analyzing] Original Paper is not found: {0}'.format(original_paper))
                        continue
                    f = open(original_paper, "r", encoding='UTF-8')
                    paper_name = f.readline().replace('\n', '').replace('\'', '\"')
                    f.close()
                    # Store all sentences in train_data
                    paper_sentences_in_array = []
                    for sentence in df.context.tolist():
                        paper_sentences_in_array.append(sentence)
                    # Json to string use json.loads(paper_sentences)
                    paper_sentences = json.dumps(paper_sentences_in_array)
                    # Save to database
                    result_create_paper_node = GeneralRepository.create_paper_node(paper_name, original_paper,
                                                                                   processed_paper, paper_sentences,
                                                                                   category_nodes, current_category,
                                                                                   current_date_node)
                    if result_create_paper_node['code'] == GeneralConstant.RESULT_FALSE():
                        print('[data_analyzing] Failed at create_paper_node at paper: {0}'.format(paper_name))
                    # case delete duplicate file
                    elif result_create_paper_node['code'] == GeneralConstant.DELETE_PAPER():
                        os.remove(original_paper)  # delete original file
                        os.remove(processed_paper)  # delete processed file
                        print('\t\tDelete duplicate paper: {0}'.format(paper_name))
                except Exception as e:
                    print('[DATA ANALYZING] Failed processing at paper: {0} with exception: {1}'.format(paper_name,
                                                                                                        e.args[0]))
    # 2018-04-24: Dac: prepare data to write to time_log
    end_time = datetime.datetime.now()  # Stop time for writing log file
    pre_processing_time_log = '{0}\t\t\t{1}\t\t\t{2}\t\t\t{3} ms'.format(datetime.datetime.now().strftime("%Y-%m-%d"),
                                                                         date_num, paper_num,
                                                                         (end_time - start_time).total_seconds() * 1000)
    result = {'code': GeneralConstant.RESULT_TRUE(), 'last_processed_date': current_date,
              'pre_processing_time_log': pre_processing_time_log}
    print('Analyzing Data successfully\n')
    return result


def generate_word_2_vec():
    """
    Pre Processing
    :return: code, pre_processing_time_log
    """
    # Enable logging
    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    # Get list category in database
    category_nodes = GeneralRepository.category_nodes  # list category nodes
    # read file
    root_folder = glob.glob(GeneralConstant.PROCESSED_DATA_PATH())
    # analyzing data default is 0
    last_processed_date = '0'
    if os.path.isfile(GeneralConstant.LAST_PROCESSING_DATE_PATH()):
        f = open(GeneralConstant.LAST_PROCESSING_DATE_PATH(), "r+", encoding='UTF-8')
        last_processed_date = f.readlines()[-1]
        f.close()
    result_data_analyzing = data_analyzing(root_folder, category_nodes, last_processed_date)
    # generate word2vec model
    # 2018-04-24: Dac: prepare data to write to time_log
    start_time = datetime.datetime.now()
    for category in category_nodes.keys():
        category_nodes[category].set('model', generate_word2vec_model(category, last_processed_date))
    end_time = datetime.datetime.now()
    # writing last processed date to file
    if last_processed_date < result_data_analyzing['last_processed_date']:
        f = open(GeneralConstant.LAST_PROCESSING_DATE_PATH(), "a")
        f.write('\n' + result_data_analyzing['last_processed_date'])
        f.close()
    # 2018-04-24: Dac: update pre_processing_time_log
    pre_processing_time_log = result_data_analyzing['pre_processing_time_log'] + '\t\t\t{0} ms'.format(
        (end_time - start_time).total_seconds() * 1000)  # update generate_word2vec time
    result = {'code': GeneralConstant.RESULT_TRUE(), 'pre_processing_time_log': pre_processing_time_log}
    return result


##
# MAIN
##

# 2018-04-24: Dac: writing to time_log_pre_processing
pre_processing_time_log = generate_word_2_vec()['pre_processing_time_log']
# load keyword from file and integrate with category and date
# pre_processing_time_log += WordProcessing.run()['pre_processing_time_log']

f = open(GeneralConstant.TIME_PROCESSING_LOG_PATH(), "a+")
f.write('\n' + pre_processing_time_log)
f.close()
