import pandas as pd
import streamlit as st

def format_currency(value):
    """Format the value as currency in Rupees with commas."""
    return f"₹{value:,.2f}"

def calculate_profits(data, selected_store, start_date, end_date):

    st.markdown("<h4 style='color: green; text-align: center;'>Profit KPI</h4>", unsafe_allow_html=True)

    # Calculate profit per store
    store_profit = data.groupby('storeName').apply(lambda x: (x['totalProductPrice'] - x['costPrice']).sum()).reset_index()
    store_profit.columns = ['storeName', 'profit']

    # Calculate overall profit
    overall_profit = store_profit['profit'].sum()

    # Calculate date range in days
    date_range_days = (end_date - start_date).days + 1  # Adding 1 to include the end date

    # Calculate overall average profit using the new formula
    overall_average_profit = 42358 * date_range_days * 0.3

    # Calculate store average profit
    store_average_profit = store_profit.loc[store_profit['storeName'] == selected_store, 'profit'].values[0] / len(store_profit)

    # Calculate store performance as overall profit
    store_performance = overall_profit
    
    # Calculate store revenue for the selected store
    store_revenue = data[data['storeName'] == selected_store]['totalProductPrice'].sum()

    # Calculate profit contribution percentage using the new formula
    store_profit_value = store_profit.loc[store_profit['storeName'] == selected_store, 'profit'].values[0]
    profit_contribution_percentage = (store_profit_value / store_revenue * 100) if store_revenue > 0 else 0

    # Prepare the results as a dictionary
    results = {
        'selected_store_profit': store_profit_value,
        'overall_average_profit': overall_average_profit,
        'selected_store_average_profit': store_average_profit,
        'profit_contribution_percentage': profit_contribution_percentage
    }

    return results

def display_profit_metrics(data, selected_store, start_date, end_date):
    # Calculate profits
    profits = calculate_profits(data, selected_store, start_date, end_date)

    # Create three equal columns
    col1, col2, col3 = st.columns(3, gap="large")

    # Custom CSS for perfect alignment and conditional formatting
    custom_metric_style = """
           <style>
            [data-testid="metric-container"] {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                margin: 0 auto;
                padding: 0;
            }
            [data-testid="stMetricValue"] {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            [data-testid="stMetricLabel"] {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .negative {
                color: rgb(255, 43, 43) !important;
            }
            .positive {
                color: rgb(9, 171, 59) !important;
            }
        </style>
    """
    st.markdown(custom_metric_style, unsafe_allow_html=True)

    # Store Profit in col1
    with col1:
        st.metric(
            "Store Profit",
            format_currency(profits['selected_store_profit'])
        )

    # Overall Average Profit in col2
    with col2:
        st.metric(
            "Overall Average Profit",
            format_currency(profits['overall_average_profit'])
        )

    # Profit Contribution Percentage in col3 with conditional formatting
    with col3:
        profit_percentage = profits['profit_contribution_percentage']
        st.metric(
            "Contribution to total Profit",
            f"{profit_percentage:.2f}%"
        )
    
    # Return the profits dictionary
    return profits
