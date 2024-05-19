import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

def sideBar():
    df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
    df_lat_lon = pd.read_excel('data/demo.xlsx')

    with st.sidebar:
        st.title('🏂 KSP Dashboard')

        # File uploader in the sidebar
        data = st.file_uploader("Upload a Dataset", type=["csv", "xlsx", "xls"])
        if data is not None:
            if data.name.endswith('.csv'):
                df_lat_lon = pd.read_csv(data)
            elif data.name.endswith(('.xlsx', '.xls')):
                df_lat_lon = pd.read_excel(data)
            df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
        else:
            df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
            df_lat_lon = pd.read_excel('data/demo.xlsx')

        # Year selection
        year_list = list(df_lat_lon.Year.unique())[::-1]
        selected_year = st.selectbox('Select a year', year_list)
        df_selected_year = df_reshaped[df_reshaped.year == selected_year]
        df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

        # Filter latitude and longitude data by selected year
        df_lat_lon_selected_year = df_lat_lon[df_lat_lon.Year == selected_year]

        # Clean and standardize district names
        df_lat_lon_selected_year['DISTRICTNAME'] = df_lat_lon_selected_year['DISTRICTNAME'].str.strip().str.upper()

        # Count the number of latitude entries per district
        df_accident_count = df_lat_lon_selected_year.groupby('DISTRICTNAME')['Latitude'].count().reset_index()
        df_accident_count.columns = ['district', 'accident_count']

        # Sort the districts by accident count in descending order
        df_accident_count_sorted = df_accident_count.sort_values(by='accident_count', ascending=False)

        color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
        selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

        # Sidebar menu for page navigation
        selected = option_menu(
            menu_title="Menu",
            options=["Home", "Predicted Spot", "Analytics"],
            icons=["house", "eye", "bar-chart"],
            menu_icon="cast",
            default_index=0,
        )

        # Nested menu for Analytics
        if selected == "Analytics":
            analytics_option = option_menu(
                menu_title="Analytics",
                options=["Analytics 1", "Analytics 2", "Analytics 3", "Analytics 4"],
                icons=["chart-line", "chart-pie", "chart-bar", "chart-area"],
                menu_icon="cast",
                default_index=0,
            )
            return selected, selected_year, df_accident_count_sorted, selected_color_theme, df_lat_lon_selected_year, df_selected_year, analytics_option

    return selected, selected_year, df_accident_count_sorted, selected_color_theme, df_lat_lon_selected_year, df_selected_year, None