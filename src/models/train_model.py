import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ..data.preprocessing import Preprocessor
from ..features.build_features import FeatureBuilder
from ..utils.logger import Logger
from ..features.outliers import Outliers
from .model_factory import ModelFactory

def find_best_result(df:pd.DataFrame):
    test_results = df[df['type'] == 'Test']

    idmax = test_results['Adjusted R^2'].values.argmax()

    return test_results.iloc[idmax]


def main():
    logger = Logger(__name__, __name__ == '__main__')

    preprocessor = Preprocessor()

    df = preprocessor.start(True)

    feat_builder = FeatureBuilder()

    df = feat_builder.build()

    df = Outliers(df).detect()

    print('Training Data Points', df.shape)

    best_model = None

    results = []

    for name, model in ModelFactory.models.items():

        logger.info(f'Training Model :: {name}')
        train_result, test_result = model(df).train()

        train_result['type'] = 'Train'
        train_result['model'] = name

        test_result['type'] = 'Test'
        test_result['model'] = name

        results.append(train_result)
        results.append(test_result)

    result_df = pd.concat(results, axis=0, ignore_index=True)

    print(result_df)

    

    best_result = find_best_result(result_df)

    logger.info(f'Best model is {best_result.model}({best_result.type}) with score {best_result["Adjusted R^2"]}',)

    best_model = ModelFactory().get_model(best_result.model)

    user_inp = input(
        'Do you want to perform hyper parameter tuning of the best model?[Y/n](default=n)')

    if user_inp and user_inp.lower() == 'y' and best_model:
        logger.info(f'Started hyper parameter tuning of {best_result.model}')

        mdl = best_model(df)
        
        logger.info(f"Using hyper parameters : {mdl.hyper_params}",)

        result = mdl.hyper_tuning()

        best_result = find_best_result(result)

        logger.info(f'Best score after hyper parameter tuning is {best_result["Adjusted R^2"]}')


if __name__ == '__main__':
    main()
