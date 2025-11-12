import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_data(filepath: str) -> pd.DataFrame:
    """
    Load local CSV data.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame containing the loaded data
    """
    return pd.read_csv(filepath)

def filter_data(df: pd.DataFrame, countries: list[str]) -> pd.DataFrame:
    """
    Filter dataset by selected countries.
    
    Args:
        df: Input DataFrame
        countries: List of country names to filter by
        
    Returns:
        Filtered DataFrame
    """
    if not countries:
        return df
    return df[df['country'].isin(countries)]

def plot_box(df: pd.DataFrame, y_col: str, x_col: str = "country", title: str = "") -> go.Figure:
    """
    Create a boxplot using Plotly.
    
    Args:
        df: Input DataFrame
        y_col: Column name for y-axis values
        x_col: Column name for x-axis categories (default: "country")
        title: Plot title
        
    Returns:
        Plotly figure object
    """
    fig = px.box(
        df, 
        x=x_col, 
        y=y_col, 
        color=x_col, 
        points="all", 
        title=title
    )
    
    fig.update_layout(
        xaxis_title=x_col.title(),
        yaxis_title=y_col,
        template="plotly_white",
        showlegend=False,
        height=500
    )
    
    return fig

def top_regions_table(
    df: pd.DataFrame, 
    region_col: str, 
    metric_col: str, 
    top_n: int = 5
) -> pd.DataFrame:
    """
    Return top regions by average metric.
    
    Args:
        df: Input DataFrame
        region_col: Column name for regions
        metric_col: Column name for the metric to aggregate
        top_n: Number of top regions to return
        
    Returns:
        DataFrame with top regions and their average metrics
    """
    # Validate inputs
    if region_col not in df.columns:
        return pd.DataFrame(columns=["Region", f"Avg {metric_col}"])
    
    if metric_col not in df.columns:
        return pd.DataFrame(columns=["Region", f"Avg {metric_col}"])
    
    # Check if metric column is numeric
    if not pd.api.types.is_numeric_dtype(df[metric_col]):
        return pd.DataFrame(columns=["Region", f"Avg {metric_col}"])
    
    try:
        # Group and aggregate
        top = (
            df.groupby(region_col, as_index=False)[metric_col]
            .mean()
            .sort_values(metric_col, ascending=False)
            .head(top_n)
        )
        
        # Rename columns to avoid conflicts
        top = top.rename(columns={
            region_col: "Region",
            metric_col: f"Avg {metric_col}"
        })
        
        return top
    except Exception as e:
        # Return empty dataframe if any error occurs
        return pd.DataFrame(columns=["Region", f"Avg {metric_col}"])