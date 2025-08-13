#!/usr/bin/env python3
"""
Streamlit Web App for CTEV Earnings Call Sentiment Analysis
Displays sentiment heatmaps for each quarter with detailed topic analysis.
"""

import streamlit as st
import json
import pandas as pd
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="CTEV Earnings Call Sentiment Analysis",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hover-info {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #1f77b4;
        margin: 1rem 0;
    }
    /* Make tabs bigger */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        font-size: 30px;
        font-weight: bold;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)


def load_quarter_data(quarter_file):
    """Load and parse JSON data for a specific quarter."""
    try:
        with open(quarter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data for {quarter_file}: {e}")
        return pd.DataFrame()


def display_topic_details(df, quarter_name):
    """Display detailed topic information."""
    if df.empty:
        return
    
    # Sort by sentiment for better analysis
    df_sorted = df.sort_values('sentiment', ascending=False)
    
    for _, row in df_sorted.iterrows():
        st.markdown(f"""
        <div class="hover-info">
            <h4>{row['topic']}</h4>
            <p><strong>Sentiment Score:</strong> {row['sentiment']:.2f}</p>
            <p><strong>Reasoning:</strong> {row['reasoning']}</p>
        </div>
        """, unsafe_allow_html=True)


def display_quarter_tab(quarter_name, json_file, png_file):
    """Display content for a specific quarter tab."""
    if os.path.exists(json_file):
        df = load_quarter_data(json_file)
        if not df.empty:
            # Display PNG file
            if os.path.exists(png_file):
                st.image(png_file, use_container_width=False)
            else:
                st.warning("PNG file not found. Please run the analysis first.")
            
            # Detailed Topic Analysis
            st.header(f"Detailed Topic Analysis for {quarter_name}")
            display_topic_details(df, quarter_name)
        else:
            st.warning(f"No data available for {quarter_name}")
    else:
        st.info(f"{quarter_name} analysis not found. Please run the analysis first.")


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">CTEV Earnings Call Sentiment Analysis</h1>', unsafe_allow_html=True)
    
    # Check if output directory exists
    output_dir = Path("output")
    if not output_dir.exists():
        st.error("Output directory not found. Please run the analysis first to generate data.")
        st.info("Run: `python src/ctev_earnings_call_analysis.py` to generate analysis data.")
        return
    
    # Available quarters
    quarters = {
        "Q4 2024": ("output/q4_2024_analysis_results.json", "output/q4_2024_sentiment_heatmap.png"),
        "Q1 2025": ("output/q1_2025_analysis_results.json", "output/q1_2025_sentiment_heatmap.png"),
        "Q2 2025": ("output/q2_2025_analysis_results.json", "output/q2_2025_sentiment_heatmap.png")
    }
    
    # Create tabs for each quarter (most recent first)
    tab1, tab2, tab3 = st.tabs(["Q2 2025", "Q1 2025", "Q4 2024"])
    
    # Q2 2025 Tab (most recent)
    with tab1:
        display_quarter_tab("Q2 2025", quarters["Q2 2025"][0], quarters["Q2 2025"][1])
    
    # Q1 2025 Tab
    with tab2:
        display_quarter_tab("Q1 2025", quarters["Q1 2025"][0], quarters["Q1 2025"][1])
    
    # Q4 2024 Tab (oldest)
    with tab3:
        display_quarter_tab("Q4 2024", quarters["Q4 2024"][0], quarters["Q4 2024"][1])
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with Streamlit • Analysis by OpenAI GPT-5 </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
