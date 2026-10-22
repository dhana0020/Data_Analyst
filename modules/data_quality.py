import pandas as pd
import numpy as np


def get_data_quality_report(df):
    """
    Analyze the overall quality of a dataset.

    Returns:
        dict containing:
        - overall_score
        - total_cells
        - missing_cells
        - missing_percentage
        - duplicate_rows
        - duplicate_percentage
        - column_issues
        - numeric_outliers
    """

    total_cells = df.shape[0] * df.shape[1]

    if total_cells == 0:
        return {
            "overall_score": 0,
            "total_cells": 0,
            "missing_cells": 0,
            "missing_percentage": 0,
            "duplicate_rows": 0,
            "duplicate_percentage": 0,
            "column_issues": [],
            "numeric_outliers": {},
        }

    # -----------------------------
    # Missing values
    # -----------------------------

    missing_cells = int(df.isna().sum().sum())
    missing_percentage = (missing_cells / total_cells) * 100

    # -----------------------------
    # Duplicate rows
    # -----------------------------

    duplicate_rows = int(df.duplicated().sum())

    if len(df) > 0:
        duplicate_percentage = (
            duplicate_rows / len(df)
        ) * 100
    else:
        duplicate_percentage = 0

    # -----------------------------
    # Column-level issues
    # -----------------------------

    column_issues = []

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        if missing_count > 0:

            percentage = (
                missing_count / len(df)
            ) * 100

            column_issues.append({
                "column": column,
                "issue": "Missing Values",
                "count": missing_count,
                "percentage": round(percentage, 2)
            })

        # Check columns with only one unique value

        unique_count = df[column].nunique(dropna=True)

        if unique_count <= 1 and len(df) > 1:

            column_issues.append({
                "column": column,
                "issue": "Constant Column",
                "count": unique_count,
                "percentage": 100.0
            })

    # -----------------------------
    # Numeric outlier detection
    # IQR method
    # -----------------------------

    numeric_outliers = {}

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    for column in numeric_columns:

        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = series[
            (series < lower_bound) |
            (series > upper_bound)
        ]

        if len(outliers) > 0:

            numeric_outliers[column] = {
                "count": int(len(outliers)),
                "percentage": round(
                    (len(outliers) / len(series)) * 100,
                    2
                ),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound)
            }

    # -----------------------------
    # Quality score
    # -----------------------------

    score = 100.0

    # Missing data penalty
    score -= min(
        missing_percentage * 0.5,
        30
    )

    # Duplicate penalty
    score -= min(
        duplicate_percentage * 0.5,
        20
    )

    # Outlier penalty
    total_outlier_percentage = 0

    for info in numeric_outliers.values():
        total_outlier_percentage += info["percentage"]

    score -= min(
        total_outlier_percentage * 0.1,
        10
    )

    score = max(
        0,
        min(100, score)
    )

    return {
        "overall_score": round(score, 1),
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_percentage": round(
            missing_percentage,
            2
        ),
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": round(
            duplicate_percentage,
            2
        ),
        "column_issues": column_issues,
        "numeric_outliers": numeric_outliers,
    }


def get_quality_dataframe(report):
    """
    Convert column issues into a DataFrame
    for display in Streamlit.
    """

    issues = report["column_issues"]

    if not issues:
        return pd.DataFrame(
            columns=[
                "Column",
                "Issue",
                "Count",
                "Percentage"
            ]
        )

    return pd.DataFrame([
        {
            "Column": issue["column"],
            "Issue": issue["issue"],
            "Count": issue["count"],
            "Percentage": issue["percentage"]
        }
        for issue in issues
    ])


def get_quality_status(score):
    """
    Convert quality score into a human-readable status.
    """

    if score >= 90:
        return "Excellent"

    if score >= 75:
        return "Good"

    if score >= 50:
        return "Needs Attention"

    return "Poor"