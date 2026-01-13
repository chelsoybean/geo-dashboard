import streamlit as st
import altair as alt
import pandas as pd

from script import *

def render():
    st.title("PROJECT")

    #READ DATA FROM GOOGLE SHEETS
    project_sheets_id = "18saFv1Kb5waaRbM6qOuufAicjh8MoynG2aVi24tHLjw"
    project_df = read_sheets(project_sheets_id, "table_append")

    #CONVERT TYPE
    num_cols = [
    'Qty', 'Harga', 'Jumlah', 'Total jual',
    'RAB', 'Realisasi', 'Profit',
    'Gap', 'Margin', 'Markup'
    ]

    project_df = clean_numeric(project_df, num_cols)

    project_df['Tanggal Pemesanan'] = pd.to_datetime(project_df['Tanggal Pemesanan'], errors='coerce')
    project_df['year'] = project_df['Tanggal Pemesanan'].dt.year
    project_df['month'] = project_df['Tanggal Pemesanan'].dt.month
    project_df['month_name'] = project_df['Tanggal Pemesanan'].dt.strftime('%b')


    #FILTERS
    years = sorted(project_df['year'].dropna().unique())
    year_options = ["ALL"] + years

    col_filter = st.columns([2,6], gap="large")
    with col_filter[0]:
        selected_year = st.selectbox(
            "Year",
            year_options,
            index=0,
        )

        if selected_year == "ALL":
            filtered_df = project_df.copy()
        else:
            filtered_df = project_df[project_df['year'] == selected_year]

    with col_filter[1]:
        month_map = (
        filtered_df[['month', 'month_name']]
        .drop_duplicates()
        .sort_values('month')
        )

        selected_months = st.pills(
            "Month",
            options=month_map['month_name'],
            default=month_map['month_name'],
            selection_mode="multi"
        )

        filtered_df = filtered_df[
            filtered_df['month_name'].isin(selected_months)
        ]

    # CALCULATE METRICS
    total_projects = filtered_df['Item Project'].count()
    avg_margin = filtered_df['Margin'].mean()
    cost_variance = filtered_df['Cost Var'].abs().mean()
    overbudget = (filtered_df['Gap']<0).sum() / filtered_df['Gap'].count()

    #Calcuulate percentage project profit higher than margin 
    margin_valid = filtered_df['Margin'].dropna()
    median_margin = margin_valid.median()
    profitable_projects = (margin_valid > median_margin).sum()
    percent_profitable = profitable_projects / margin_valid.count()

    #DISPLAY PAGE CONTENT
    with st.container():
        col = st.columns(5)
        with col[0]:
            st.metric("Total Project", total_projects,
                      help="Jumlah total item project yang telah dikerjakan.")
        with col[1]:
            st.metric("Overbudget", f"{overbudget*100:.2f}%", 
                      help="Persentase project yang mengeluarkan biaya lebih besar dari rencana anggaran (RAB)")
        with col[2]:
            st.metric("Cost Variance", f"{cost_variance*100:.2f}%",
                      help="Rata-rata besarnya persentase penyimpangan biaya project dibandingkan rencana anggaran (RAB), baik lebih tinggi maupun lebih rendah.")
        with col[3]:
            st.metric("Avg Margin", f"{avg_margin*100:.2f}%",
                      help="Rata-rata persentase profit per project, menggambarkan kualitas profit project secara umum")
        with col[4]:
            st.metric("Higher Profit", f"{percent_profitable*100:.2f}%", 
                      help="Persentase project dengan margin di atas median margin.")

    #Chart profit per month
    monthly_profit = (
        project_df
        .groupby(['year', 'month', 'month_name'], as_index=False)
        .agg(total_profit=('Profit', 'sum'))
    )

    monthly_profit['year'] = monthly_profit['year'].astype(str)
    monthly_profit = monthly_profit.sort_values('month')

    #Chart jml Kategori project
    category_counts = (
        filtered_df
        .groupby('Kategori')
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
    )
    
    #Chart profit vs qty
    scatter_df = (
        project_df.copy().dropna(subset=["Profit", "Qty"])
    )
    scatter_df["year"] = scatter_df["year"].astype(str)

    #Chart cost variance
    cv_summary = filtered_df.groupby('Kategori').agg(
        avg_profit = ('Margin', 'mean'),
        mean_cv = ('Cost Var', 'mean'),
        median_cv = ('Cost Var', 'median'),
        std_cv = ('Cost Var', 'std'),
        count = ('Cost Var', 'count')
    ).reset_index()

    cv_summary.dropna(subset=['mean_cv'], inplace=True)
    cv_summary['Status'] = cv_summary['mean_cv'].apply(lambda x: 'Hemat' if x > 0 else 'Overbudget')

    #Chart profit vs cost var per kategori
    summary_long = cv_summary.melt(id_vars='Kategori', 
                               value_vars=['avg_profit', 'mean_cv'], 
                               var_name='Metric', 
                               value_name='Value')

    # Biar label metric lebih ramah
    summary_long['Metric'] = summary_long['Metric'].map({
        'avg_profit': 'Average Profit',
        'mean_cv': 'Mean Cost Variance',
    })
    sorted_categories = cv_summary.sort_values('avg_profit', ascending=False)['Kategori'].tolist()

    #DISPLAY CHARTS
    col_chart = st.columns(2)
    with col_chart[0]:
        st.subheader("Monthly Profit Trend")
        chart = (
            alt.Chart(monthly_profit)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    'month_name:N',
                    sort=month_map['month_name'].tolist(),  # biar Jan–Dec
                    title='Month'
                ),
                y=alt.Y('total_profit:Q', title='Total Profit'),
                color=alt.Color('year:N', title='Year'),
                tooltip=['year', 'month_name', 'total_profit']
            )
        .properties(height=350)
        )

        st.altair_chart(chart, use_container_width=True)

    with col_chart[1]:
        st.subheader("Project Count by Category")
        chart = (
            alt.Chart(category_counts)
            .mark_bar()
            .encode(
                x=alt.X('count:Q', sort='ascending', title='Jumlah Project'),
                y=alt.Y('Kategori:N', sort='-x', title='Kategori')
            )
            .properties(height=350)
        )

        # Tambah label di ujung bar
        text = (
            alt.Chart(category_counts)
            .mark_text(
                align='left',
                baseline='middle',
                dx=3  # geser sedikit ke kanan dari bar
            )
            .encode(
                x=alt.X('count:Q', title='Jumlah Project'),
                y=alt.Y('Kategori:N', sort='-x'),
                text='count:Q'
            )
            .properties(height=350)
        )

        st.altair_chart(chart + text, use_container_width=True)

    st.subheader("Profit vs Quantity")
    scatter = (
        alt.Chart(scatter_df)
        .mark_circle(size=80, opacity=0.7)
        .encode(
            x=alt.X("Qty:Q", scale=alt.Scale(type="log"), title="Quantity (log)"),
            y=alt.Y("Profit:Q", scale=alt.Scale(type="log"), title="Profit (log)"),
            color=alt.Color("year:N", title="Year"),
            tooltip=[
                "year:N",
                "Qty:Q",
                alt.Tooltip("Profit:Q", format=",")
            ]
        )
        .properties(height=450)
    )

    st.altair_chart(scatter, use_container_width=True)

    col_chart2 = st.columns(2)
    with col_chart2[0]:
        st.subheader("Rata-rata Cost Variance by Category")
        chart = (
            alt.Chart(cv_summary)
            .mark_bar()
            .encode(
                y=alt.Y('Kategori:N', sort='-x', title='Kategori'),
                x=alt.X('mean_cv:Q', title='Mean Cost Variance', axis=alt.Axis(format='%')),
                color=alt.Color('Status:N', title='Status',
                    scale=alt.Scale(domain=['Hemat', 'Overbudget'], range=['green', 'red']),
                    legend=alt.Legend(orient='top', title=None, direction='horizontal')),
                tooltip=[
                    alt.Tooltip('Kategori:N'),
                    alt.Tooltip('mean_cv:Q', format='.2%', title="Mean Cost Variance"),
                    alt.Tooltip('count:Q')
                ]
            )
            .properties(height=400)
        )

        # Garis vertical di 0 sebagai baseline
        zero_line = alt.Chart(pd.DataFrame({'x':[0]})).mark_rule(color='black').encode(x='x')

        st.altair_chart(chart + zero_line, use_container_width=True)

    with col_chart2[1]:
        st.subheader("Margin vs Cost Variance by Category")
        chart = (
            alt.Chart(summary_long)
            .mark_bar()
            .encode(
                y=alt.Y('Kategori:N', sort=sorted_categories, title='Kategori'),
                x=alt.X('Value:Q', title='Mean Value', axis=alt.Axis(format='%')),
                color=alt.Color('Metric:N', title='Metric', scale=alt.Scale(range=['#1f77b4', '#ff7f0e']), 
                                legend=alt.Legend(orient='top', title=None, direction='horizontal')),
                tooltip=['Kategori', 'Metric', alt.Tooltip('Value', format='.2%')],
                yOffset='Metric:N' 
            )
            .properties(height=400)
        )

        st.altair_chart(chart, use_container_width=True)


