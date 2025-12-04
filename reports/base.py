"""
Comprehensive Sales Analytics Report Generator
Combines data loading, validation, and report generation with visualizations.
"""

import logging
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from load.load_postgres import PostgresLoader
import numpy as np
from reports import PlotHelper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class AnalyticsReportGenerator:
    """
    Comprehensive analytics report generator with visualizations and CSV exports.
    Handles data loading, validation, and report generation in one place.
    """
    
    SAVE_LOCATION = "data/reports/"
    AVAILABLE_WEBSITES = ["jumia"]
    
    def __init__(self, website, date):
        """
        Initialize the report generator.
        
        Args:
            website (str): Website name (e.g., 'jumia')
            date (str): Date in YYYY-MM-DD format
        """
        self.website = website
        self.date = date
        self.loader = PostgresLoader()
        self.data = None
        
        # Create dated folder for reports
        self.report_folder = os.path.join(
            self.SAVE_LOCATION, 
            f"report_{datetime.now().strftime('%Y%m%d')}"
        )
        os.makedirs(self.report_folder, exist_ok=True)
        logger.info(f"Reports will be saved to: {self.report_folder}")
    
    def _validate_website(self):
        """Validate that the website is supported"""
        if self.website not in self.AVAILABLE_WEBSITES:
            raise ValueError(f"Invalid website: {self.website}. Supported: {self.AVAILABLE_WEBSITES}")
    
    def _validate_date(self):
        """
        Validate date and load data from PostgreSQL database.
        Returns True if data exists for the given date.
        """
        try:
            date_obj = datetime.strptime(self.date, "%Y-%m-%d")
            self.data = self.loader.get_data_by_filters(website=self.website, scraped_at=date_obj)
            
            # Convert Decimal columns to float for numpy compatibility
            numeric_columns = ['current_price', 'old_price', 'discount', 'rating', 'review_count']
            for col in numeric_columns:
                if col in self.data.columns:
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
            logger.info(f"Data loaded for website: {self.website} and date: {self.date}")
            logger.info(f"Data loaded: {len(self.data)} rows")
            
            return len(self.data) > 0
            
        except ValueError:
            raise ValueError(f"Invalid date format: {self.date}. Expected YYYY-MM-DD")
        except Exception as e:
            raise ValueError(f"Error loading data: {e}")
    
    def _init_report_generator(self):
        """Initialize and validate the report generator"""
        self._validate_website()
        loaded = self._validate_date()
        if not loaded:
            raise ValueError(f"No data found for {self.website} on {self.date}")
        logger.info("✅ Validation complete. Starting report generation...")
    
    def _save_csv(self, df, filename):
        """Save DataFrame to CSV"""
        filepath = os.path.join(self.report_folder, filename)
        df.to_csv(filepath, index=False, encoding='utf-8')
        logger.info(f"✅ Saved CSV: {filename}")
        return filepath
    
    def _save_plot(self, filename):
        """Save current matplotlib figure"""
        filepath = os.path.join(self.report_folder, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"✅ Saved plot: {filename}")
        return filepath
    

    
    def generate_category_statistics(self):
        """Generate category-level statistics"""
        logger.info("📊 Generating category statistics...")
        
        # Use the category column from database
        category_stats = self.data.groupby('category').agg({
            'sku': 'count',
            'current_price': ['mean', 'min', 'max', 'median'],
            'discount': 'mean',
            'rating': 'mean',
            'review_count': 'sum',
            'is_official_store': lambda x: (x == True).sum()
        }).round(2)
        
        category_stats.columns = [
            'product_count', 
            'avg_price', 'min_price', 'max_price', 'median_price',
            'avg_discount', 'avg_rating', 'total_reviews', 'official_stores'
        ]
        category_stats = category_stats.reset_index()
        category_stats = category_stats.sort_values('product_count', ascending=False)
        
        # Save CSV
        self._save_csv(category_stats, 'category_statistics.csv')
        
        # Create visualization using helper functions
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        top_categories = category_stats.head(10)
        
        # Top 10 categories by product count
        PlotHelper.create_bar(axes[0, 0], top_categories['category'], top_categories['product_count'],
                        'Top 10 Categories by Product Count', 'Number of Products', None,
                        color='steelblue', horizontal=True)
        
        # Average price by category
        PlotHelper.create_bar(axes[0, 1], top_categories['category'], top_categories['avg_price'],
                        'Average Price by Category', 'Average Price (EGP)', None,
                        color='coral', horizontal=True)
        
        # Average discount by category
        PlotHelper.create_bar(axes[1, 0], top_categories['category'], top_categories['avg_discount'],
                        'Average Discount by Category', 'Average Discount (%)', None,
                        color='mediumseagreen', horizontal=True)
        
        # Average rating by category
        PlotHelper.create_bar(axes[1, 1], top_categories['category'], top_categories['avg_rating'],
                        'Average Rating by Category', 'Average Rating', None,
                        color='gold', horizontal=True)
        axes[1, 1].set_xlim(0, 5)
        
        self._save_plot('category_statistics.png')
        
        return category_stats
    
    def generate_top_rated_products(self, limit=50):
        """Generate top-rated products report"""
        logger.info(f"⭐ Generating top {limit} rated products...")
        
        # Filter products with ratings and reviews
        rated_products = self.data[
            (self.data['rating'].notna()) & 
            (self.data['rating'] > 0) &
            (self.data['review_count'] > 0)
        ].copy()
        
        # Calculate a weighted score (rating * log(review_count + 1))
        rated_products['weighted_score'] = (
            rated_products['rating'] * np.log1p(rated_products['review_count'])
        )
        
        # Get top products
        top_products = rated_products.nlargest(limit, 'weighted_score')[[
            'name', 'category', 'current_price', 'old_price', 'discount', 
            'rating', 'review_count', 'weighted_score', 
            'is_official_store', 'url'
        ]].round(2)
        
        # Save CSV
        self._save_csv(top_products, 'top_rated_products.csv')
        
        # Create visualization using helper functions
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Top 20 by rating
        top_20 = top_products.head(20)
        PlotHelper.create_scatter(axes[0], top_20['rating'], top_20['review_count'],
                        'Top 20 Products: Rating vs Review Count\n(Bubble size = Weighted Score)',
                        'Rating', 'Review Count',
                        color='purple', size=top_20['weighted_score']*10)
        
        # Price distribution of top products
        PlotHelper.create_histogram(axes[1], top_products['current_price'].dropna(),
                        'Price Distribution of Top Rated Products',
                        'Price (EGP)', 'Frequency',
                        bins=30, color='teal',
                        vlines={'median': top_products['current_price'].median()})
        
        self._save_plot('top_rated_products.png')
        
        return top_products
    
    def generate_discount_analysis(self):
        """Generate discount analysis report"""
        logger.info("💰 Generating discount analysis...")
        
        # Filter products with discounts
        discounted = self.data[
            (self.data['discount'].notna()) & 
            (self.data['discount'] > 0)
        ].copy()
        
        # Get biggest discounts
        biggest_discounts = discounted.nlargest(100, 'discount')[[
            'name', 'category', 'current_price', 'old_price', 'discount', 
            'rating', 'review_count', 'is_official_store', 'url'
        ]].round(2)
        
        # Save CSV
        self._save_csv(biggest_discounts, 'biggest_discounts.csv')
        
        # Discount statistics by range
        discount_ranges = pd.cut(
            discounted['discount'], 
            bins=[0, 10, 20, 30, 40, 50, 100],
            labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+']
        )
        discount_distribution = discount_ranges.value_counts().sort_index()
        
        # Create visualization using helper functions
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Discount distribution
        PlotHelper.create_bar(axes[0, 0], discount_distribution.index.astype(str), discount_distribution.values,
                        'Distribution of Discounts', 'Discount Range', 'Number of Products',
                        color='crimson')
        
        # Discount vs Price
        sample = discounted.sample(min(1000, len(discounted)))
        PlotHelper.create_scatter(axes[0, 1], sample['current_price'], sample['discount'],
                        'Discount vs Current Price', 'Current Price (EGP)', 'Discount (%)',
                        color='orange', alpha=0.4)
        
        # Top 15 biggest discounts
        top_15_discounts = biggest_discounts.head(15)
        PlotHelper.create_horizontal_bar(axes[1, 0], top_15_discounts['name'], top_15_discounts['discount'],
                        'Top 15 Products by Discount', 'Discount (%)', None,
                        color='darkred')
        
        # Average discount by official store status
        store_discount = discounted.groupby('is_official_store')['discount'].mean()
        PlotHelper.create_bar(axes[1, 1], ['Non-Official', 'Official'], 
                        [store_discount.get(False, 0), store_discount.get(True, 0)],
                        'Average Discount: Official vs Non-Official Stores', None, 'Average Discount (%)',
                        color=['lightcoral', 'darkgreen'])
        
        self._save_plot('discount_analysis.png')
        
        return biggest_discounts
    
    def generate_price_distribution_analysis(self):
        """Generate price distribution analysis"""
        logger.info("💵 Generating price distribution analysis...")
        
        # Price statistics
        price_stats = self.data['current_price'].describe()
        
        # Price ranges
        price_ranges = pd.cut(
            self.data['current_price'].dropna(),
            bins=[0, 100, 500, 1000, 5000, 10000, float('inf')],
            labels=['0-100', '100-500', '500-1K', '1K-5K', '5K-10K', '10K+']
        )
        price_distribution = price_ranges.value_counts().sort_index()
        
        # Save statistics
        stats_df = pd.DataFrame({
            'Metric': ['Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max'],
            'Value': [
                price_stats['count'],
                price_stats['mean'],
                price_stats['std'],
                price_stats['min'],
                price_stats['25%'],
                price_stats['50%'],
                price_stats['75%'],
                price_stats['max']
            ]
        })
        self._save_csv(stats_df, 'price_statistics.csv')
        
        # Create visualization using helper functions
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Price distribution histogram
        PlotHelper.create_histogram(axes[0, 0], self.data['current_price'].dropna(),
                        'Price Distribution (All Products)', 'Price (EGP)', 'Frequency',
                        bins=50, color='navy',
                        vlines={'mean': price_stats['mean'], 'median': price_stats['50%']})
        
        # Price ranges
        PlotHelper.create_bar(axes[0, 1], price_distribution.index.astype(str), price_distribution.values,
                        'Products by Price Range', 'Price Range (EGP)', 'Number of Products',
                        color='teal')
        
        # Box plot
        axes[1, 0].boxplot(self.data['current_price'].dropna(), orientation='horizontal')
        PlotHelper.style_axis(axes[1, 0], 'Price Distribution Box Plot', 'Price (EGP)')
        
        # Log scale histogram for better visibility
        PlotHelper.create_histogram(axes[1, 1], self.data['current_price'].dropna(),
                        'Price Distribution (Log Scale)', 'Price (EGP)', 'Frequency (log scale)',
                        bins=50, color='purple')
        axes[1, 1].set_yscale('log')
        
        self._save_plot('price_distribution.png')
        
        return stats_df
    
    def generate_rating_analysis(self):
        """Generate rating and review analysis"""
        logger.info("⭐ Generating rating analysis...")
        
        # Filter rated products
        rated = self.data[
            (self.data['rating'].notna()) & 
            (self.data['rating'] > 0)
        ].copy()
        
        # Rating statistics
        rating_stats = rated.groupby(pd.cut(rated['rating'], bins=[0, 1, 2, 3, 4, 5]) , observed=True).agg({
            'sku': 'count',
            'review_count': 'sum',
            'current_price': 'mean'
        }).round(2)
        rating_stats.columns = ['product_count', 'total_reviews', 'avg_price']
        rating_stats = rating_stats.reset_index()
        
        self._save_csv(rating_stats, 'rating_statistics.csv')
        
        # Create visualization using helper functions
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Rating distribution
        PlotHelper.create_histogram(axes[0, 0], rated['rating'],
                        'Rating Distribution', 'Rating', 'Number of Products',
                        bins=20, color='gold',
                        vlines={'mean': rated['rating'].mean()})
        
        # Review count distribution (log scale)
        PlotHelper.create_histogram(axes[0, 1], rated['review_count'].dropna(),
                        'Review Count Distribution', 'Review Count', 'Number of Products',
                        bins=50, color='skyblue')
        axes[0, 1].set_yscale('log')
        
        # Rating vs Review Count
        PlotHelper.create_scatter(axes[1, 0], rated['rating'], rated['review_count'],
                        'Rating vs Review Count', 'Rating', 'Review Count',
                        color='green', alpha=0.3)
        axes[1, 0].set_yscale('log')
        
        # Average price by rating range
        rating_price = rated.groupby(pd.cut(rated['rating'], bins=5), observed=True)['current_price'].mean()
        PlotHelper.create_bar(axes[1, 1], rating_price.index.astype(str), rating_price.values,
                        'Average Price by Rating Range', 'Rating Range', 'Average Price (EGP)',
                        color='coral')
        
        self._save_plot('rating_analysis.png')
        
        return rating_stats

    def generate_store_performance(self):
        """Generate official store performance analysis"""
        logger.info("🏪 Generating store performance analysis...")
        
        # Compare official vs non-official stores
        store_comparison = self.data.groupby('is_official_store').agg({
            'sku': 'count',
            'current_price': 'mean',
            'discount': 'mean',
            'rating': 'mean',
            'review_count': 'sum'
        }).round(2)
        
        store_comparison.columns = [
            'product_count', 'avg_price', 'avg_discount', 'avg_rating', 'total_reviews'
        ]
        store_comparison = store_comparison.reset_index()
        store_comparison['is_official_store'] = store_comparison['is_official_store'].map({
            True: 'Official Store', False: 'Non-Official Store'
        })
        
        self._save_csv(store_comparison, 'store_performance.csv')
        
        # Create visualization using helper functions
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Product count comparison
        PlotHelper.create_bar(axes[0, 0], store_comparison['is_official_store'], store_comparison['product_count'],
                        'Product Count: Official vs Non-Official Stores', None, 'Number of Products',
                        color=['darkgreen', 'lightcoral'])
        
        # Average price comparison
        PlotHelper.create_bar(axes[0, 1], store_comparison['is_official_store'], store_comparison['avg_price'],
                        'Average Price: Official vs Non-Official Stores', None, 'Average Price (EGP)',
                        color=['darkblue', 'orange'])
        
        # Average discount comparison
        PlotHelper.create_bar(axes[1, 0], store_comparison['is_official_store'], store_comparison['avg_discount'],
                        'Average Discount: Official vs Non-Official Stores', None, 'Average Discount (%)',
                        color=['purple', 'yellow'])
        
        # Average rating comparison
        PlotHelper.create_bar(axes[1, 1], store_comparison['is_official_store'], store_comparison['avg_rating'],
                        'Average Rating: Official vs Non-Official Stores', None, 'Average Rating',
                        color=['gold', 'silver'])
        axes[1, 1].set_ylim(0, 5)
        
        self._save_plot('store_performance.png')
        
        return store_comparison
    
    def generate_daily_summary(self):
        """Generate daily summary statistics"""
        logger.info("📅 Generating daily summary...")
        
        summary = {
            'Date': [self.date],
            'Website': [self.website],
            'Total Products': [len(self.data)],
            'Avg Price': [self.data['current_price'].mean()],
            'Median Price': [self.data['current_price'].median()],
            'Products with Discount': [len(self.data[self.data['discount'] > 0])],
            'Avg Discount': [self.data[self.data['discount'] > 0]['discount'].mean()],
            'Products with Rating': [len(self.data[self.data['rating'] > 0])],
            'Avg Rating': [self.data[self.data['rating'] > 0]['rating'].mean()],
            'Total Reviews': [self.data['review_count'].sum()],
            'Official Store Products': [len(self.data[self.data['is_official_store'] == True])],
            'Non-Official Store Products': [len(self.data[self.data['is_official_store'] == False])],
            'Unique Categories': [self.data['category'].nunique()]
        }
        
        summary_df = pd.DataFrame(summary).round(2)
        self._save_csv(summary_df, 'daily_summary.csv')
        
        return summary_df
    
    def generate_report(self):
        """
        Main method to generate all reports and visualizations.
        This is the primary entry point for report generation.
        
        Returns:
            tuple: (summary_text, summary_filename)
        """
        logger.info("🚀 Starting comprehensive report generation...")
        
        # Initialize and validate
        self._init_report_generator()
        
        try:
            # Generate all reports
            self.generate_category_statistics()
            self.generate_top_rated_products()
            self.generate_discount_analysis()
            self.generate_price_distribution_analysis()
            self.generate_rating_analysis()
            self.generate_store_performance()
            self.generate_daily_summary()
            
            # Create a summary report text file
            summary_text = f"""
{'='*80}
SALES ANALYTICS REPORT
{'='*80}
Website: {self.website.upper()}
Date: {self.date}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

SUMMARY STATISTICS
{'-'*80}
Total Products Scraped: {len(self.data):,}
Unique Categories: {self.data['category'].nunique()}
Average Price: {self.data['current_price'].mean():.2f} EGP
Median Price: {self.data['current_price'].median():.2f} EGP
Price Range: {self.data['current_price'].min():.2f} - {self.data['current_price'].max():.2f} EGP

DISCOUNT INSIGHTS
{'-'*80}
Products with Discounts: {len(self.data[self.data['discount'] > 0]):,} ({len(self.data[self.data['discount'] > 0])/len(self.data)*100:.1f}%)
Average Discount: {self.data[self.data['discount'] > 0]['discount'].mean():.2f}%
Maximum Discount: {self.data['discount'].max():.2f}%

RATING & REVIEWS
{'-'*80}
Products with Ratings: {len(self.data[self.data['rating'] > 0]):,} ({len(self.data[self.data['rating'] > 0])/len(self.data)*100:.1f}%)
Average Rating: {self.data[self.data['rating'] > 0]['rating'].mean():.2f} / 5.0
Total Reviews: {self.data['review_count'].sum():,.0f}

STORE BREAKDOWN
{'-'*80}
Official Store Products: {len(self.data[self.data['is_official_store'] == True]):,} ({len(self.data[self.data['is_official_store'] == True])/len(self.data)*100:.1f}%)
Non-Official Store Products: {len(self.data[self.data['is_official_store'] == False]):,} ({len(self.data[self.data['is_official_store'] == False])/len(self.data)*100:.1f}%)

{'='*80}
GENERATED FILES
{'='*80}
CSV Reports:
  - category_statistics.csv
  - top_rated_products.csv
  - biggest_discounts.csv
  - price_statistics.csv
  - rating_statistics.csv
  - store_performance.csv
  - daily_summary.csv

Visualizations:
  - category_statistics.png
  - top_rated_products.png
  - discount_analysis.png
  - price_distribution.png
  - rating_analysis.png
  - store_performance.png

All files saved to: {self.report_folder}
{'='*80}
"""
            
            # Save summary text
            summary_path = os.path.join(self.report_folder, 'REPORT_SUMMARY.txt')
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            logger.info(f"✅ All reports generated successfully!")
            logger.info(f"📁 Reports location: {self.report_folder}")
            
            return summary_text, 'REPORT_SUMMARY.txt'
            
        except Exception as e:
            logger.error(f"❌ Error generating reports: {e}")
            raise
        finally:
            # Close database connection
            self.loader.close()


# Main function for easy import and use
def generate_analytics_report(website="jumia", date=None):
    """
    Convenience function to generate analytics report.
    
    Args:
        website (str): Website name (default: "jumia")
        date (str): Date in YYYY-MM-DD format (default: today)
    
    Returns:
        tuple: (summary_text, summary_filename)
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    generator = AnalyticsReportGenerator(website=website, date=date)
    return generator.generate_report()


if __name__ == "__main__":
    # Example usage
    generate_analytics_report(website="jumia", date="2025-12-01")
