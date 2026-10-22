
from io import BytesIO

import pandas as pd

from modules.data_profiler import (
    get_dataset_metrics,
    get_data_profile,
    get_summary_statistics
)


def generate_excel_report(
    df,
    result=None,
    question=None,
    explanation=None
):
    output = BytesIO()

    metrics = get_dataset_metrics(df)

    metrics_df = pd.DataFrame(
        list(metrics.items()),
        columns=["Metric", "Value"]
    )

    profile_df = get_data_profile(df)
    summary_df = get_summary_statistics(df)

    if isinstance(result, pd.Series):
        result_df = result.rename("Value").reset_index()

    elif isinstance(result, dict):
        result_df = pd.DataFrame(
            list(result.items()),
            columns=["Category", "Value"]
        )

    elif result is not None:
        result_df = pd.DataFrame(
            {"Result": [str(result)]}
        )

    else:
        result_df = pd.DataFrame(
            {"Result": ["No analysis performed yet"]}
        )

    question_df = pd.DataFrame({
        "Field": ["Question", "Explanation"],
        "Details": [
            question or "No question asked yet",
            explanation or "No explanation available"
        ]
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        metrics_df.to_excel(
            writer,
            sheet_name="Dataset Metrics",
            index=False
        )

        profile_df.to_excel(
            writer,
            sheet_name="Column Profile",
            index=False
        )

        summary_df.to_excel(
            writer,
            sheet_name="Summary Statistics",
            index=True
        )

        question_df.to_excel(
            writer,
            sheet_name="AI Analysis Details",
            index=False
        )

        result_df.to_excel(
            writer,
            sheet_name="Analysis Result",
            index=False
        )

    output.seek(0)
    return output.getvalue()
