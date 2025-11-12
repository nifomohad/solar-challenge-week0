import streamlit as st
import pandas as pd
import os
from utils import load_data, plot_box, top_regions_table

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Solar Insights Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<p class="main-header"> Solar Energy Insights Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interactive visualization of Global Horizontal Irradiance (GHI) and solar metrics worldwide</p>', unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
DATA_PATH = "data/solar_data.csv"

@st.cache_data
def get_data(path):
    """Load and cache data for better performance."""
    return load_data(path)

# Handle both local and deployed scenarios
if not os.path.exists(DATA_PATH):
    # st.info("📤 **Upload Mode**: Please upload your solar data CSV file to begin analysis.")
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type="csv",
        help="Upload a CSV file containing solar irradiance data"
    )
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success(f" Successfully loaded **{len(df):,}** records!")
    else:
        st.warning(" Waiting for data upload...")
        st.markdown("""
            **Expected CSV format:**
            - Column for country/location names
            - Column for region names (optional)
            - Numeric columns for metrics (GHI, DNI, DHI, etc.)
        """)
        st.stop()
else:
    try:
        df = get_data(DATA_PATH)
        st.success(f" Successfully loaded **{len(df):,}** records from the dataset!")
    except FileNotFoundError:
        st.error(" Data file not found! Please ensure `data/solar_data.csv` exists locally.")
        st.stop()
    except Exception as e:
        st.error(f" Error loading data: {str(e)}")
        st.stop()

# -----------------------------
# DATA INSPECTION & COLUMN DETECTION
# -----------------------------
# Show available columns for debugging
with st.expander(" Dataset Information - Click to see your data structure"):
    st.write("**Available Columns:**")
    st.write(df.columns.tolist())
    st.write(f"**Total Rows:** {len(df):,}")
    st.write(f"**Total Columns:** {len(df.columns)}")
    st.write("\n**First 3 rows preview:**")
    st.dataframe(df.head(3), use_container_width=True)

# Detect country column (case-insensitive)
country_col = None
possible_country_names = ['country', 'countries', 'location', 'nation', 'state', 'region']
for col in df.columns:
    if col.lower() in possible_country_names:
        country_col = col
        st.info(f" Detected country column: **{col}**")
        break

if country_col is None:
    st.error(" No country/location column found in the dataset!")
    st.warning(f"Looking for columns named: {', '.join(possible_country_names)}")
    st.info("**Your columns are:** " + ", ".join(df.columns.tolist()))
    
    # Let user manually select the column
    st.markdown("### Please select which column contains location/country names:")
    country_col = st.selectbox(
        "Select the column for geographic grouping:",
        options=df.columns.tolist(),
        help="Choose the column that contains country, state, or location names"
    )
    
    if country_col:
        st.success(f"Using **{country_col}** as the geographic grouping column")

# Detect region column
region_col = None
possible_region_names = ['region', 'regions', 'area', 'zone', 'district', 'city']
for col in df.columns:
    if col.lower() in possible_region_names and col != country_col:
        region_col = col
        st.info(f" Detected region column: **{col}**")
        break

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("Control Panel")
st.sidebar.markdown("---")

# Country Selection
st.sidebar.subheader(f" {country_col} Selection")
try:
    countries = sorted(df[country_col].dropna().unique().tolist())
except Exception as e:
    st.error(f"Error reading {country_col} column: {str(e)}")
    st.stop()

select_all = st.sidebar.checkbox(f"Select All {country_col}s", value=False)

if select_all:
    selected_countries = countries
else:
    default_selection = countries[:3] if len(countries) >= 3 else countries
    selected_countries = st.sidebar.multiselect(
        f"Choose {country_col.lower()}s to analyze:",
        options=countries,
        default=default_selection,
        help=f"Select one or more {country_col.lower()}s to visualize"
    )

# Metric Selection
st.sidebar.markdown("---")
st.sidebar.subheader(" Metric Selection")

# Get numeric columns
numeric_cols = df.select_dtypes(include=['float64', 'int64', 'float32', 'int32']).columns.tolist()

# Prioritize common solar metrics
preferred_metrics = ['GHI', 'DNI', 'DHI', 'Tamb', 'TModA', 'TModB', 'WS', 'WSgust', 'RH']
available_metrics = [m for m in preferred_metrics if m in numeric_cols]

# If no preferred metrics found, use all numeric columns
if not available_metrics:
    available_metrics = numeric_cols

if not available_metrics:
    st.error(" No numeric columns found in the dataset!")
    st.stop()

metric = st.sidebar.selectbox(
    "Select metric for visualization:",
    available_metrics,
    index=0,
    help="Choose the metric to analyze"
)

# Top N Selection
st.sidebar.markdown("---")
st.sidebar.subheader(" Top Regions")
top_n = st.sidebar.slider(
    "Number of top regions to display:",
    min_value=3,
    max_value=min(20, len(df[country_col].unique()) if country_col else 20),
    value=5,
    step=1,
    help="Select how many top regions to show"
)

# Display Options
st.sidebar.markdown("---")
st.sidebar.subheader(" Display Options")
show_raw_data = st.sidebar.checkbox("Show Raw Data Table", value=False)
show_statistics = st.sidebar.checkbox("Show Key Statistics", value=True)

