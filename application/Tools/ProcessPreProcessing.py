import os

from application.Service.DataPreProcessingService import run_training_model, \
    run_data_pre_processing_exclude_training_model
from application.Tools.ChangeFolderFileName import run_changing_folder_name_process
from application.Service.KeywordService import find_similar_keywords_by_dates

""" MAIN """


def run_pre_processing(action):
    if action == '1' or action == '3':
        run_changing_folder_name_process()
        # 2018-04-24: Dac: pre-processing without training model
        result_data_preprocessing = run_data_pre_processing_exclude_training_model()
        # 2018-06-20: Dac: training model
        if action == '3':
            last_processed_date = result_data_preprocessing['last_processed_date']
            result_training_model = run_training_model(last_processed_date)
    elif action == '2':
        # 2018-06-20: Dac: training model
        date = input('Please input the last date you want to train (EX: 20180620): ')
        result_training_model = run_training_model(date)['training_model_time_log']  # manual run && update model
    print('Done!')
    os.system("cls")


# 2018-06-22: Dac: find similar keyword
def run_find_similar_keywords_by_dates():
    from_date = input('Please input from_date & to_date (EX: 20180620)\n'
                      'from_date: ')
    to_date = input('to_date: ')
    find_similar_keywords_by_dates(from_date, to_date)
    print('Done!')
    os.system("cls")


stop_loop = 0
while not stop_loop:
    os.system("cls")

    action = input('\n>>>> Vietnamese Text Mining project!<<<<\n'
                   '\n'
                   '[1]. Automatic Pre-processing\n'
                   '[2]. Testing Tools\n'
                   '[3]. Exit!\n\n'
                   'Please type a number: ')
    os.system("cls")
    if action == '1':
        action = input('Automatic Pre-processing process\n'
                       '[1]. Run pre-processing only\n'
                       '[2]. Run training model only\n'
                       '[3]. Run both pre-processing & training model processes (up to date)\n'
                       '[4]. Back\n'
                       'Please type a number: ')
        os.system("cls")
        if action != '4':
            run_pre_processing(action)
    elif action == '2':
        action = input('Testing tools process\n'
                       '[1]. Find similar keywords\n'
                       '[2]. Back\n'
                       'Please type a number: ')
        os.system("cls")
        if action == '1':
            run_find_similar_keywords_by_dates()

    elif action == '3':
        stop_loop = 1
print('\nThank you!')
