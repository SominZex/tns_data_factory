import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def grn_analysis(sales_data, stock_data, selected_store):
    """
    Analyze GRN (Goods Receipt Note) data by comparing sales and stock data.
    
    Parameters:
    sales_data (pd.DataFrame): DataFrame containing sales data
    stock_data (pd.DataFrame): DataFrame containing stock data
    selected_store (str): Name of the selected store
    """
    if stock_data is None:
        st.warning("Please upload stock data to perform GRN analysis.")
        return
    
    try:
        # Filter data for selected store
        store_sales_data = sales_data[sales_data['storeName'] == selected_store].copy()
        store_stock_data = stock_data[stock_data['storeName'] == selected_store].copy()
        
        # Ensure proper data types
        store_sales_data['productId'] = store_sales_data['productId'].astype(str)
        store_stock_data['productId'] = store_stock_data['productId'].astype(str)
        
        # Merge sales and stock data
        merged_data = pd.merge(
            store_sales_data,
            store_stock_data,
            on=['productId', 'storeName'],
            how='outer',
            suffixes=('_sales', '_stock')
        )
        
        # Handle None/NaN values
        merged_data['quantity_sales'] = merged_data['quantity_sales'].fillna(0)
        merged_data['quantity_stock'] = merged_data['quantity_stock'].fillna(0)
        merged_data['productName_sales'] = merged_data['productName_sales'].fillna(
            merged_data['productName_stock']
        )
        merged_data['productName_stock'] = merged_data['productName_stock'].fillna(
            merged_data['productName_sales']
        )
        
        # Calculate discrepancies
        merged_data['discrepancy'] = merged_data['quantity_stock'] - merged_data['quantity_sales']
        
        # Display analysis results
        st.subheader("GRN Analysis Results")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Products", len(merged_data))
        with col2:
            st.metric("Products with Discrepancies", 
                     len(merged_data[merged_data['discrepancy'] != 0]))
        with col3:
            accuracy_rate = (len(merged_data[merged_data['discrepancy'] == 0]) / 
                           len(merged_data) * 100)
            st.metric("GRN Accuracy Rate", f"{accuracy_rate:.2f}%")
        
        # Detailed analysis
        st.subheader("Detailed GRN Analysis")
        
        # Filter options
        discrepancy_filter = st.selectbox(
            "Filter by Discrepancy Type",
            ["All", "Over-stocked", "Under-stocked", "Matched"]
        )
        
        # Apply filters
        if discrepancy_filter == "Over-stocked":
            filtered_data = merged_data[merged_data['discrepancy'] > 0]
        elif discrepancy_filter == "Under-stocked":
            filtered_data = merged_data[merged_data['discrepancy'] < 0]
        elif discrepancy_filter == "Matched":
            filtered_data = merged_data[merged_data['discrepancy'] == 0]
        else:
            filtered_data = merged_data
        
        # Display detailed table
        if not filtered_data.empty:
            display_columns = [
                'productId', 'productName_sales', 'quantity_sales',
                'quantity_stock', 'discrepancy'
            ]
            
            # Clean up display data
            display_data = filtered_data[display_columns].copy()
            display_data = display_data.replace({None: "N/A"})
            display_data = display_data.sort_values('discrepancy', ascending=False)
            
            st.dataframe(display_data, use_container_width=True)
            
            # Enhanced Visualization
            if len(filtered_data) > 0:
                # Create tabs for different visualizations
                tab1, tab2 = st.tabs(["Discrepancy Analysis", "Stock vs Sales Comparison"])
                
                with tab1:
                    # Prepare data for visualization
                    viz_data = filtered_data.head(10).copy()
                    
                    # Create a more meaningful visualization using a waterfall chart
                    fig = go.Figure(go.Waterfall(
                        name="Discrepancy",
                        orientation="v",
                        measure=["relative"] * len(viz_data),
                        x=viz_data['productName_sales'],
                        y=viz_data['discrepancy'],
                        text=viz_data['discrepancy'].round(2),
                        textposition="outside",
                        connector={"line": {"color": "rgb(63, 63, 63)"}},
                        decreasing={"marker": {"color": "red"}},
                        increasing={"marker": {"color": "green"}},
                        totals={"marker": {"color": "blue"}}
                    ))
                    
                    fig.update_layout(
                        title="Top 10 Products - Stock Discrepancy Analysis",
                        xaxis_title="Product Name",
                        yaxis_title="Quantity Discrepancy",
                        showlegend=False,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    # Create a comparison bar chart
                    comparison_fig = go.Figure()
                    
                    comparison_fig.add_trace(go.Bar(
                        name='Stock Quantity',
                        x=viz_data['productName_sales'],
                        y=viz_data['quantity_stock'],
                        marker_color='rgb(55, 83, 109)'
                    ))
                    
                    comparison_fig.add_trace(go.Bar(
                        name='Sales Quantity',
                        x=viz_data['productName_sales'],
                        y=viz_data['quantity_sales'],
                        marker_color='rgb(26, 118, 255)'
                    ))
                    
                    comparison_fig.update_layout(
                        title='Stock vs Sales Quantity Comparison (Top 10 Products)',
                        xaxis_tickangle=-45,
                        xaxis_title="Product Name",
                        yaxis_title="Quantity",
                        barmode='group',
                        bargap=0.15,
                        bargroupgap=0.1
                    )
                    
                    st.plotly_chart(comparison_fig, use_container_width=True)
        else:
            st.info("No data available for the selected filter.")
        
    except Exception as e:
        st.error(f"An error occurred during GRN analysis: {str(e)}")
        st.write("Please ensure your data contains the required columns and proper format.")

def upload_stock_data():
    """Upload and validate stock data file"""
    stock_file = st.file_uploader("Upload Stock CSV file (for GRN Analysis)", type="csv")
    
    if stock_file is not None:
        try:
            stock_data = pd.read_csv(stock_file)
            required_columns = ['productId', 'storeName', 'quantity']
            
            # Validate required columns
            if not all(col in stock_data.columns for col in required_columns):
                st.error("Stock data must contain: productId, storeName, and quantity columns")
                return None
                
            return stock_data
            
        except Exception as e:
            st.error(f"Error processing stock data: {str(e)}")
            return None
            
    return None