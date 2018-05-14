# 2018-05-04: Dac: create new function to read data from file
def get_data_from_file(lines):
    """
    Get keyword from text file
    :param lines:
    :return: result{date:{category:{paper:{keyword:[],}}}}
    """
    # Processing file 1
    position = 0
    result = {}
    current_date = ''
    current_category = ''
    current_paper = ''
    while position < len(lines) - 5:
        if current_date != lines[position]:
            current_date = lines[position]
            current_category = lines[position + 1]
            current_paper = lines[position + 2]

            result[current_date] = {}  # date
            result[current_date][current_category] = {}  # category
            result[current_date][current_category][current_paper] = {'keywords': [], 'keyword-weight': []}  # paper
        elif current_category != lines[position + 1]:
            current_category = lines[position + 1]
            current_paper = lines[position + 2]

            result[current_date][current_category] = {}  # category
            result[current_date][current_category][current_paper] = {'keywords': [], 'keyword-weight': []}  # paper
        elif current_paper != lines[position + 2]:
            current_paper = lines[position + 2]

            result[current_date][current_category][current_paper] = {'keywords': [], 'keyword-weight': []}  # paper
        result[current_date][current_category][current_paper]['keywords'].append(lines[position + 3])
        # 2018-05-04: Data to write keyword and weight to file
        result[current_date][current_category][current_paper]['keyword-weight'].append(
            '{0}: {1}'.format(lines[position + 3], lines[position + 4]))
        position += 5
    return result


def check_accurate(file_1, file_2, result_path):
    """
    Measure accurate by checing similarity between file 1 and file 2
    :param file_1:
    :param file_2:
    :param result_path:
    """
    print('Checking accurate of two files: {0} and {1}'.format(file_1, file_2))
    writer = open(result_path, 'w', encoding='UTF-8')

    reader_1 = open(file_1, 'r', encoding='UTF-8')
    lines_1 = reader_1.readlines()

    reader_2 = open(file_2, 'r', encoding='UTF-8')
    lines_2 = reader_2.readlines()

    # Processing file 1 & file 2
    result_1 = get_data_from_file(lines_1)
    result_2 = get_data_from_file(lines_2)

    # 2018-05-03: Dac: Check number of keyword
    # 2018-05-04: Dac: print out papers that don't contain 10 words
    # print('Paper 1:')
    # for date in result_1:  # loop date
    #     writer.write('{0}'.format(date))
    #     for category in result_1[date]:  # loop category
    #         writer.write('\t{0}'.format(category))
    #         for paper in result_1[date][category]:  # loop paper
    #             result_1[date][category][paper]['similarity'] = 0
    #
    #             if len(result_1[date][category][paper]['keywords']) < 10:  # Loop keyword
    #                 print('{0} {1} {2} {3}'.format(date.replace('\n', ''), category, paper,
    #                                                len(result_1[date][category][paper]['keywords'])))
    # print('Paper 2:')
    # for date in result_2:  # loop date
    #     writer.write('{0}'.format(date))
    #     for category in result_2[date]:  # loop category
    #         writer.write('\t{0}'.format(category))
    #         for paper in result_2[date][category]:  # loop paper
    #             result_2[date][category][paper]['similarity'] = 0
    #
    #             if len(result_2[date][category][paper]['keywords']) < 10:  # Loop keyword
    #                 print('{0} {1} {2} {3}'.format(date.replace('\n', ''), category, paper,
    #                                                len(result_2[date][category][paper]['keywords'])))

    sum = 0
    count = 0
    for date in result_1:  # loop date
        writer.write('{0}'.format(date))
        for category in result_1[date]:  # loop category
            writer.write('\t{0}'.format(category))
            for paper in result_1[date][category]:  # loop paper
                result_1[date][category][paper]['similarity'] = 0

                for keyword in result_1[date][category][paper]['keywords']:  # Loop keyword
                    try:
                        if keyword in result_2[date][category][paper]['keywords']:  # found same keyword
                            result_1[date][category][paper]['similarity'] += 1
                        # else:
                        # print(keyword)
                    except Exception as ex:
                        print(ex.args[0])

                # calculate the same ratio of two paper
                result_1[date][category][paper]['ratio'] = 100 * result_1[date][category][paper]['similarity'] / len(
                    result_1[date][category][paper]['keywords'])
                # write result to file
                writer.write(
                    '\t\t{0}: {1}%\t\t{2}\t-\t{3}\n'.format(paper.replace('\n', ''),
                                                            result_1[date][category][paper]['ratio'],
                                                            result_1[date][category][paper]['keyword-weight'],
                                                            result_2[date][category][paper]['keyword-weight']))
                sum += result_1[date][category][paper]['ratio']
                count += 1
    writer.write('\t\t\tFinal Ratio: {0}%\n'.format(sum / count))
    print('Total processed papers: {0}'.format(count))
    print('Checking accurate completed!')


check_accurate(
    'E:\Developing\PycharmProjects/vn-topic-clustering\Data20180321-20180421\PreprocessingData/papers_keywords_10_1.txt',
    'E:\Developing\PycharmProjects/vn-topic-clustering\Data20180321-20180421\PreprocessingData/abc.txt',
    'E:/Developing/PycharmProjects/vn-topic-clustering/Data20180321-20180421/accurate_measuring_result.txt')
