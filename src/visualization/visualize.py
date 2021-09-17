
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from ..utils.logger import Logger
import seaborn as sns

logger = Logger(__name__,__name__ == '__main__')

REPORTS_PATH = Path('visualizations')

def _get_df():
    path = Path('data/processed/processed.csv')

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
        plt.title(f"{col} Distribution")
        dist_plot = sns.displot(df[col])

        dist_plot.savefig(str(REPORTS_PATH / f"{col}_distribution.png"))

def plot_heatmap():
    df = _get_df()
    plt.figure(figsize=(12,8))
    plt.title("Correlation Heatmap")
    hmap = sns.heatmap(data=df.corr(),annot=True)

    hmap.get_figure().savefig(str(REPORTS_PATH / "heatmap.png"))


def owner_coutplot():
    df = _get_df()
    plt.figure(figsize=(12,8))
    plt.title("Owners Countplot")
    cplot = sns.countplot(x='owner',data=df)

    cplot.get_figure().savefig(str(REPORTS_PATH / "onwers_countplot.png"))

def top_cities_plot():
    
    path = Path('data/processed/data.csv')

    if not path.exists():
        err = f"File does not exist {str(path)}"
        logger.error(err)
        raise FileNotFoundError(err)
    
    df = pd.read_csv(str(path))

    top = 20
    plt.figure(figsize=(18,8))
    plt.xticks(rotation='vertical')
    plt.title(f'Top {top} cities where used bikes are sold')
    plot = sns.countplot(x='location',data=df,order=df.location.value_counts().iloc[:top].index)

    plot.get_figure().savefig(str(REPORTS_PATH / f"top_{top}_cities.png"))

   


if __name__ == '__main__':
    pairplot()

    plot_feature_dist()

    plot_heatmap()

    owner_coutplot()

    top_cities_plot()

