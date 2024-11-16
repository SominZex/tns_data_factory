import pandas as pd
import streamlit as st
import plotly.express as px

def low_performing_brand_analysis(store_data):
    st.markdown("<h4 style='color: green; text-align: center;'>Revenue VS Low performing Brands</h4>", unsafe_allow_html=True)
    st.markdown("---")

    # Group the data by brandName to calculate product count, total sales, total cost, profit, and profit margin
    low_performing_brands = store_data.groupby('brandName').agg(
        product_count=('productId', 'nunique'),
        quantity_sold=('quantity', 'sum'),
        total_revenue=('totalProductPrice', 'sum'), 
        total_cost=('costPrice', 'sum') 
    ).reset_index()

    # Calculate profit and profit margin
    low_performing_brands['profit'] = low_performing_brands['total_revenue'] - low_performing_brands['total_cost']
    low_performing_brands['profit_margin'] = (low_performing_brands['profit'] / low_performing_brands['total_revenue']) * 100

    # Format profit margin as a percentage with the '%' symbol
    low_performing_brands['profit_margin'] = low_performing_brands['profit_margin'].map(lambda x: f"{x:.2f}%")

    # Sort the brands by quantity sold in ascending order for analysis
    low_performing_brands = low_performing_brands.sort_values(by='quantity_sold')

    # Check if there are any brands in the analysis
    if not low_performing_brands.empty:
        # Move the controls to the sidebar
        st.sidebar.markdown("## Filter Options for low performing brands")
        
        # for idx, row in low_performing_brands.iterrows():
        #     unique_key = f"data_labl_k_{idx}_{row['brandName']}"
        #     show_data_labels = st.sidebar.checkbox(f"Show Data Labels for {row['brandName']}", key=unique_key)

        # Choose color scale
        color_scale_low = st.sidebar.selectbox("Select Color Scale for Low sale brands:", 
                                           options=['Viridis', 'Cividis', 'Plasma', 'Blues'], 
                                           index=2, key = "low_performing_color_brands")

        # Choose plot type
        plot_type_low = st.sidebar.selectbox("Select Plot Type for low sales brands:", 
                                         options=['Bar Plot', 'Line Plot'], 
                                         index=0, key = "low_performing_brands_plot")

        # Plot Quantity Sold
        # if plot_type == 'Bar Plot':
        #     fig_quantity_sold = px.bar(
        #         low_performing_brands,
        #         x='brandName',
        #         y='quantity_sold',
        #         title='Quantity Sold by Low Performing Brands',
        #         labels={'quantity_sold': 'Quantity Sold', 'brandName': 'Brand'},
        #         color='quantity_sold',
        #         color_continuous_scale=color_scale
        #     )
        # else:  # Line Plot
        #     fig_quantity_sold = px.line(
        #         low_performing_brands,
        #         x='brandName',
        #         y='quantity_sold',
        #         title='Quantity Sold by Low Performing Brands',
        #         labels={'quantity_sold': 'Quantity Sold', 'brandName': 'Brand'},
        #         markers=True
        #     )

        # Add data labels for quantity sold plot
        # if show_data_labels:
        #     text_position = 'outside' if plot_type == 'Bar Plot' else 'top left'
        #     fig_quantity_sold.update_traces(text=low_performing_brands['quantity_sold'], textposition=text_position)

        # # Set the size of the Quantity Sold plot
        # fig_quantity_sold.update_layout(width=1000, height=600)
        # # Display the Quantity Sold plot
        # st.plotly_chart(fig_quantity_sold)

        # Sort low_performing_brands by total revenue for the revenue plot
        low_performing_brands_sorted_by_revenue = low_performing_brands.sort_values(by='total_revenue')

        # Plot Total Revenue
        if plot_type_low == 'Bar Plot':
            fig_total_revenue = px.bar(
                low_performing_brands_sorted_by_revenue,
                x='brandName',
                y='total_revenue',
                title='Total Revenue by Low Performing Brands',
                labels={'total_revenue': 'Total Revenue', 'brandName': 'Brand'},
                color='total_revenue',
                color_continuous_scale=color_scale_low
            )
        else:  # Line Plot
            fig_total_revenue = px.line(
                low_performing_brands_sorted_by_revenue,
                x='brandName',
                y='total_revenue',
                title='Total Revenue by Low Performing Brands',
                labels={'total_revenue': 'Total Revenue', 'brandName': 'Brand'},
                markers=True
            )

        # # Add data labels for total revenue plot
        # if show_data_labels:
        #     text_position = 'outside' if plot_type == 'Bar Plot' else 'top left'
        #     fig_total_revenue.update_traces(text=low_performing_brands_sorted_by_revenue['total_revenue'], textposition=text_position)

        # Set the size of the Total Revenue plot
        fig_total_revenue.update_layout(width=1100, height=400)
        # Display the Total Revenue plot
        st.plotly_chart(fig_total_revenue)
        
    else:
        st.warning("No low performing brands found in the selected store.")


    low_performing_brands['total_revenue'] = low_performing_brands['total_revenue'].apply(lambda x: f"{x:.2f}")
    low_performing_brands['total_cost'] = low_performing_brands['total_cost'].apply(lambda x: f"{x:.2f}")

    # Display the low performing brands in a table
    # st.markdown(
    #     "<h2 style='color: green; text-align: center;'>Low performing Brands sorted by QTY.</h2>", 
    #     unsafe_allow_html=True
    # )  
    #st.table(low_performing_brands[['brandName', 'product_count', 'quantity_sold', 'total_revenue', 'total_cost', 'profit', 'profit_margin']])

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_brands = convert_df(low_performing_brands)

    st.sidebar.download_button(
            label="Download low performing brands Data",
            data=csv_brands,   
            file_name='low_performing_brands.csv',
            mime='text/csv',
        )