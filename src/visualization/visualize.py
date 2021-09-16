
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from ..utils.logger import Logger
import seaborn as sns

logger = Logger(__name__,__name__ == '__main__')

REPORTS_PATH = Path('visualizations')

def _get_df():
    path = Path('data/processed/data.csv')

    if not path.exists():
        err = f"File does not exist {str(path)}"
        logger.error(err)
        raise FileNotFoundError(err)

    return pd.read_csv(str(path))

def pairplot():
    df = _get_df()

    pplot = sns.pairplot(df)
    pplot.savefig(str(REPORTS_PATH / 'pairplot_fig.png'))


def plot_feature_dist():
    df = _get_df()

    for col in df.select_dtypes(include=['int','float']).columns:
        dist_plot = sns.displot(df[col])

        dist_plot.savefig(str(REPORTS_PATH / f"{col}_distribution.png"))



if __name__ == '__main__':
    pairplot()

    plot_feature_dist()

