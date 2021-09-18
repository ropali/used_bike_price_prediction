import pandas as pd
import numpy as np
from pathlib import Path
from ..data.preprocessing import Preprocessor
from ..features.build_features import FeatureBuilder
from ..utils.logger import Logger
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression


class Metrics:

    def mape(self, targets, predictions):
        return np.mean(np.abs((targets - predictions)) / targets) * 100

    def adj_r2(self, ind_vars, targets, predictions):
        r2 = r2_score(targets, predictions)
        n = ind_vars.shape[0]
        k = ind_vars.shape[1]
        return 1-((1-r2)*(n-1)/(n-k-1))

    # Model performance check
    def model_perf(self, model, inp, out, cross_val=True):

        y_pred = model.predict(inp)
        y_act = out.values

        cross_val_ = cross_val_score(
            model, inp, out, cv=10).mean() if cross_val else None

        return pd.DataFrame({
            "RMSE": np.sqrt(mean_squared_error(y_act, y_pred)),
            "MAE": mean_absolute_error(y_act, y_pred),
            "MAPE": self.mape(y_act, y_pred),
            "R^2": r2_score(y_act, y_pred),
            "Adjusted R^2": self.adj_r2(inp, y_act, y_pred),
            "Cross Val Score (Mean)": cross_val_ if cross_val else None
        }, index=[0])


class BaseModel:
    def __init__(self, df: DataFrame):
        self.logger = Logger(__name__, __name__ == '__main__', 'train.log')
        self.df = df
        self.X = self.df.drop('price', axis=1)
        self.y = self.df['price']

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=.25, random_state=11)

        self.metrics = Metrics()

    def get_model(self):
        raise NotImplemented(
            f'This method is not implemented for {self.__class__.__name__}')

    def train(self):
        model = self.get_model()

        pipe = self.build_pipeline(model)

        pipe.fit(self.X_train, self.y_train)

        train_metrics_df = self.metrics.model_perf(pipe, self.X_train,self.y_train)
        test_metrics_df = self.metrics.model_perf(pipe, self.X_test,self.y_test)

        return train_metrics_df, test_metrics_df

    def build_pipeline(self, estimator):
        return Pipeline([
            ('category_transformer', self.col_transformer()),
            ('estimator', estimator),
        ])

    def col_transformer(self):
        return ColumnTransformer([
            ("kms_driven_engine_min_max_scaler", MinMaxScaler(), [0, 6, 3, 4]),
            ("owner_ordinal_enc", OrdinalEncoder(categories=[
             ['fourth', 'third', 'second', 'first']], handle_unknown='ignore', dtype=np.int16), [1]),
            ("brand_location_ohe", OneHotEncoder(
                sparse=False, handle_unknown='error', drop='first',), [2, 5]),
        ], remainder='passthrough')


class _LinearRegressionModel(BaseModel):
    def __init__(self, df: DataFrame):
        super().__init__(df)

        # scaling the target feature
        self.y_train = np.log1p(self.y_train)
        self.y_test = np.log1p(self.y_train)

    def get_model(self):
        return LinearRegression()


class ModelFactory:
    models = {
        'LinearRegression': _LinearRegressionModel
    }

    def get_model(self,model_name):
        model = self.models.get(model_name,None)

        if not model:
            raise ValueError(f"{model_name}: This model does not exist!")

        return model



def main():
    pass


if __name__ == '__main__':
    preprocessor = Preprocessor()

    df = preprocessor.start(True)

    feat_builder = FeatureBuilder()

    df = feat_builder.build()

    model_cls = ModelFactory().get_model('LinearRegression')

    model = model_cls(df)

    train_result,test_result = model.train()

    print(train_result)
    print('\n')
    print(test_result)


