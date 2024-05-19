import streamlit as st
from predict import create_Scatterplot_map

def progress_page(df_lat_lon_selected_year):
    st.markdown("## Prediction Page")
    # Display the Folium map
    map_plotly = create_Scatterplot_map(df_lat_lon_selected_year)
    st.plotly_chart(map_plotly, use_container_width=True)
