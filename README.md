# Used Bike Price Prediction Using Machine Learning
A predictive model to get the resell value of any bike in India given some features like brand,mileage power etc.


## Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         and `-` delimited description, e.g.
    │                         `1.0-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, csv etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    


--------
## Installation
Clone this repo in your local machine. Create a virtual environment to install the packages like this,

```> virtualenv venv```
After it successfully creates virtual environment then activate it.

```
> source venv/bin/activate # for linux

> .\venv\Scripts\actiavet # for windows
```

Now install all the require packages from `requirements.txt` file like this,

```> pip install -r requirements.txt```


## Making Dataset
This repo already contains the data in `data/raw/data.csv` which you can directly use. Or you can scrape the data directly from the source using the script.The orinal way to generate a dataset is to collect a data from source and store it in the sqlite database & then export the dataset into .csv file.
To scrape the data from source then run this command.

```
> python -m src.data.make_dataset
```
It will check for local sqlite database and if could not find then will ask you start the scrapping.

## Training Model
To start training the model you can start by using this command,
```
> python -m src.models.train_model
```
All the intermediatery steps like pre-processing,feature engineering, outlier removal will be performed automatically. All the generated models will be saved in `models` directory.

## Visualization
To generate basic visualization for the dataset, you can use this command.

```
> python -m src.visualization.visualize
```

All the generated figures will be stored in `visualizations` directory.

## Logging 
All the operations will be logged in the `debug.log` file which will be generated automatically once you start running the code.