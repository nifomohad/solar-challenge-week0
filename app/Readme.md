Solar Energy Insights Dashboard

An interactive Streamlit dashboard for visualizing and analyzing global solar energy metrics such as Global Horizontal Irradiance (GHI), Direct Normal Irradiance (DNI), Diffuse Horizontal Irradiance (DHI), and more. The dashboard supports both local CSV uploads and pre-loaded datasets for quick analysis.

Features

Interactive Visualizations: Boxplots and statistics for selected solar metrics by country or region.

Top Regions Analysis: Identify top-performing countries/regions for a chosen metric.

Dynamic Data Filtering: Filter data by country and metric with control panel in the sidebar.

Data Table & Search: Explore and search the filtered dataset with download functionality.

Customizable Dashboard: Easily update metrics, countries, and regions for analysis.

Responsive UI: Works on both local and deployed Streamlit environments.

Installation




Create and activate a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows


Install required packages:

pip install -r requirements.txt


Requirements: streamlit, pandas, plotly, any other dependencies from utils.py.

Usage
Run Locally
streamlit run app.py

Data Input

Default Mode: Loads data/solar_data.csv if available.

Upload Mode: Upload your own CSV file through the dashboard.

Expected CSV format:

Country/Location	Region (Optional)	GHI	DNI	DHI	Tamb	...
Dashboard Sections

Distribution Analysis

Visualize the distribution of a chosen metric by country/region using boxplots.

Includes key statistics: mean, median, standard deviation, min, max.

Top Regions

Displays top N countries/regions by average metric.

Provides key insights with performance metrics.

Data Table

Filtered dataset display with search functionality.

Option to download filtered data as CSV.

Sidebar Controls

Country Selection: Multi-select or select all countries/locations.

Metric Selection: Choose from numeric solar metrics (GHI, DNI, DHI, etc.).

Top Regions: Select the number of top regions to display.

Display Options: Toggle raw data table and key statistics.

Utilities (utils.py)

load_data(path): Loads CSV data from the specified path.

plot_box(df, y_col, x_col, title): Generates boxplots for visual analysis.

top_regions_table(df, region_col, metric_col, top_n): Returns top N regions by metric.

Deployment

Compatible with Streamlit Cloud or any server hosting Python 3.x.

Make sure data/solar_data.csv is available, or enable file upload.