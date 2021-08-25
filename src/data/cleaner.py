from numpy.lib.function_base import select
from ..utils import logger
from sklearn.impute import KNNImputer, SimpleImputer
from pandas import DataFrame


class Cleaner:
    """
    To clean the give dataset,it performs imputation,empty columns removal
    and removal of columns with zero std.

    Params:
    filepath (str): Path of the csv file to be cleaned.
    """

    def __init__(self, df: DataFrame, exclude_cols=[]):
        self.logger = logger.Logger(__name__)

        self.exclude_cols = exclude_cols

        self.df = df

    def clean(self):
        """
        Starts cleaning the data.
        """
        self.logger.info(
            'Started cleaning process for dataset.')

        self._remove_empty_columns()
        self._impute()
        self._remove_columns_with_zero_std()
        self.logger.info(
            'Finished cleaning process for dataset.')

    def _impute(self):
        """
        for numerical columns use KNN to impute the value
        and for categorical feature use mode value
        """
        self.logger.info(
            f'Started imputation process using KNN algoritm for dataset.')
        num_cols = self._get_num_features()
        cat_cols = self._get_cat_features()

        knn_imputer = KNNImputer(n_neighbors=5, weights="uniform")
        self.df[num_cols] = knn_imputer.fit_transform(self.df[num_cols])

        simple_imputer = SimpleImputer(strategy='most_frequent')
        self.df[cat_cols] = simple_imputer.fit_transform(self.df[cat_cols])

        self.logger.info(f'Finished imputation process for dataset.')

    def _remove_empty_columns(self):
        empty_cols = []

        for column in self.df.columns:
            col_series = self.df[column]

            if len(col_series) == 0:
                empty_cols.append(column)

        self.df.drop(columns=empty_cols, inplace=True)
        self.logger.info(
            f'Removed {len(empty_cols)} empty columns from dataset.')

    def _remove_columns_with_zero_std(self):
        empty_cols = []

        for column in self.df.select_dtypes(exclude=['object', 'datetime']).columns.to_list():
            if self.df[column].std() == 0:
                empty_cols.append(column)

        self.df.drop(columns=empty_cols, inplace=True)
        self.logger.info(
            f'Removed {len(empty_cols)} columns with 0 std from dataset.')

    def _get_num_features(self):
        """
        Get the numerical features in the dataset

        Return:
        columns (list): List of columns of numerical data type.
        """
        return list(self.df.select_dtypes(exclude=['object']).columns)

    def _get_cat_features(self):
        """
        Get the categorical features in the dataset

        Return:
        columns (list): List of columns of categorical data type.
        """
        return list(self.df.select_dtypes(exclude=['int', 'float']).columns)

    def save(self, output_path):
        self.logger.info(f'Saved cleaned dataset to {output_path}')
        self.df.to_csv(output_path)