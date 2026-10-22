
import streamlit as st
import pandas as pd

from modules.report_generator import generate_excel_report
from modules.data_loader import load_dataset
from modules.data_profiler import (
    get_dataset_metrics,
    get_data_profile,
    get_summary_statistics
)
from modules.data_quality import (
    get_data_quality_report,
    get_quality_dataframe,
    get_quality_status
)
from modules.ai_analyst import get_client, get_plan
from modules.analysis_engine import run_analysis
from modules.visualizer import (
    display_analysis_result,
    display_exploratory_charts
)
from modules.chat_manager import (
    initialize_chat,
    add_message,
    display_chat_history,
    clear_chat
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title("📊 AI Data Analyst")

st.write(
    "Upload a dataset, explore its contents, "
    "and ask questions in natural language."
)


# ============================================================
# INITIALIZE CHAT
# ============================================================

initialize_chat()


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx"]
)


# ============================================================
# MAIN APPLICATION
# ============================================================

if uploaded_file is not None:

    try:

        # ----------------------------------------------------
        # LOAD DATASET
        # ----------------------------------------------------

        df = load_dataset(uploaded_file)

        if df.empty:
            st.warning("The uploaded dataset is empty.")
            st.stop()

        st.success("Dataset loaded successfully!")


        # ----------------------------------------------------
        # DATASET PREVIEW
        # ----------------------------------------------------

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(10).astype(str),
            width="stretch"
        )


        # ----------------------------------------------------
        # BASIC DATASET METRICS
        # ----------------------------------------------------

        metrics = get_dataset_metrics(df)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Rows",
            f"{metrics['rows']:,}"
        )

        col2.metric(
            "Columns",
            f"{metrics['columns']:,}"
        )

        col3.metric(
            "Missing Values",
            f"{metrics['missing_values']:,}"
        )

        col4.metric(
            "Duplicate Rows",
            f"{metrics['duplicate_rows']:,}"
        )


        # ====================================================
        # DATA QUALITY ENGINE
        # ====================================================

        st.divider()

        st.subheader("🔎 Data Health")

        quality_report = get_data_quality_report(df)

        quality_score = quality_report["overall_score"]

        quality_status = get_quality_status(
            quality_score
        )


        # ----------------------------------------------------
        # QUALITY METRICS
        # ----------------------------------------------------

        q1, q2, q3 = st.columns(3)

        q1.metric(
            "Data Quality Score",
            f"{quality_score}/100"
        )

        q2.metric(
            "Missing Data",
            f"{quality_report['missing_percentage']}%"
        )

        q3.metric(
            "Duplicate Rows",
            f"{quality_report['duplicate_percentage']}%"
        )


        # ----------------------------------------------------
        # QUALITY STATUS
        # ----------------------------------------------------

        st.write(
            f"**Overall Data Health: {quality_status}**"
        )


        # ----------------------------------------------------
        # COLUMN QUALITY ISSUES
        # ----------------------------------------------------

        quality_issues = get_quality_dataframe(
            quality_report
        )

        if not quality_issues.empty:

            with st.expander(
                "⚠️ View Data Quality Issues"
            ):

                st.dataframe(
                    quality_issues,
                    width="stretch"
                )

        else:

            st.success(
                "✓ No major column-level "
                "data quality issues detected."
            )


        # ----------------------------------------------------
        # NUMERIC OUTLIERS
        # ----------------------------------------------------

        outliers = quality_report[
            "numeric_outliers"
        ]

        if outliers:

            with st.expander(
                "📈 Potential Numeric Outliers"
            ):

                for column, info in outliers.items():

                    st.write(
                        f"**{column}** — "
                        f"{info['count']} potential "
                        f"outlier(s) "
                        f"({info['percentage']}%)"
                    )


        # ====================================================
        # DATA PROFILE
        # ====================================================

        with st.expander("Data Profile"):

            st.dataframe(
                get_data_profile(df),
                width="stretch"
            )


        # ====================================================
        # SUMMARY STATISTICS
        # ====================================================

        with st.expander("Summary Statistics"):

            st.dataframe(
                get_summary_statistics(df),
                width="stretch"
            )


        # ====================================================
        # COMPLETE EXCEL REPORT
        # ====================================================

        st.download_button(
            label="Download Complete Excel Report",

            data=generate_excel_report(
                df,
                result=st.session_state.get(
                    "latest_analysis_result"
                ),
                question=st.session_state.get(
                    "latest_analysis_question"
                ),
                explanation=st.session_state.get(
                    "latest_analysis_explanation"
                )
            ),

            file_name="ai_data_analyst_report.xlsx",

            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )


        # ====================================================
        # EXPLORATORY CHARTS
        # ====================================================

        display_exploratory_charts(df)


        # ====================================================
        # AI DATA ANALYSIS
        # ====================================================

        st.divider()

        st.subheader("Ask Your Dataset")


        # ----------------------------------------------------
        # DISPLAY CHAT HISTORY
        # ----------------------------------------------------

        display_chat_history()


        # ----------------------------------------------------
        # CHAT INPUT
        # ----------------------------------------------------

        question = st.chat_input(
            "Ask a question about your dataset..."
        )


        if question:

            # ------------------------------------------------
            # STORE USER QUESTION
            # ------------------------------------------------

            add_message(
                "user",
                question
            )


            # ------------------------------------------------
            # DISPLAY USER MESSAGE
            # ------------------------------------------------

            with st.chat_message("user"):

                st.markdown(question)


            # ------------------------------------------------
            # AI RESPONSE
            # ------------------------------------------------

            with st.chat_message("assistant"):

                with st.spinner(
                    "Analyzing your question..."
                ):

                    try:

                        # ----------------------------------------
                        # GET GEMINI CLIENT
                        # ----------------------------------------

                        client = get_client()


                        # ----------------------------------------
                        # GENERATE ANALYSIS PLAN
                        # ----------------------------------------

                        plan = get_plan(
                            question,
                            df,
                            client,
                            st.session_state.chat_history[:-1]
                        )


                        # ----------------------------------------
                        # EXECUTE ANALYSIS
                        # ----------------------------------------

                        result = run_analysis(
                            plan,
                            df
                        )


                        # ----------------------------------------
                        # SAVE LATEST ANALYSIS
                        # ----------------------------------------

                        st.session_state[
                            "latest_analysis_result"
                        ] = result

                        st.session_state[
                            "latest_analysis_question"
                        ] = question

                        st.session_state[
                            "latest_analysis_explanation"
                        ] = plan.get(
                            "explanation",
                            "Analysis completed."
                        )


                        # ----------------------------------------
                        # DISPLAY EXPLANATION
                        # ----------------------------------------

                        st.write(
                            plan.get(
                                "explanation",
                                "Here is your analysis."
                            )
                        )


                        # ----------------------------------------
                        # DISPLAY RESULT + CHART
                        # ----------------------------------------

                        display_analysis_result(
                            result,
                            plan
                        )


                        # ====================================================
                        # DOWNLOAD ANALYSIS RESULT
                        # ====================================================

                        if isinstance(
                            result,
                            dict
                        ):

                            report_df = pd.DataFrame(
                                list(result.items()),
                                columns=[
                                    "Category",
                                    "Value"
                                ]
                            )

                        elif isinstance(
                            result,
                            pd.Series
                        ):

                            report_df = (
                                result
                                .rename("Value")
                                .reset_index()
                            )

                        else:

                            report_df = pd.DataFrame(
                                {
                                    "Result": [
                                        str(result)
                                    ]
                                }
                            )


                        st.download_button(
                            label="Download Analysis Result",

                            data=report_df.to_csv(
                                index=False
                            ),

                            file_name=(
                                "analysis_result.csv"
                            ),

                            mime="text/csv",

                            key=(
                                "download_analysis_result"
                            )
                        )


                        # ====================================================
                        # STORE RESULT IN CHAT HISTORY
                        # ====================================================

                        if isinstance(
                            result,
                            dict
                        ):

                            answer = str(result)

                        elif hasattr(
                            result,
                            "to_string"
                        ):

                            answer = result.to_string()

                        else:

                            answer = str(result)


                        explanation = plan.get(
                            "explanation",
                            "Analysis result"
                        )

                        add_message(
                            "assistant",
                            f"{explanation}\n\n"
                            f"Result:\n{answer}"
                        )


                    except Exception as e:

                        st.error(
                            f"Analysis failed: {e}"
                        )


        # ====================================================
        # CLEAR CHAT
        # ====================================================

        if st.button("Clear Chat"):

            clear_chat()

            st.rerun()


    except Exception as e:

        st.error(
            f"Could not load the dataset: {e}"
        )


# ============================================================
# NO DATASET
# ============================================================

else:

    st.info(
        "Upload a CSV or XLSX file to get started."
    )