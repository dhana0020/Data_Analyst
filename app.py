
import streamlit as st
import pandas as pd
import hashlib

from modules.report_generator import generate_excel_report
from modules.data_loader import load_dataset
from modules.data_profiler import (
    get_dataset_metrics,
    get_data_profile,
    get_summary_statistics
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


st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Data Analyst")
st.write(
    "Upload a dataset, explore its contents, "
    "and ask questions in natural language."
)

initialize_chat()

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        # Load the uploaded dataset
        df = load_dataset(uploaded_file)

        if df.empty:
            st.warning("The uploaded dataset is empty.")
            st.stop()

        # Identify the dataset so results from a previous
        # dataset are not included in the new dataset's report.
        dataset_id = hashlib.sha256(
            uploaded_file.getvalue()
        ).hexdigest()

        if st.session_state.get("current_dataset_id") != dataset_id:
            st.session_state["current_dataset_id"] = dataset_id
            st.session_state["latest_analysis_result"] = None
            st.session_state["latest_analysis_question"] = None
            st.session_state["latest_analysis_explanation"] = None
            clear_chat()

        st.success("Dataset loaded successfully!")

        # Dataset preview
        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(10).astype(str),
            width="stretch"
        )

        # Dataset metrics
        metrics = get_dataset_metrics(df)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Rows", f"{metrics['rows']:,}")
        col2.metric("Columns", f"{metrics['columns']:,}")
        col3.metric(
            "Missing Values",
            f"{metrics['missing_values']:,}"
        )
        col4.metric(
            "Duplicate Rows",
            f"{metrics['duplicate_rows']:,}"
        )

        # Data profile
        with st.expander("Data Profile"):
            st.dataframe(
                get_data_profile(df),
                width="stretch"
            )

        # Summary statistics
        with st.expander("Summary Statistics"):
            st.dataframe(
                get_summary_statistics(df),
                width="stretch"
            )

        # Complete Excel report
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
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key="download_complete_report"
        )

        # Exploratory visualizations
        display_exploratory_charts(df)

        st.divider()
        st.subheader("Ask Your Dataset")

        # Display conversation history
        display_chat_history()

        question = st.chat_input(
            "Ask a question about your dataset..."
        )

        if question:
            add_message("user", question)

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing your question..."):
                    try:
                        client = get_client()

                        # Generate an analysis plan using Gemini
                        plan = get_plan(
                            question,
                            df,
                            client,
                            st.session_state.chat_history[:-1]
                        )

                        # Execute the analysis
                        result = run_analysis(plan, df)

                        # Save the latest analysis for Excel export
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

                        st.write(
                            plan.get(
                                "explanation",
                                "Here is your analysis."
                            )
                        )

                        # Display result and visualization
                        display_analysis_result(result, plan)

                        # Prepare result for CSV download
                        if isinstance(result, dict):
                            report_df = pd.DataFrame(
                                list(result.items()),
                                columns=["Category", "Value"]
                            )

                        elif isinstance(result, pd.Series):
                            report_df = (
                                result.rename("Value")
                                .rename_axis("Category")
                                .reset_index()
                            )

                        else:
                            report_df = pd.DataFrame({
                                "Result": [str(result)]
                            })

                        st.download_button(
                            label="Download Analysis Result",
                            data=report_df.to_csv(index=False),
                            file_name="analysis_result.csv",
                            mime="text/csv",
                            key="download_analysis_result"
                        )

                        # Save the answer in chat history
                        if isinstance(result, dict):
                            answer = str(result)

                        elif hasattr(result, "to_string"):
                            answer = result.to_string()

                        else:
                            answer = str(result)

                        add_message(
                            "assistant",
                            (
                                f"{plan.get('explanation', 'Analysis result')}"
                                f"\n\nResult:\n{answer}"
                            )
                        )

                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

        # Clear conversation
        if st.button("Clear Chat"):
            clear_chat()
            st.rerun()

    except Exception as e:
        st.error(f"Could not load the dataset: {e}")

else:
    st.info("Upload a CSV or XLSX file to get started.")