# -----------------------------
# FILTER DATA
# -----------------------------
if not selected_countries:
    st.warning(f" Please select at least one {country_col.lower()} from the sidebar.")
    st.stop()

# Filter data
filtered_df = df[df[country_col].isin(selected_countries)]

if len(filtered_df) == 0:
    st.error(f" No data available for selected {country_col.lower()}s.")
    st.stop()

# -----------------------------
# KEY METRICS
# -----------------------------
if show_statistics:
    st.markdown("###  Key Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"{country_col}s Selected",
            value=len(selected_countries),
            delta=f"{len(selected_countries)/len(countries)*100:.1f}% of total"
        )
    
    with col2:
        st.metric(
            label="Total Records",
            value=f"{len(filtered_df):,}",
            delta=f"{len(filtered_df)/len(df)*100:.1f}% of dataset"
        )
    
    with col3:
        avg_value = filtered_df[metric].mean()
        st.metric(
            label=f"Avg {metric}",
            value=f"{avg_value:.2f}",
            delta=f"±{filtered_df[metric].std():.2f}"
        )
    
    with col4:
        max_value = filtered_df[metric].max()
        st.metric(
            label=f"Max {metric}",
            value=f"{max_value:.2f}"
        )

st.markdown("---")

# -----------------------------
# MAIN DASHBOARD
# -----------------------------
tab1, tab2, tab3 = st.tabs([" Distribution Analysis", " Top Regions", " Data Table"])

# TAB 1: Distribution Analysis
with tab1:
    st.subheader(f"Distribution of {metric} by {country_col}")
    st.markdown(f"*Analyzing {len(filtered_df):,} data points across {len(selected_countries)} {country_col.lower()}s*")
    
    col_chart, col_stats = st.columns([3, 1])
    
    with col_chart:
        fig = plot_box(filtered_df, y_col=metric, x_col=country_col, title=f"{metric} Distribution by {country_col}")
        st.plotly_chart(fig, use_container_width=True)
    
    with col_stats:
        st.markdown("####  Statistics")
        stats_df = pd.DataFrame({
            'Metric': ['Mean', 'Median', 'Std Dev', 'Min', 'Max'],
            'Value': [
                f"{filtered_df[metric].mean():.2f}",
                f"{filtered_df[metric].median():.2f}",
                f"{filtered_df[metric].std():.2f}",
                f"{filtered_df[metric].min():.2f}",
                f"{filtered_df[metric].max():.2f}"
            ]
        })
        st.dataframe(stats_df, hide_index=True, use_container_width=True)
        
        with st.expander("Understanding Boxplots"):
            st.markdown("""
            - **Box**: 25th to 75th percentile (IQR)
            - **Line in box**: Median value
            - **Whiskers**: Min/Max range
            - **Points**: Individual data points
            """)

# TAB 2: Top Regions
with tab2:
    st.subheader(f"Top {top_n} {country_col}s by Average {metric}")
    
    # Use country_col for grouping if no separate region column
    group_col = region_col if region_col else country_col
    
    col_table, col_insights = st.columns([2, 1])
    
    with col_table:
        top_regions = top_regions_table(df, region_col=group_col, metric_col=metric, top_n=top_n)
        
        if len(top_regions) > 0:
            st.dataframe(
                top_regions,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning(f"No data available for ranking by {group_col}")
            st.info(f"Attempted to group by: **{group_col}** and aggregate: **{metric}**")
    
    with col_insights:
        st.markdown("###  Key Insights")
        if len(top_regions) > 0 and "Region" in top_regions.columns:
            best_region = top_regions.iloc[0]["Region"]
            best_value = top_regions.iloc[0][f"Avg {metric}"]
            st.success(f"**Best Performing:**\n\n{best_region}")
            st.metric("Performance", f"{best_value:.2f}")
            
            if len(top_regions) > 1:
                second_value = top_regions.iloc[1][f"Avg {metric}"]
                diff = best_value - second_value
                st.info(f"**Lead over 2nd:**\n\n{diff:.2f}")
        else:
            st.info("No ranking data available")

# TAB 3: Data Table
with tab3:
    st.subheader(" Filtered Dataset")
    
    if show_raw_data:
        st.markdown(f"Showing **{len(filtered_df):,}** records for selected {country_col.lower()}s")
        
        # Search functionality
        search_term = st.text_input(" Search in data:", placeholder="Type to search...")
        
        if search_term:
            mask = filtered_df.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            display_df = filtered_df[mask]
            st.info(f"Found **{len(display_df)}** matching records")
        else:
            display_df = filtered_df
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Download button
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"solar_data_{metric}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info(" Enable 'Show Raw Data Table' in the sidebar to view the full dataset")
        st.markdown("**Preview (first 5 rows):**")
        st.dataframe(filtered_df.head(), use_container_width=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p> <strong>Solar Energy Insights Dashboard</strong> | Built with Streamlit </p>
        <p style='font-size: 0.8rem;'>Interactive • Clean • Production-Ready</p>
    </div>
""", unsafe_allow_html=True)