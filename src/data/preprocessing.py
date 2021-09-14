from pathlib import Path
import pandas as pd
import numpy as np
from src.utils.logger import Logger


class Preprocessor:
    data_file = Path('data/raw/data.csv')

    cleaned_file = Path('data/processed/data.csv')

    def __init__(self):
        self.logger = Logger(__name__, __name__ == '__main__')

        if not self.data_file.exists():
            err = f"File does not exist {self.data_file}"
            self.logger.info(err)

            raise FileNotFoundError(err)

    def load_data(self):
        self.df = pd.read_csv(str(self.data_file))
        return self.df

    def start(self):
        self.load_data()
        self.logger.info('Starting cleaning process.')
        self._strip_features()
        self._clean_kms_driven()
        self._clean_price()
        self._clean_owner()
        self._clean_mileage()
        self._clean_power()

        self._fix_col_type()
        self._drop_empty_cols()
        self._remove_duplicates()

        self.logger.info(f'Saving cleaned file at {self.cleaned_file}')

        self.df.to_csv(str(self.cleaned_file))

    def _strip_features(self):
        # if not self.df:
        #     return

        for col in self.df.select_dtypes(include='object').columns:
            self.df[col] = self.df[col].str.strip()

        self.logger.info('Stripping whitespaces from objects columns.')

    def _clean_kms_driven(self):
        def clean_kms_driven(val):
            if not val:
                return ''

            val = val.lower()

            if 'kms' in val:
                val = val.replace('kms', '')

            if 'km' in val:
                val = val.replace('km', '')

            if 'mileage' in val.lower():
                return np.nan

            return val.replace(',', '')

        self.df['kms_driven'] = self.df.kms_driven.apply(clean_kms_driven)
        self.logger.info('Cleaned `kms_driven` column.')

    def _clean_price(self):
        def clean_price(val):
            """
            1. removes currency symbol.
            2. removes commas
            3. fix the val which is represented as lakh
            """
            if not val:
                return ''

            val = str(val)

            val = val.replace(',', '')

            return val

        self.df['price'] = self.df['price'].apply(clean_price)
        self.logger.info('Cleaned `price` column.')

    def _clean_owner(self):
        """Removes 'owner' word form the data as it holds not value"""
        def clean_owner(val):
            if not val:
                return val

            val = val.replace('owner', '')

            if 'or more' in val.lower():
                return 'fourth'

            return val

        self.df['owner'] = self.df['owner'].apply(clean_owner)
        self.logger.info('Cleaned `owner` column.')

    def _clean_mileage(self):
        def clean_mileage(val):
            if not val:
                return np.nan

            return str(val).lower().replace('kmpl', '')

        self.df['mileage'] = self.df.mileage.apply(clean_mileage)
        self.logger.info('Cleaned `mileage` column.')

    def _clean_power(self):
        """Removes bhp word form the column."""
        def clean_power(val):
            if not val:
                return np.nan

            return str(val).lower().replace('bhp', '')

        self.df['power'] = self.df.power.apply(clean_power)
        self.logger.info('Cleaned `power` column.')

    def _fix_col_type(self):
        """Fix the columns types"""
        cols = ['kms_driven', 'price']
        
        for col in cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce', downcast='integer')
        
        self.logger.info(f'Fixing dtype of columns {cols}.')

    def _drop_empty_cols(self):
        self.df.dropna(how='all', axis=1, inplace=True)
        self.logger.info('Dropping empty columns.')

    def _remove_duplicates(self):
        dups_count = self.df.duplicated().sum()
        self.logger.info(f'Found {dups_count} records.')
        self.df = self.df[~self.df.duplicated()]
        self.logger.info('Removed all the duplicates records.')


if __name__ == '__main__':
    Preprocessor().start()
    
