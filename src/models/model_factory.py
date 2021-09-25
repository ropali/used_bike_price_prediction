from pandas import DataFrame
import pandas as pd
from ..utils.logger import Logger
import numpy as np
from sklearn.model_selection import train_test_split
from .metrics import Metrics
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
import pickle


class Model:
    hyper_params = {}

    def __init__(self, df: DataFrame, cross_validate=True):
        self.logger = Logger(__name__, __name__ == '__main__')
        self.df = df
        self.cross_validate = cross_validate

        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            self.X, self.y, test_size=.25, random_state=42)

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
    def y_train(self, val):
        self._y_train = val

    @property
    def y_test(self):
        return self._y_test

    @y_test.setter
    def y_test(self, val):
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

        y_imputer = KNNImputer(n_neighbors=3, weights='uniform')
        y_imputer.fit([self.y_train])

    def train(self):

        # first impute missing values
        self.impute()

        self.pipe = self._build_pipeline()

        self.pipe.fit(self.X_train, self.y_train)

        train_metrics_df = self.metrics.model_perf(
            self.pipe, self.X_train, self.y_train, self.cross_validate)

        test_metrics_df = self.metrics.model_perf(
            self.pipe, self.X_test, self.y_test, self.cross_validate)

        return train_metrics_df, test_metrics_df

    def hyper_tuning(self):
        _pipe_hyper_params = {}

        if self.hyper_params:
            for k, v in self.hyper_params.items():
                _pipe_hyper_params[f'estimator__{k}'] = v
        else:
            self.logger.info(f'Hyper paramerts not found for {self.estimator}')

        if _pipe_hyper_params:
            self.logger.info(
                'Performing randomized search cv for best model....')

            self.impute()

            self.pipe = self._build_pipeline()

            model = RandomizedSearchCV(self.pipe, _pipe_hyper_params, cv=5)

            model.fit(self.X_train, self.y_train)

            result_train = self.metrics.model_perf(
                model, self.X_train, self.y_train)

            result_train['type'] = 'Train'

            result_test = self.metrics.model_perf(
                model, self.X_test, self.y_test)

            result_test['type'] = 'Test'

            return pd.concat([result_train, result_test], axis=0)

    def _build_pipeline(self):
        return Pipeline([
            ('category_transformer', self._col_transformer()),
            ('estimator', self.estimator),
        ])

    def _col_transformer(self):
        return ColumnTransformer([
            ("kms_driven_engine_min_max_scaler", MinMaxScaler(), [0, 6, 3, 4]),
            ("owner_ordinal_enc", OrdinalEncoder(categories=[
             ['fourth', 'third', 'second', 'first']], handle_unknown='ignore', dtype=np.int16), [1]),
            ("brand_location_ohe", OneHotEncoder(
                sparse=False, handle_unknown='error', drop='first',), [2, 5]),
        ], remainder='passthrough')

    def save(self, filepath: str):
        if not self.pipe:
            raise Exception(
                'Model is not trained. Start model trainign first.')

        pickle.dump(self.pipe, open(filepath, 'wb'))

        self.logger.info(f'Model file saved at {filepath}')


class _LinearRegressionModel(Model):
    def __init__(self, df: DataFrame):
        super().__init__(df)

        self.y_train = self.y_train.fillna(self.y_train.mean())
        self.y_test = self.y_test.fillna(self.y_test.mean())

        self._y_train = np.log1p(self._y_train)
        self._y_test = np.log1p(self._y_test)

        self.estimator = LinearRegression()


class _RandomForestModel(Model):

    hyper_params = {
        'criterion': ['mse', 'mae'],
        'n_estimators': [100, 110, 120, 130, 140, 150, 160, 200],
        'max_depth': [5, 10, 15, 20, 25, 30, 35, 40],
        'min_samples_split': range(2, 30),
        'max_features': ['auto', 'sqrt', 'log2'],
    }

    def __init__(self, df: DataFrame):
        super().__init__(df)

        self.estimator = RandomForestRegressor(n_estimators=150)


class _KNNModel(Model):

    hyper_params = {
        'n_neighbors': [5, 7, 9, 11, 13],
        'weights': ['uniform', 'distance'],
        'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
        'leaf_size': range(30, 50)
    }

    def __init__(self, df: DataFrame, cross_validate=True):
        super().__init__(df, cross_validate=cross_validate)

        self.estimator = KNeighborsRegressor(n_neighbors=3)


class _GradienBoostModel(Model):

    hyper_params = {
        'loss': ['squared_error', 'ls', 'absolute_error', 'lad', 'huber', 'quantile'],
        'learning_rate': [.1, .01, .001, .0001],
        'n_estimators': [100, 110, 120, 130, 140, 150],
        'criterion': ['friedman_mse', 'squared_error', 'mse', 'mae'],
        'min_samples_split': [2, 3, 4, 5, 6, 7, 8, 9, 10],
        'max_depth': [3, 4, 5, 6, 7, 8, 9, 10]
    }

    def __init__(self, df: DataFrame, cross_validate=True):
        super().__init__(df, cross_validate=cross_validate)

        self.estimator = GradientBoostingRegressor()


class ModelFactory:
    models = {
        'linear_regression': _LinearRegressionModel,
        'random_forest': _RandomForestModel,
        'knn': _KNNModel,
        'gradient_boost': _GradienBoostModel
    }

    def get_model(self, model_name):
        model = self.models.get(model_name, None)

        if not model:
            raise ValueError(f"{model_name}: This model does not exist!")

        return model
