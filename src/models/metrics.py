import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import cross_val_score
import pandas as pd

class Metrics:

    def mape(self, targets, predictions):
        return np.mean(np.abs((targets - predictions)) / targets) * 100

    def adj_r2(self, ind_vars, targets, predictions):
        r2 = r2_score(targets, predictions)
        n = ind_vars.shape[0]
        k = ind_vars.shape[1]
        return 1-((1-r2)*(n-1)/(n-k-1))

    # Model performance check
    def model_perf(self, model, inp, out, cross_val=False):

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
