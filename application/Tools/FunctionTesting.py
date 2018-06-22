from application.Service.DataPreProcessingService import run_training_model, \
    run_data_pre_processing_exclude_training_model
from application.Service.KeywordService import find_similar_keywords_by_dates

""" MAIN """

# 2018-04-24: Dac: preprocessing without training model
# result_data_preprocessing = run_data_pre_processing_exclude_training_model()

# 2018-06-20: Dac: training model
# last_processed_date = result_data_preprocessing['last_processed_date']
# result_training_model = run_training_model(last_processed_date)  # automatic run & update model after pre-processing
# result_training_model = run_training_model('20180430')['training_model_time_log']  # manual run && update model


# 2018-06-22: Dac: find similar keyword
find_similar_keywords_by_dates('20180321', '20180325')
