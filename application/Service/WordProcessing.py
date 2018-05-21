import datetime

from gensim.models import Word2Vec

import application.Repository.GeneralRepository as GeneralRepository

"""
FUNCTION
"""


# Load keyword from file to python
def load_keyword_from_file(path):
    keyword = []

    keyword_file = open(path, "r", encoding='UTF-16', errors='ignore')
    position = 0
    if keyword_file.mode == 'r':
        lines = keyword_file.readlines()
        elem = []  # each element

        # Loop line by line
        for line in lines:

            # Reset elem
            if position == 4:
                keyword.append(elem)  # add elem to keyword
                position = 0
                elem = []

            elem.append(line.replace('\n', ""))
            position += 1
    return keyword


"""
MAIN
"""


def run():
    result = {}
    result['code'] = False
    # 2018-04-24: Dac: writing to time_log_pre_processing
    keyword_num = 0
    similar_words_num = 0
    start_time = datetime.datetime.now()

    print('Processing keywords')
    # load list keyword and related data from file
    keyword_content = load_keyword_from_file("Library/keyword/KeyWordList.txt")
    current_category = ""

    # writing last processed date to file
    # result_file = open("Library/result/related_keyword.txt", "w+", encoding='utf-8')

    # Get list category in database
    category_nodes = GeneralRepository.category_nodes  # list category nodes

    # Word model
    model = Word2Vec()

    # Loop all keyword
    for keyword in keyword_content:
        # 2018-04-24: Dac: update number of keywords
        keyword_num += 1

        current_keyword = keyword[1]  # .replace("_", "")# get keyword
        current_date = keyword[3]

        if current_category != keyword[0]:  # update category
            current_category = keyword[0]
            model = Word2Vec.load(category_nodes[current_category]['model'])

        # Get keyword from Neo4j
        current_keyword_node = GeneralRepository.create_keyword_node(current_keyword, category_nodes[current_category],
                                                                     current_date)
        # word2vec processing
        try:
            words = model.wv.similar_by_word(current_keyword, topn=20)  # find similar word

            for word in words:
                print("({0}, {1}) ".format(word[0], str(word[1])))
                # data_to_write += "({0}, {1}) ".format(word[0], str(word[1]))
            similar_words_num += len(words)
            # Write to file
            # result_file.write("Keyword: {0}\nResults:\n{1}\n".format(current_keyword, data_to_write))
        except Exception as e:
            print("[Word Processing] Failed Word2Vec at words: {0}\t\t\tWith error: {1}".format(current_keyword,
                                                                                                e.args[0]))
            # data_to_write = "[Word Processing] Failed Word2Vec at words: " + current_keyword
    # 2018-04-24: Dac: writing to time_log_pre_processing
    end_time = datetime.datetime.now()
    pre_processing_time_log = '\t\t\t{0}\t\t\t{1}\t\t\t{2} ms'.format(keyword_num, similar_words_num, (
            end_time - start_time).total_seconds() * 1000)  # update similar word time log

    print('Processing keyword successfully')

    result['code'] = True
    result['pre_processing_time_log'] = pre_processing_time_log
    return result
