import glob
import math
import os
import time

from sklearn.feature_extraction.text import TfidfVectorizer


def cosine_similarity(vector1, vector2):
    dot_product = sum(p * q for p, q in zip(vector1, vector2))
    magnitude = math.sqrt(sum([val ** 2 for val in vector1])) * math.sqrt(sum([val ** 2 for val in vector2]))
    if not magnitude:
        return 0
    return dot_product / magnitude


def generate_paper_keyword(num):
    print('Generating paper keywords')
    folder_dates_path = 'E:\Developing\PycharmProjects/vn-topic-clustering\Data20180321-20180421\PreprocessingData'
    # csv_writer = csv.writer(
    #     open('E:/Developing/PycharmProjects/vn-topic-clustering/trial/preprocessing_data/papers_keywords.csv', 'w',
    #          encoding='UTF-8'))
    writer = open(
        'E:\Developing\PycharmProjects/vn-topic-clustering\Data20180321-20180421/papers_keywords_'
        '{0}.txt'.format(num), 'w', encoding='UTF-8')
    data = []
    for folder_current_date in glob.glob(folder_dates_path + '/*'):
        current_date = os.path.basename(folder_current_date)
        print('Processing at date: {0}'.format(current_date))
        for folder_category in glob.glob(folder_current_date + '/*'):
            current_category = os.path.basename(folder_category)

            # tfidf_results = tfidf.analyze(glob.glob(folder_category + '/*'), resultsPerDocument=num, ranking=True,
            #                               preferNouns=True, files=True)

            # 2018-05-07: Dac scikit learn
            all_documents = []
            for document in glob.glob(folder_category + '/*'):
                document_data = ''
                for line in open(document, "r", encoding='UTF-8').readlines():
                    document_data += line + ' '
                all_documents.append(document_data)

            sklearn_tfidf = TfidfVectorizer(norm='l2', min_df=0, use_idf=True, smooth_idf=False, sublinear_tf=True,
                                            tokenizer=lambda doc: doc.lower().split(" "))
            sklearn_representation = sklearn_tfidf.fit_transform(all_documents)
            skl_tfidf_comparisons = []
            for count_0, doc_0 in enumerate(sklearn_representation.toarray()):
                for count_1, doc_1 in enumerate(sklearn_representation.toarray()):
                    skl_tfidf_comparisons.append((cosine_similarity(doc_0, doc_1), count_0, count_1))
            print('')
            # for paper in tfidf_results:
            #     current_paper = paper['paper_id']
            #
            #     for keyword in paper['keywords']:
            #         row = [current_date, current_category, current_paper.replace('.txt', '')] + keyword
            #         data.append(row)

    # Write to CSV
    # csv_writer.writerows(data)
    for row in data:
        for element in row:
            writer.write(element + '\n')
    print('Generating completed')


start = time.time()
generate_paper_keyword(10)
end = time.time()
print(end - start)
