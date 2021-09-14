
from pathlib import Path
import pandas as pd
from utils.logger import Logger
import re


class FeatureBuilder:
    data_file = Path('../../data/processed/data.csv')

    target_var = 'price'

    def __init__(self):
        self.logger = Logger(__name__)

        if not self.data_file.exists():
            err = f'Data file does not exist {self.data_file}'
            self.logger.info(err)
            raise FileNotFoundError(err)
        

    def load_data(self):
        self.df = pd.read_csv(str(self.data_file))
        return self.df

   
    def _make_brand_feature(self):
        """There are too many models, let try to create a brand category using the first word of the model name."""
        self.df['brand'] = self.df['model_name'].apply(lambda x: ' '.join(x.split()[:1]))

        # Let's take only top 10 brands as our base brand & make other as 'other' category
        top_brands = self.df['brand'].value_counts().index[:10]
        self.df['brand'] = self.df['brand'].apply(lambda x: x if x in top_brands else 'other')


    def _make_engine_feature(self):
        """Model name contains the engine details e.g 150cc,Make new feature using the info as engine."""
        def extract_cc(val):
            match =  re.search(r"\d{2,}(cc)", val) 
            if match:
                return match.group().replace('cc','')
            else:
                return None
        
        self.df['engine'] = self.df['model_name'].apply(extract_cc)

    def _make_age_feature(self):
        """We can use model_year to calculate the age of the bike, Age might give us the better results or representation."""
        from datetime import date
        current_year = date.today().year

        self.df['age'] = self.df.model_year.apply(lambda x: current_year - x if x else None )

    def _handle_location(self):
        """Convert all the values into top 5 categories and make other as 'others'"""
        top_locations = self.df.location.value_counts().index[:5]

        self.df['location'] = self.df.location.apply(lambda x: x if x in top_locations else 'other')


    def clean_df(self):
        drop_cols = ['model_name','model_year']

        self.df.drop(drop_cols,axis=1,inplace=True)
        self.df.reset_index()
