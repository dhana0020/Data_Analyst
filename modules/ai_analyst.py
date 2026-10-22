
import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    return genai.Client(api_key=api_key)


def get_plan(question, df, client, chat_history=None):
    schema = [
        {
            "column": str(col),
            "dtype": str(df[col].dtype),
            "examples": (
                df[col].dropna().astype(str).head(3).tolist()
            )
        }
        for col in df.columns
    ]

    history_text = ""

    if chat_history:
        history_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in chat_history[-6:]
        )

    prompt = f"""
You are an AI data analysis planner.

Return ONLY a valid JSON object with these keys:
operation, column, group_by, second_column, top_n, explanation.

Allowed operations:
count_rows, sum, mean, median, min, max, value_counts,
group_sum, group_mean, correlation, missing_values.

Rules:
- Use only column names from the supplied dataset schema.
- column must be a column name or null.
- group_by must be a column name or null.
- second_column must be a column name or null.
- top_n must be an integer between 1 and 20.
- Resolve follow-up questions using the previous conversation.
- Use the current question as the main instruction.
- Do not invent results or dataset values.
- For count_rows, count all dataset rows.
- For sum, mean, median, min and max, use column.
- For value_counts, use column as the categorical column.
- For group_sum and group_mean, use column as the numeric
  column and group_by as the grouping column.
- For correlation, use column and second_column.
- For missing_values, no column is required.
- explanation must briefly describe the intended calculation.

Dataset schema:
{json.dumps(schema, ensure_ascii=False)}

Previous conversation:
{history_text}

Current user question:
{question}
"""

    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0
                )
            )
            break

        except Exception as e:
            error_message = str(e).upper()

            temporary_errors = (
                "503",
                "UNAVAILABLE",
                "429",
                "RESOURCE_EXHAUSTED",
                "500",
                "INTERNAL",
                "502",
                "504"
            )

            is_temporary = any(
                code in error_message
                for code in temporary_errors
            )

            if not is_temporary:
                raise

            if attempt == 2:
                raise RuntimeError(
                    f"Gemini failed after 3 attempts. "
                    f"Original error: {e}"
                ) from e

            time.sleep(2 ** (attempt + 1))

    if response is None or not response.text:
        raise ValueError(
            "Gemini returned an empty response. Please try again."
        )

    try:
        plan = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError(
            "Gemini returned an invalid analysis plan. "
            "Please try your question again."
        ) from e

    if not isinstance(plan, dict):
        raise ValueError("The analysis plan must be a JSON object.")

    allowed_operations = {
        "count_rows",
        "sum",
        "mean",
        "median",
        "min",
        "max",
        "value_counts",
        "group_sum",
        "group_mean",
        "correlation",
        "missing_values"
    }

    operation = plan.get("operation")

    if operation not in allowed_operations:
        raise ValueError(
            f"Unsupported analysis operation: {operation}"
        )

    for key in ("column", "group_by", "second_column"):
        col = plan.get(key)

        if col is not None and col not in df.columns:
            raise ValueError(
                f"Gemini selected an invalid column: {col}"
            )

    column_required = {
        "sum",
        "mean",
        "median",
        "min",
        "max",
        "value_counts",
        "group_sum",
        "group_mean"
    }

    if operation in column_required and plan.get("column") is None:
        raise ValueError(
            f"The {operation} operation requires a column."
        )

    if operation in {"group_sum", "group_mean"}:
        if plan.get("group_by") is None:
            raise ValueError(
                "A grouping column is required for this analysis."
            )

    if operation == "correlation":
        if (
            plan.get("column") is None
            or plan.get("second_column") is None
        ):
            raise ValueError(
                "Correlation requires two columns."
            )

    try:
        top_n = int(plan.get("top_n", 10))
    except (TypeError, ValueError):
        top_n = 10

    plan["top_n"] = max(1, min(top_n, 20))

    if not isinstance(plan.get("explanation"), str):
        plan["explanation"] = "Analysis of the uploaded dataset."

    return plan
