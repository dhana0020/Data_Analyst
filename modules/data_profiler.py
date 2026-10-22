
import pandas as pd


def get_dataset_metrics(df):
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }


def get_data_profile(df):
    return pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isnull().sum().values,
        "Unique Values": df.nunique().values
    })


def get_summary_statistics(df):
    return df.describe(include="all").fillna("").astype(str)
