import streamlit as st
import pandas as pd
from sales_by_category import sales_by_category_analysis
from time_slot_analysis import time_slot_analysis
from sales_per_channel import sales_per_channel_analysis
from top_n_brand_sales import top_n_brand_sales_analysis
from brand_availability import top_n_brand_availability_analysis
from top_n_products import top_n_product_analysis
from top_n_product_availability import top_n_product_availability_analysis
from fnb_performance import fnb_performance_analysis
from monetized_brands import analyze_monetized_brands
from counter_shelf_analysis import analyze_counter_shelf_products
from low_performing_brand import low_performing_brand_analysis
from low_performing_products import low_performing_product_analysis
from profit import display_profit_metrics


from pptx import Presentation
from pptx.util import Inches
import numpy as np
from weasyprint import HTML
import base64
import os
import io

# Set page configuration
st.set_page_config(page_title="TNS DataFactory", page_icon=":bar_chart:", layout="wide")

st.markdown("""
    <style>
    /* General web layout */
    .stApp {
        max-width: 70%; /* Use full available width for web */
        margin-left: auto;
        margin-right: auto;
        padding: 10px; /* Padding for better visuals */
        background-color: white;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); /* Subtle shadow */
    }

    /* Center the page title */
    h1 {
        text-align: center;
        color: #2e7d32; /* Dark green color */
    }

    /* Style the metrics and other boxed elements */
    .metrics-box {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f0f4f8;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Strong emphasis text style */
    .metrics-box p {
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        line-height: 1.5;
        margin: 5px 0;
    }

    /* Style for RAG analysis (Red, Amber, Green) */
    .rag-red {
        background-color: red;
        color: white;
        font-weight: bold;
        padding: 5px;
        border-radius: 5px;
    }

    .rag-amber {
        background-color: orange;
        color: white;
        font-weight: bold;
        padding: 5px;
        border-radius: 5px;
    }

    .rag-green {
        background-color: green;
        color: white;
        font-weight: bold;
        padding: 5px;
        border-radius: 5px;
    }

    /* A4-specific styling for printing */
    @media print {
        @page {
            size: A4; /* A4 size page */
            margin: 4mm; /* Adjust as needed for print */
        }

        body {
            width: 210mm;  /* A4 width */
            height: 297mm; /* A4 height */
            margin: 0 auto;
            -webkit-print-color-adjust: exact !important; /* Ensure colors are printed accurately */
            color-adjust: exact !important;
        }

        /* Constrain the app to A4 width in print view */
        .stApp {
            max-width: 210mm; /* Limit to A4 width */
            margin: 0 auto; /* Center content on the page */
            padding: 10mm; /* Ensure proper padding for print */
        }

        .metrics-box {
            page-break-inside: avoid;
        }

        /* RAG color preservation during print */
        .rag-red {
            background-color: red !important;
            color: white !important;
        }

        .rag-amber {
            background-color: orange !important;
            color: white !important;
        }

        .rag-green {
            background-color: green !important;
            color: white !important;
        }

        /* Hide unnecessary elements for printing */
        .back-to-top {
            display: none !important;
        }
        
            .back-to-top {
            position: fixed;
            bottom: 20px; /* Position from the bottom */
            right: 20px; /* Position from the right */
            background-color: #2e7d32; /* Dark green color */
            color: white; /* Text color */
            border: none;
            border-radius: 5px;
            padding: 10px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            display: none; /* Hidden by default */
        }

        /* Show the button when scrolling down */
        body.scroll .back-to-top {
            display: block;
        }

    </style>
""", unsafe_allow_html=True)


# Title
# st.markdown("<h1>🏭 TNS Data Factory (WIP)</h1>", unsafe_allow_html=True)



if 'data' not in st.session_state:
    st.session_state.data = None
if 'show_uploader' not in st.session_state:
    st.session_state.show_uploader = True

# File uploader
if st.session_state.show_uploader:
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    if uploaded_file is not None:
        # Load the uploaded data
        st.session_state.data = pd.read_csv(uploaded_file)
        st.session_state.data['orderDate'] = pd.to_datetime(st.session_state.data['orderDate'], format='%d-%m-%Y')
        st.session_state.show_uploader = False 

# Toggle button to show/hide the uploader
if st.button("^"):
    st.session_state.show_uploader = not st.session_state.show_uploader

