import streamlit as st
import sys
import os

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reports import generate_analytics_report
from datetime import datetime
import pandas as pd

class StreamlitApp:
    def __init__(self):
        st.set_page_config(layout="wide", page_title="Sales Analytics Dashboard")
        self.websites = ["jumia"]

    def run(self):
        st.title("Sales Analytics Dashboard")

        # --- Sidebar for Inputs ---
        with st.sidebar:
            st.header("Report Parameters")
            website = st.selectbox("Select Website", self.websites)
            
            today = datetime.now()
            date = st.date_input("Select Date", today)
            date_str = date.strftime("%Y-%m-%d")

            # The button click state is captured here
            generate_clicked = st.button("Generate Report", type="primary")

        # --- Main Page for Content ---
        if generate_clicked:
            # The report display is now called outside the sidebar block
            self.generate_and_display_report(website, date_str)
        else:
            st.info("Select parameters and click 'Generate Report' to view the analytics.", icon="ℹ️")


    def _display_professional_summary(self, summary_text):
        """Parses the raw summary text and displays it in a professional format."""
        st.header("📊 Report Summary")

        lines = [line.strip() for line in summary_text.strip().split('\n')]
        
        # Extract basic info
        website = next((l.split(': ')[1] for l in lines if 'Website:' in l), 'N/A')
        date = next((l.split(': ')[1] for l in lines if 'Date:' in l), 'N/A')
        
        col1, col2 = st.columns(2)
        col1.markdown(f"**Website:** `{website}`")
        col2.markdown(f"**Date:** `{date}`")
        st.divider()

        # Extract metrics using a helper function
        def get_metric(key, unit=''):
            val = next((l.split(': ')[1] for l in lines if key in l), 'N/A')
            if unit:
                val = val.replace(unit, '').strip()
            return val

        # --- SUMMARY STATISTICS ---
        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Products", get_metric('Total Products Scraped'))
        col2.metric("Unique Categories", get_metric('Unique Categories'))
        col3.metric("Average Price", f"{get_metric('Average Price', 'EGP')} EGP")
        st.divider()

        # --- DISCOUNT INSIGHTS ---
        st.subheader("Discount Insights")
        col1, col2 = st.columns(2)
        col1.metric("Products with Discounts", get_metric('Products with Discounts'))
        col2.metric("Average Discount", f"{get_metric('Average Discount', '%')}%")
        st.divider()
        
        # --- RATING & REVIEWS ---
        st.subheader("Rating & Reviews")
        col1, col2, col3 = st.columns(3)
        col1.metric("Products with Ratings", get_metric('Products with Ratings'))
        col2.metric("Average Rating", get_metric('Average Rating'))
        col3.metric("Total Reviews", get_metric('Total Reviews'))
        st.divider()

        # --- STORE BREAKDOWN ---
        st.subheader("Store Breakdown")
        col1, col2 = st.columns(2)
        col1.metric("Official Store Products", get_metric('Official Store Products'))
        col2.metric("Non-Official Store Products", get_metric('Non-Official Store Products'))
        st.divider()

        # --- GENERATED FILES ---
        with st.expander("📂 View Generated Files and Location"):
            try:
                files_section = summary_text.split("GENERATED FILES")[1]
                st.code(files_section.strip())
            except IndexError:
                st.warning("Could not parse the generated files list.")

    def generate_and_display_report(self, website, date):
        try:
            with st.spinner(f"⏳ Generating report for {website} on {date}..."):
                summary_text, _, reports_data = generate_analytics_report(website=website, date=date)
            
            st.success("✅ Report generated successfully!")

            # Display the enhanced summary
            self._display_professional_summary(summary_text)

            st.header("🔍 Detailed Analysis")
            st.info("Explore the detailed data and charts for each report section below.")

            tab_names = [name.replace('_', ' ').title() for name in reports_data.keys()]
            tabs = st.tabs(tab_names)

            for i, (report_name, df) in enumerate(reports_data.items()):
                with tabs[i]:
                    st.subheader(f"{report_name.replace('_', ' ').title()}")
                    
                    if df.empty:
                        st.warning("No data available for this section.")
                        continue

                    st.dataframe(df)

                    # Add some simple, interactive charts
                    if report_name == 'category_statistics' and not df.empty:
                        st.subheader("Top 10 Categories by Product Count")
                        chart_data = df.head(10).set_index('category')['product_count']
                        st.bar_chart(chart_data)

                    elif report_name == 'price_distribution_analysis' and not df.empty:
                        st.subheader("Price Statistics")
                        chart_data = df.set_index('Metric')['Value']
                        st.line_chart(chart_data)
                    
                    elif report_name == 'discount_analysis' and not df.empty:
                        st.subheader("Top 15 Products by Discount")
                        chart_data = df.head(15).set_index('name')['discount']
                        st.bar_chart(chart_data)

                    elif report_name == 'rating_analysis' and not df.empty:
                        st.subheader("Product Count by Rating")
                        # FIX: Convert pandas Interval objects to strings for charting
                        df_chartable = df.copy()
                        df_chartable['rating'] = df_chartable['rating'].astype(str)
                        chart_data = df_chartable.set_index('rating')['product_count']
                        st.bar_chart(chart_data)

        except ValueError as e:
            st.error(f"❌ Validation Error: {e}")
            st.warning("""
                Please check that:
                - Data exists for the selected date.
                - The database is running and accessible.
            """)
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")
            st.exception(e)


if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
