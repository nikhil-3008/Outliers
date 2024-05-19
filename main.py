import streamlit as st
from slidebar import sideBar
from home_page import home_page
import altair as alt
from prediction_page import progress_page
from analytics_page import analytics_page

# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

# CSS styling
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Main
selected, selected_year, df_accident_count_sorted, selected_color_theme, df_lat_lon_selected_year, df_selected_year, analytics_option = sideBar()

if selected == "Home":
    try:
        home_page(selected_year, df_accident_count_sorted, selected_color_theme, df_selected_year, df_lat_lon_selected_year)
    except Exception as e:
        st.warning(f"An error occurred: {e}")

elif selected == "Predicted Spot":
    try:
        progress_page(df_lat_lon_selected_year)
    except Exception as e:
        st.warning(f"An error occurred: {e}")

elif selected == "Analytics":
    try:
        if analytics_option:
            analytics_page(analytics_option)
        else:
            analytics_page()
    except Exception as e:
        st.warning(f"An error occurred: {e}")