# Proceed only if data is loaded
if st.session_state.data is not None:
    data = st.session_state.data

    # Move selectors and inputs to sidebar
    with st.sidebar:
        st.markdown("### Selectors Menu")
        
        # Store selection
        store_names = data['storeName'].unique()
        selected_store = st.selectbox("Select a Store:", store_names, key="store_selector")

        # Date range selection
        start_date = st.date_input("Select Start Date:", value=data['orderDate'].min().date(),
                                   min_value=data['orderDate'].min().date(),
                                   max_value=data['orderDate'].max().date())
        end_date = st.date_input("Select End Date:", value=data['orderDate'].max().date(),
                                 min_value=data['orderDate'].min().date(),
                                 max_value=data['orderDate'].max().date())

    st.markdown(f"""
    <style>
    .fixed-store-name {{
        position: fixed;
        top: 26px;
        left: 0;
        width: 100%;
        color: green;
        font-size: 28px;
        font-weight: bold;
        padding: 10px;
        z-index: 1000;
        text-align: center;
        border-bottom: 1px solid #ccc;
        background-color: white;
    }}

    .main {{
        padding-top: 60px;
    }}
    </style>
    <div class="fixed-store-name">{selected_store}</div>
    """, unsafe_allow_html=True)

  
    # Convert start_date and end_date to datetime64[ns] for comparison
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on selected store and date range
    store_data = data[(data['storeName'] == selected_store) & 
                      (data['orderDate'] >= start_date) & 
                      (data['orderDate'] <= end_date)]

    # Filter for available stock using the quantity column
    store_data_filtered = store_data[store_data['quantity'] > 0]

    # Calculate the total number of unique stores for overall data
    overall_unique_store_count = data['storeName'].nunique()

    # Define the performance rating function based on the logic you provided
    def performance_rating(avg_price, overall_average):
        if avg_price > overall_average * 1.2:
            return 'Excellent'
        elif avg_price > overall_average:
            return 'Good'
        elif avg_price == overall_average:
            return 'Average'
        elif avg_price >= overall_average * 0.8:
            return 'Below Average'
        else:
            return 'Poor'
      
    selected_store_total_revenue = store_data['totalProductPrice'].sum()

    overall_data_filtered = data[(data['orderDate'] >= start_date) & 
                              (data['orderDate'] <= end_date)]


    # Calculate total revenue for all stores
    overall_total_revenue = overall_data_filtered['totalProductPrice'].sum()

    if len(overall_data_filtered) > 0:
        overall_avg_sales = overall_total_revenue / overall_unique_store_count
    else:
        overall_avg_sales = 0

    if len(store_data) > 0:
        selected_store_avg_sales = selected_store_total_revenue / len(store_data)
    else:
        selected_store_avg_sales = 0


    # Calculate the percentage difference from the overall average
    avg_difference_percentage = ((selected_store_avg_sales - overall_avg_sales) / overall_avg_sales) * 100 if overall_avg_sales > 0 else 0

    # Create a DataFrame for store performance
    store_performance = pd.DataFrame({
        'storeName': [selected_store],
        'averageTotalProductPrice': [selected_store_avg_sales],
        'totalRevenue': [selected_store_total_revenue],
        'percentageDifference': [avg_difference_percentage],
        'overallAverage': [overall_avg_sales],
        'overallRevenue': [overall_total_revenue]
    })

    if overall_total_revenue > 0:
        selected_store_percentage_contribution = (selected_store_total_revenue / overall_total_revenue) * 100
    else:
        selected_store_percentage_contribution = 0

    store_performance['performanceRating'] = store_performance['averageTotalProductPrice'].apply(performance_rating, overall_average=overall_avg_sales)
    # Create KPI Cards for key metrics
    st.markdown(f"<h2 style='color: green; text-align: center;'>Overall Store KPI: {selected_store}</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<h4 style='color: green; text-align: center;'>{start_date.date()} to {end_date.date()}</h4>",
        unsafe_allow_html=True
    )
    # Function to display metrics with conditional formatting
    def display_metric(column, label, value, percentage_difference):
        column.metric(label, value)
        # Conditional formatting for delta text
        if percentage_difference > 0:
            delta_text = f'<span style="color: green;">+{percentage_difference:.2f}%</span>'
        elif percentage_difference < 0:
            delta_text = f'<span style="color: red;">{percentage_difference:.2f}%</span>'
        else:
            delta_text = f'<span style="color: grey;">{percentage_difference:.2f}%</span>'
        column.markdown(delta_text, unsafe_allow_html=True)

    # Display KPIs as cards
    col1, col2, col3 = st.columns([1, 1, 1], gap="large")

    # Total Revenue
    col1.metric("Store Revenue", f"₹{store_performance['totalRevenue'].values[0]:,.2f}")

    # Calculate the percentage difference between overall average sales and store total revenue
    total_revenue_difference_percentage = ((selected_store_total_revenue - overall_avg_sales) / overall_avg_sales) * 100

    # Display the percentage difference right below Store Revenue
    col1.markdown(f"<span style='color: {'green' if total_revenue_difference_percentage >= 0 else 'red'};'>{total_revenue_difference_percentage:.2f}%</span>", unsafe_allow_html=True)

    # Percentage Contribution to Total Revenue
    col2.metric("% Contribution to Total Revenue", f"{selected_store_percentage_contribution:.2f}%", delta_color="normal")

    # Overall Average Sales
    col3.metric("Overall Average Sales", f"₹{overall_avg_sales:,.2f}")


    
    selected_store_data = data[data['storeName'] == selected_store]


    # Run all analyses and capture the relevant DataFrames for the report


    all_data = data.copy()
    sales_by_category_analysis(store_data, all_data)


    time_slot_analysis(store_data, all_data)

    sales_per_channel_analysis(store_data, data)

    top_n_brand_df = top_n_brand_sales_analysis(store_data, all_data)
    #top_n_brand_availability_analysis(store_data_filtered)
    top_n_product_analysis(store_data, all_data)
    #top_n_product_availability_analysis(store_data_filtered)
    fnb_performance_analysis(store_data, all_data)
    analyze_monetized_brands(store_data, all_data)
    analyze_counter_shelf_products(store_data, all_data)
    low_performing_brand_analysis(store_data)
    low_performing_product_analysis(store_data)

    def create_html_report():
        html_content = f"""
        <html>
        <head>
            <title>TNS Data Factory Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1, h2 {{ color: #2e7d32; text-align: center; }}
                .kpi-container {{ display: flex; justify-content: space-around; flex-wrap: wrap; }}
                .kpi-card {{ border: 1px solid #ccc; border-radius: 10px; padding: 10px; width: 200px; text-align: center; margin: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                img {{ max-width: 100%; height: auto; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h1>TNS Data Factory Report</h1>
            <h2>Store: {selected_store}</h2>
            <p style="text-align: center;">Date Range: {start_date.date()} - {end_date.date()}</p>
            
            <h2>Overall Store KPI</h2>
            <div class="kpi-container">
                <div class="kpi-card">
                    <h3>Store Revenue</h3>
                    <p>₹{store_performance['totalRevenue'].values[0]:,.2f}</p>
                </div>
                <div class="kpi-card">
                    <h3>% Contribution to Total Revenue</h3>
                    <p>{selected_store_percentage_contribution:.2f}%</p>
                </div>
                <div class="kpi-card">
                    <h3>Overall Average Sales</h3>
                    <p>₹{overall_avg_sales:,.2f}</p>
                </div>
            </div>

            <h2>Sales by Category Analysis</h2>

            
            <h2>Top N Brand Sales Analysis</h2>

            
            <h2>Top N Brand Availability Analysis</h2>

            
            <h2>Top N Product Analysis</h2>


            <h2>Top N Product Availability Analysis</h2>

            
            <h2>F&B Performance Analysis</h2>

            

            <h2>Monetized Brands Analysis</h2>

            

            <h2>Counter Shelf Products Analysis</h2>

            

            <h2>Low Performing Brand Analysis</h2>

            

            <h2>Low Performing Product Analysis</h2>

            

            <h2>Profit Metrics</h2>

            
        </body>
        </html>
        """
        return html_content

    # Function f generate PDF reprot
    def generate_pdf_report():
        html_content = create_html_report()
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        return pdf_file

    # Button genrate PDF report
    if st.button("Generate PDF Report"):
        pdf = generate_pdf_report()
        st.download_button(
            label="Download PDF Report",
            data=pdf,
            file_name="TNS_Data_Factory_Report.pdf",
            mime="application/pdf"
        )

st.markdown("<footer><p style='text-align:center;'>TNS Data Factory © 2024</p></footer>", unsafe_allow_html=True)

