"""
Baseline Energy Model (R2 & Annex A).
Builds a baseline of expected energy consumption from production volume,
product mix, and weather (Cooling Degree Days) using ordinary least squares.
Implemented with pure NumPy for maximum performance and portability.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from src.database import db

class BaselineModel:
    def __init__(self):
        self.fitted = False
        self.feature_names = []
        self.coefficients = {}
        self.intercept = 0.0
        self.metrics = {}

    def prepare_training_data(self, period: str = "2026-Q2") -> pd.DataFrame:
        """
        Prepares daily training features for a given baseline quarter (e.g. 2026-Q2).
        Features: units of Product_A, Product_B, Product_C, CDD, avg_temp_c
        Target: daily main meter energy (kWh)
        """
        if period == "2026-Q2":
            start_date, end_date = "2026-04-01", "2026-06-30"
        elif period == "2026-Q3":
            start_date, end_date = "2026-07-01", "2026-09-30"
        else:
            start_date, end_date = "2026-04-01", "2026-06-30"

        # 1. Daily energy
        df_energy = db.query(f"""
            SELECT CAST(ts AS DATE) as date, SUM(kwh) as daily_kwh
            FROM meter_15min
            WHERE meter_id = 'main'
              AND CAST(ts AS DATE) >= '{start_date}'
              AND CAST(ts AS DATE) <= '{end_date}'
            GROUP BY CAST(ts AS DATE)
            ORDER BY date
        """)

        # 2. Daily production mix
        df_prod = db.query(f"""
            SELECT date, product, units
            FROM production
            WHERE date >= '{start_date}' AND date <= '{end_date}'
        """)
        df_mix = df_prod.pivot(index="date", columns="product", values="units").fillna(0).reset_index()

        # 3. Daily weather
        df_weather = db.query(f"""
            SELECT date, avg_temp_c, cooling_degree_days
            FROM weather
            WHERE date >= '{start_date}' AND date <= '{end_date}'
        """)

        # Merge datasets
        df_merged = df_energy.merge(df_mix, on="date", how="inner").merge(df_weather, on="date", how="inner")
        return df_merged

    def fit(self, period: str = "2026-Q2") -> Dict[str, Any]:
        """Fits the regression baseline on the baseline quarter using OLS."""
        df = self.prepare_training_data(period=period)
        if len(df) == 0:
            raise ValueError(f"No baseline data available for period {period}")

        possible_prods = [c for c in ["Product_A", "Product_B", "Product_C"] if c in df.columns]
        self.feature_names = possible_prods + ["cooling_degree_days"]

        # Design matrix with intercept column
        X_raw = df[self.feature_names].values
        N = len(df)
        X = np.hstack([np.ones((N, 1)), X_raw])
        y = df["daily_kwh"].values

        # Solve OLS: beta = (X^T X)^-1 X^T y
        beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
        self.intercept = float(beta[0])
        self.coefficients = {name: float(beta[i+1]) for i, name in enumerate(self.feature_names)}

        # Predictions & goodness of fit
        y_pred = X @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 1.0
        rmse = float(np.sqrt(np.mean((y - y_pred) ** 2)))
        mean_y = float(np.mean(y))
        cv_rmse = float(rmse / mean_y * 100.0)

        self.fitted = True
        self.metrics = {
            "r2": round(r2, 4),
            "rmse_kwh": round(rmse, 2),
            "cv_rmse_pct": round(cv_rmse, 2),
            "intercept_kwh": round(self.intercept, 2),
            "coefficients": self.coefficients,
            "period": period,
            "sample_days": N
        }
        return self.metrics

    def predict_expected_energy(self, df_features: pd.DataFrame) -> np.ndarray:
        """Predicts expected energy for a dataframe having the feature columns."""
        if not self.fitted:
            self.fit("2026-Q2")

        N = len(df_features)
        X = np.ones((N, len(self.feature_names) + 1))
        for i, col in enumerate(self.feature_names):
            if col in df_features.columns:
                X[:, i + 1] = df_features[col].values
            else:
                X[:, i + 1] = 0.0

        beta = np.array([self.intercept] + [self.coefficients[name] for name in self.feature_names])
        return X @ beta

baseline_model = BaselineModel()
