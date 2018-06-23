import datetime

from gensim.models import Word2Vec

import application.Library.Constant.GeneralConstant as GeneralConstant
import application.Repository.GeneralRepository as GeneralRepository

"""
FUNCTION
"""


def find_similar_keywords(current_category, current_keyword):
    """
    find_similar_keywords
    :param current_category:
    :param current_keyword:
    :return:
    """
    result = {'code': GeneralConstant.RESULT_FALSE(), 'data': None}
    try:
        category_nodes = GeneralRepository.category_nodes  # list category nodes
        model = Word2Vec.load(category_nodes[current_category]['model'])
        words = model.wv.similar_by_word(current_keyword, topn=10)  # find similar word
        # for word in words:
        #     print("({0}, {1}) ".format(word[0], str(word[1])))

        result = {'code': GeneralConstant.RESULT_TRUE(), 'data': words}
    except Exception as e:
        print('[find_similar_keywords] Failed with error: {0}'.format(e.args[0]))
    return result


def find_similar_keywords_by_dates(from_date, to_date):
    print('Finding Similar Keywords from date {0} to date {1}'.format(from_date, to_date))
    result = {'code': GeneralConstant.RESULT_FALSE(), 'data': None}
    query_results = GeneralRepository.get_date_category_paper_keyword_by_date(from_date, to_date)

    papers_of_date = {}
    papers_num = {}
    keywords_num = {}
    processing_time = {}
    dates = []
    if query_results['code'] == GeneralConstant.RESULT_TRUE():
        start_time = 0
        current_date = '0'
        for row in query_results['data']:
            # append date
            if row[0] not in papers_of_date.keys():
                if current_date != '0':
                    # update processing time
                    end_time = datetime.datetime.now()
                    processing_time[current_date] = (end_time - start_time).total_seconds() * 1000
                # update new date
                current_date = row[0]
                print('\tProcessing date: {0}'.format(current_date))
                start_time = datetime.datetime.now()
                papers_of_date[current_date] = []
                dates.append(current_date)
                papers_num[current_date] = 0
                keywords_num[current_date] = 0
                processing_time[current_date] = 0

            if row[2] not in papers_of_date[row[0]]:
                papers_num[current_date] += 1  # count papers
                papers_of_date[current_date].append(row[2])

            keywords_num[current_date] += 1  # count keywords
            current_category = row[1]
            current_keyword = row[3]
            similar_keywords = find_similar_keywords(current_category, current_keyword)
        # 2018-06-22: Dac: Add the last day
        if current_date != '0':
            # update processing time
            end_time = datetime.datetime.now()
            processing_time[current_date] = (end_time - start_time).total_seconds() * 1000

    finding_similar_word_log = ''
    for date in dates:
        finding_similar_word_log += '{0}\t\t\t{1}\t\t\t{2}\t\t\t{3} ms\n' \
            .format(date, papers_num[date], keywords_num[date], processing_time[date])

    f = open(GeneralConstant.FINDING_SIMILAR_WORD_LOG_PATH(), "a")
    f.write('\n' + finding_similar_word_log)
    f.close()
    print('Write to log file successfully!')
    result = {'code': GeneralConstant.RESULT_TRUE()}
    return result
