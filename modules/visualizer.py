
import pandas as pd
import plotly.express as px
import streamlit as st


def display_analysis_result(result, plan):
    operation = plan["operation"]
    column = plan.get("column")

    st.subheader("Analysis Result")

    if isinstance(result, pd.Series):
        st.dataframe(
            result.rename("Value").reset_index(),
            width="stretch"
        )

        if len(result) > 0:
            chart_data = result.rename("Value").reset_index()
            category_column = chart_data.columns[0]

            fig = px.bar(
                chart_data,
                x=category_column,
                y="Value",
                title=plan.get("explanation", "Analysis results")
            )
            st.plotly_chart(fig, width="stretch")

    elif isinstance(result, dict):
        if result:
            result_df = pd.DataFrame(
                list(result.items()),
                columns=["Category", "Value"]
            )

            st.dataframe(result_df, width="stretch")

            if operation == "value_counts":
                fig = px.bar(
                    result_df,
                    x="Category",
                    y="Value",
                    title=f"Distribution of {column}"
                )
                st.plotly_chart(fig, width="stretch")
        else:
            st.info("No results to display.")

    elif isinstance(result, (int, float)):
        st.metric("Result", f"{result:,.4f}" if isinstance(
            result, float
        ) else f"{result:,}")

    else:
        st.write(result)


def display_exploratory_charts(df):
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    st.subheader("Explore Your Data")

    if not numeric_columns:
        st.info("No numeric columns are available for charts.")
        return

    chart_type = st.selectbox(
        "Choose chart type",
        ["Histogram", "Bar Chart", "Scatter Plot"]
    )

    if chart_type == "Histogram":
        column = st.selectbox(
            "Select numeric column",
            numeric_columns,
            key="histogram_column"
        )

        fig = px.histogram(
            df,
            x=column,
            title=f"Distribution of {column}"
        )
        st.plotly_chart(fig, width="stretch")

    elif chart_type == "Bar Chart":
        if not categorical_columns:
            st.info("No categorical columns are available.")
            return

        category = st.selectbox(
            "Select category column",
            categorical_columns,
            key="bar_category"
        )

        value = st.selectbox(
            "Select numeric column",
            numeric_columns,
            key="bar_value"
        )

        chart_data = (
            df.groupby(category, dropna=False)[value]
            .sum()
            .reset_index()
            .sort_values(value, ascending=False)
            .head(20)
        )

        fig = px.bar(
            chart_data,
            x=category,
            y=value,
            title=f"{value} by {category}"
        )
        st.plotly_chart(fig, width="stretch")

    elif chart_type == "Scatter Plot":
        x_column = st.selectbox(
            "Select X-axis column",
            numeric_columns,
            key="scatter_x"
        )

        y_column = st.selectbox(
            "Select Y-axis column",
            numeric_columns,
            key="scatter_y"
        )

        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} vs {x_column}"
        )
        st.plotly_chart(fig, width="stretch")
