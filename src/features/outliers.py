from pathlib import Path
import pandas as pd
from pandas.core.frame import DataFrame
from ..utils.logger import Logger


class Outliers:

    def __init__(self,df: DataFrame):
        self.logger = Logger(__name__, __name__ == '__main__')
        self.df = df
    

    def detect(self):
        self.logger.info(f"Started outlier detection.")
        self.logger.info(f"Dataset shape before outlier removal : {self.df.shape}")
        num_cols = ['kms_driven','price']

        for col in num_cols:

            max_val = self.df[col].quantile(.99)

            min_val = self.df[col].quantile(.1)

            self.logger.info(f"Min/Max Range for {col} is {min_val} / {max_val}")

            total_outs = self.df[~(self.df[col] <= max_val)].shape[0]

            self.logger.info(f"Total outliers detected for {col} is {total_outs}")

            self.df = self.df[(self.df[col] <= max_val)]

            self.logger.info(f"Outliers removed for {col}.")

        self.logger.info(f"Dataset shape after outlier removal : {self.df.shape}")

        self.logger.info(f"Finished outlier detection.")

        return self.df


    def _get_num_features(self):
        return self.df.select_dtypes(exclude='object').columns


if __name__ == '__main__':
    Outliers('data/processed/data.csv').detect()


