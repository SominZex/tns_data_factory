import pandas as pd
import streamlit as st
import plotly.express as px

def analyze_counter_shelf_products(store_data, all_data): 
    st.markdown("<h4 style='color: green; text-align: center;'>COUNTER SHELF PRODUCTS ANALYSIS</h4>", unsafe_allow_html=True)
    st.markdown("---")

    # List of counter shelf product categories to filter
    counter_shelf_categories = [
        "Candies & Toffees", 
        "Sweets, Chocolates & Candies", 
        "Chocolates", 
        "Gums, Mints & Mouth Freshener"
    ]

    # Move controls to the sidebar
    st.sidebar.markdown("## Filter Options for counter shelf")
    
    # Select a store from the store names in the sidebar
    store_names = store_data['storeName'].unique()
    selected_store = st.sidebar.selectbox("Select a Store:", store_names, key="store_selector_counter_shelf")

    # User input for selecting the metric for performance analysis in the sidebar
    metric = st.sidebar.selectbox("Select Metric for Counter Shelf Products Analysis:", 
                                  ["Total Quantity", "Total Revenue", "Profit", "Profit Margin"], 
                                  key="metric_selector_counter_shelf")

    # Option to display data labels in the sidebar
    show_data_labels = st.sidebar.checkbox("Show Data Labels", value=True, key="data_labels_counter_shelf")

    # Choose plot type, set default to "Pie" in the sidebar
    plot_type = st.sidebar.selectbox("Select Plot Type:", ["Bar", "Scatter", "Pie"], key="plot_type_selector_counter_shelf", index=0)

    # Choose color scale in the sidebar
    color_scale = st.sidebar.selectbox("Select Color Scale:", 
                                       ["Viridis", "Cividis", "Plasma", "Inferno", "Magma"], 
                                       key="color_scale_counter_shelf")

    # Filter the data for the selected store
    store_data_filtered = store_data[store_data['storeName'] == selected_store]

    # Filter for counter shelf product categories
    filtered_counter_shelf = store_data_filtered[store_data_filtered['categoryName'].isin(counter_shelf_categories)]

    # Check if any categories are missing
    missing_categories = set(counter_shelf_categories) - set(filtered_counter_shelf['categoryName'].unique())

    if not filtered_counter_shelf.empty:
        # Calculate total sales, total cost, profit, and profit margin for each category
        counter_shelf_performance = filtered_counter_shelf.groupby('categoryName').agg(
            total_quantity=('quantity', 'sum'),
            total_revenue=('totalProductPrice', 'sum'),
            total_cost=('costPrice', 'sum'),
            total_products=('productId', 'nunique') 
        ).reset_index()

        # Calculate profit and profit margin
        counter_shelf_performance['profit'] = counter_shelf_performance['total_revenue'] - counter_shelf_performance['total_cost']
        counter_shelf_performance['profit_margin'] = (counter_shelf_performance['profit'] / counter_shelf_performance['total_revenue']) * 100

        # Calculate Store's contribution % for each counter shelf product
        total_store_revenue = store_data_filtered['totalProductPrice'].sum()
        counter_shelf_performance['contribution'] = (counter_shelf_performance['total_revenue'] / total_store_revenue) * 100

        # # Calculate total sales for all stores (total sales for all products, not just counter shelf products)
        # total_all_data_revenue = all_data['totalProductPrice'].sum()

        # Filter for counter shelf product categories
        # all_counter_shelf = all_data[all_data['categoryName'].isin(counter_shelf_categories)]

        # all_data_counter_shelf = all_counter_shelf.groupby('categoryName').agg(
        #     total_revenue=('totalProductPrice', 'sum')
        # ).reset_index()

        company_benchmark = pd.read_csv('./company_bechmark/counter_shelf_benchmark.csv')

        counter_shelf_performance = counter_shelf_performance.merge(company_benchmark, on='categoryName', how='left')

        counter_shelf_performance['variance'] = counter_shelf_performance['contribution']-counter_shelf_performance['Company Standard']

        # Determine y-axis based on selected metric
        if metric == "Total Quantity":
            y_axis = 'total_quantity'
        elif metric == "Total Revenue":
            y_axis = 'total_revenue'
        elif metric == "Profit":
            y_axis = 'profit'
        elif metric == "Profit Margin":
            y_axis = 'profit_margin'

        # Generate the appropriate plot based on user selection
        if plot_type == "Bar":
            fig_counter_shelf = px.bar(
                counter_shelf_performance,
                x='categoryName',
                y=y_axis,
                title=f'Counter Shelf Products Performance by {metric}',
                labels={y_axis: metric, 'categoryName': 'Counter Shelf Category'},
                color=y_axis,
                color_continuous_scale=color_scale
            )
            # Add data labels for bar plot
            if show_data_labels:
                fig_counter_shelf.update_traces(text=counter_shelf_performance[y_axis], textposition='outside')

        elif plot_type == "Scatter":
            fig_counter_shelf = px.scatter(
                counter_shelf_performance,
                x='categoryName',
                y=y_axis,
                title=f'Counter Shelf Products Performance by {metric}',
                labels={y_axis: metric, 'categoryName': 'Counter Shelf Category'},
                color=y_axis,
                color_continuous_scale=color_scale,
                size=y_axis
            )
            # Add data labels for scatter plot
            if show_data_labels:
                fig_counter_shelf.update_traces(text=counter_shelf_performance[y_axis], textposition='top center')

        elif plot_type == "Pie":
            fig_counter_shelf = px.pie(
                counter_shelf_performance,
                names='categoryName',
                values=y_axis,
                title=f'Counter Shelf Products Performance by {metric}',
                color_discrete_sequence=px.colors.sequential.__dict__[color_scale],
                hole=0.3  # Optional: create a donut chart
            )
            # Add data labels for pie chart, position them outside for small slices
            if show_data_labels:
                fig_counter_shelf.update_traces(textinfo='label+percent', textposition='outside')

        # Increase the size of the plot
        fig_counter_shelf.update_layout(width=1000, height=700)

        # Display the plot and DataFrame for Counter Shelf Products Analysis
        st.plotly_chart(fig_counter_shelf)

        # Format profit margin and contribution % as a percentage with the '%' symbol
        counter_shelf_performance['profit_margin'] = counter_shelf_performance['profit_margin'].map(lambda x: f"{x:.2f}%")
        counter_shelf_performance['contribution'] = counter_shelf_performance['contribution'].map(lambda x: f"{x:.2f}%")
        counter_shelf_performance['Company Standard'] = counter_shelf_performance['Company Standard'].map(lambda x: f"{x:.2f}%")
        counter_shelf_performance['variance'] = counter_shelf_performance['variance'].map(lambda x: f"{x:.2f}%")
        counter_shelf_performance['total_revenue'] = counter_shelf_performance['total_revenue'].apply(lambda x: f"{x:.2f}")
        counter_shelf_performance['total_cost'] = counter_shelf_performance['total_cost'].apply(lambda x: f"{x:.2f}")
        counter_shelf_performance['profit'] = counter_shelf_performance['profit'].apply(lambda x: f"{x:.2f}")

        # Conditional formatting for negative variance (highlight in red)
        def highlight_negative(s):
            return ['background-color: red' if float(val.replace('%', '')) < 0 else '' for val in s]

        to_display = counter_shelf_performance[['categoryName', 'total_revenue', 'total_cost', 'profit','contribution','Company Standard','variance']]

        # Apply conditional formatting to 'variance' column
        styled_df = to_display.style.apply(highlight_negative, subset=['variance'])

        # Display the updated DataFrame with the conditional formatting
        st.table(styled_df)

        # Prepare the data for plotting and format percentages
        melted_df = counter_shelf_performance.melt(
            id_vars='categoryName', 
            value_vars=['contribution', 'Company Standard'], 
            var_name='Metric', 
            value_name='Percentage'
        )

        # Convert percentage values to float and add percentage symbol for data labels
        melted_df['Percentage'] = melted_df['Percentage'].apply(lambda x: float(x.replace('%', '')))
        melted_df['Percentage_label'] = melted_df['Percentage'].apply(lambda x: f'{x:.2f}%')

        # Plot comparing 'contribution' and 'Company Standard'
        fig_comparison = px.bar(
            melted_df,
            x='categoryName',
            y='Percentage',
            color='Metric',
            barmode='group',
            title="Comparison of Contribution and Company Standard by Category",
            labels={'Percentage': 'Percentage (%)', 'categoryName': 'Counter Shelf Category'},
            text='Percentage_label'  # Use the formatted percentage as text
        )

        # Adjust the size of the plot to 1000x600
        fig_comparison.update_layout(width=1000, height=600)

        # Display the comparison plot
        st.plotly_chart(fig_comparison)


    else:
        st.warning("No data available for the selected categories.")
    
    if missing_categories:
        st.info("Missing categories in the dataset:")
        st.write(missing_categories)

    st.markdown("<h4 style='color: green; text-align: center; margin-top: 0px;'>Recommendations</h4>", unsafe_allow_html=True)

        # Default recommendations
    default_recommendations = (
            "- You’re doing good as per counter shelf products, keep it up!\n"
            "- Gather feedback from customers to understand their preferences and reasons for not purchasing these brands.\n"
            "- Use attractive signage to draw attention to these brands.\n"
        )

        # Custom CSS to enlarge the text area font size
    st.markdown(
            """
            <style>
            .recommendations-textarea textarea {
                font-size: 16px !important; /* Adjust the font size here */
                line-height: 1.5 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
    )

        # Text area with larger font size
    feedback = st.text_area(
            "",
            default_recommendations,
            key="recommendations_input_counter",
            placeholder="Write your recommendations here...",
            label_visibility="visible",
            help="Write your suggestions or adjustments related to sales categories."
        )

        # Wrap the text area with a custom class for applying styles
    st.markdown('<div class="recommendations-textarea"></div>', unsafe_allow_html=True)
