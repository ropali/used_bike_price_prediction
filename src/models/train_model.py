import pandas as pd
import numpy as np
from pathlib import Path
from ..data.preprocessing import Preprocessor
from ..features.build_features import FeatureBuilder
from ..utils.logger import Logger
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from .metrics import Metrics
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression


class Model:
    def __init__(self, df: DataFrame, cross_validate = False):
        self.logger = Logger(__name__, __name__ == '__main__')
        self.df = df
        self.cross_validate = cross_validate

        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            self.X, self.y, test_size=.25, random_state=123)

        self.metrics = Metrics()

        self.estimator = None

    @property
    def X(self):
        return self.df.drop('price', axis=1)

    @property
    def y(self):
        return self.df['price']

    @property
    def X_train(self):
        return self._X_train
    
    @property
    def X_test(self):
        return self._X_test

    @property
    def y_train(self):
        return self._y_train

    @y_train.setter
    def y_train(self,val):
        self._y_train = val

    @property
    def y_test(self):
        return self._y_test

    @y_test.setter
    def y_test(self,val):
        self._y_test = val

    def impute(self):

        self.y_train = self.y_train.fillna(self.y_train.mean())
        self.y_test = self.y_test.fillna(self.y_test.mean())

        num_cols = [
            col for col in self.X.columns if self.X[col].dtypes != 'object']

        X_imputer = KNNImputer(n_neighbors=7, weights='distance')

        X_imputer.fit(self.X_train[num_cols])

        self.X_train.loc[:][num_cols] = X_imputer.fit_transform(
            self.X_train[num_cols])
        self.X_test.loc[:][num_cols] = X_imputer.transform(
            self.X_test[num_cols])

        y_imputer = KNNImputer(n_neighbors=7, weights='distance')
        y_imputer.fit([self.y_train])

    def train(self):

        # first impute missing values
        self.impute()

        pipe = self._build_pipeline(self.estimator)

        pipe.fit(self.X_train, self.y_train)

        train_metrics_df = self.metrics.model_perf(
            pipe, self.X_train, self.y_train, self.cross_validate)

        test_metrics_df = self.metrics.model_perf(
            pipe, self.X_test, self.y_test, self.cross_validate)

        return train_metrics_df, test_metrics_df

    def _build_pipeline(self, estimator):
        if not estimator:
            raise Exception(f'Invalid estimator value {estimator}')

        return Pipeline([
            ('category_transformer', self._col_transformer()),
            ('estimator', estimator),
        ])

    def _col_transformer(self):
        return ColumnTransformer([
            ("kms_driven_engine_min_max_scaler", MinMaxScaler(), [0, 6, 3, 4]),
            ("owner_ordinal_enc", OrdinalEncoder(categories=[
             ['fourth', 'third', 'second', 'first']], handle_unknown='ignore', dtype=np.int16), [1]),
            ("brand_location_ohe", OneHotEncoder(
                sparse=False, handle_unknown='error', drop='first',), [2, 5]),
        ], remainder='passthrough')


class _LinearRegressionModel(Model):
    def __init__(self, df: DataFrame):
        super().__init__(df)

        self.estimator = LinearRegression()

    # @property
    # def y_train(self):
    #     return np.log1p(self._y_train)

    


class ModelFactory:
    models = {
        'lr': _LinearRegressionModel
    }

    def get_model(self, model_name):
        model = self.models.get(model_name, None)

        if not model:
            raise ValueError(f"{model_name}: This model does not exist!")

        return model


def main():
    preprocessor = Preprocessor()

    df = preprocessor.start(True)

    feat_builder = FeatureBuilder()

    df = feat_builder.build()

    model_cls = ModelFactory().get_model('lr')

    model = model_cls(df)

    train_result, test_result = model.train()

    print('Train Result\n')
    print(train_result)
    print('\n')
    print('Test Result\n')
    print(test_result)


if __name__ == '__main__':
    main()
