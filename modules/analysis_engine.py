
import pandas as pd


def run_analysis(plan, df):
    operation = plan["operation"]
    column = plan.get("column")
    group_by = plan.get("group_by")
    second_column = plan.get("second_column")
    top_n = plan.get("top_n", 10)

    if operation == "count_rows":
        return len(df)

    if operation == "missing_values":
        return df.isnull().sum().to_dict()

    if operation == "sum":
        return df[column].sum()

    if operation == "mean":
        return df[column].mean()

    if operation == "median":
        return df[column].median()

    if operation == "min":
        return df[column].min()

    if operation == "max":
        return df[column].max()

    if operation == "value_counts":
        return df[column].value_counts().head(top_n).to_dict()

    if operation == "group_sum":
        result = df.groupby(group_by, dropna=False)[column].sum()
        return result.sort_values(ascending=False)

    if operation == "group_mean":
        result = df.groupby(group_by, dropna=False)[column].mean()
        return result.sort_values(ascending=False)

    if operation == "correlation":
        first = pd.to_numeric(df[column], errors="coerce")
        second = pd.to_numeric(df[second_column], errors="coerce")

        return first.corr(second)

    raise ValueError(f"Unsupported operation: {operation}")
