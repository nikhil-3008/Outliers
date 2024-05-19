import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from streamlit_folium import st_folium
from map_road_type import map_road_type
from clustermap_severity import create_cluster_map
from predict import create_Scatterplot_map
from streamlit_option_menu import option_menu
import openai
from streamlit_chat import message

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

# Load data
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
df_lat_lon = pd.read_excel('data/demo.xlsx')

# Sidebar function to manage navigation and filters
def sideBar():
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
            # st.dataframe(df.head())
            
        else:
            df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
            # st.dataframe(df.head())
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

    return selected, selected_year, df_accident_count_sorted, selected_color_theme, df_lat_lon_selected_year,df_selected_year

# Page functions
def home_page(selected_year, df_accident_count_sorted, selected_color_theme,df_selected_year):
    st.markdown('## Karnataka State Police Dashboard')

    with st.expander("🧭 My database"):
        shwdata = st.multiselect('Filter:', df_lat_lon_selected_year.columns, default=[])
        if shwdata:
            st.dataframe(df_lat_lon_selected_year[shwdata], use_container_width=True)
        else:
            st.dataframe(df_lat_lon_selected_year, use_container_width=True)

    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        st.markdown('#### Total Accidents')
        total_population = df_lat_lon[df_lat_lon['Year'] == selected_year]['Latitude'].count()
        st.metric(label="Total Accidents", value=total_population)

    with col2:
        st.markdown('#### Highest Accidents City')
        highest_population_state = df_selected_year_sorted.iloc[0]
        st.metric(label=highest_population_state['states'], value=highest_population_state['population'])

    with col3:
        st.markdown('#### Lowest Accidents City')
        lowest_population_state = df_selected_year_sorted.iloc[-1]
        st.metric(label=lowest_population_state['states'], value=lowest_population_state['population'])

    with col4:
        st.markdown('#### Migration Difference')
        if selected_year > 2010:
            population_difference_df = calculate_population_difference(df_reshaped, selected_year)
            migration_difference = population_difference_df['population_difference'].sum()
            st.metric(label="Migration Difference", value=migration_difference)
        else:
            st.metric(label="Migration Difference", value="N/A")

    col = st.columns(( 4.5, 3.5), gap='medium')


    with col[0]:
        st.markdown('#### Severity Map')
        map_folium = create_cluster_map(df_lat_lon_selected_year)
        st_folium(map_folium, width=700, height=500)

        heatmap = make_heatmap(df_reshaped, 'year', 'states', 'population', selected_color_theme)
        st.altair_chart(heatmap, use_container_width=True)

    with col[1]:
        
        st.markdown('#### Top Districts by Accident Count')
        st.dataframe(df_accident_count_sorted,
                     column_order=["district", "accident_count"],
                     hide_index=True,
                     width=None,
                     column_config={
                         "district": st.column_config.TextColumn("District"),
                         "accident_count": st.column_config.ProgressColumn(
                             "Accident Count",
                             format="%d",
                             min_value=0,
                             max_value=max(df_accident_count_sorted.accident_count),
                         )
                     }
                     )
        st.markdown('#### Choropleth Map')
        choropleth = make_choropleth(df_selected_year, 'states_code', 'population', selected_color_theme)
        st.plotly_chart(choropleth, use_container_width=True)


        with st.expander('About', expanded=True):
            st.write('''
                - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
                - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
                - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000
            ''')
        

def progress_page(df_lat_lon_selected_year):
    st.markdown("## Prediction Page")
    # Display the Folium map
    map_plotly = create_Scatterplot_map(df_lat_lon_selected_year)
    st.plotly_chart(map_plotly, use_container_width=True)
    

def analytics_page():
    # message("My message") 
    # message("Hello bot!", is_user=True)  # align's the message to the right
    st.title("ChatGPT-like clone")

    # Retrieve the API key from secrets
    api_key = st.secrets["openai"]["api_key"]

    # Initialize the OpenAI client with the API key
    openai.api_key = api_key

    # Ensure the session state is properly initialized
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get the response from OpenAI
        with st.chat_message("assistant"):
            response = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )

            response_content = response.choices[0].message['content']
            st.markdown(response_content)

        st.session_state.messages.append({"role": "assistant", "content": response_content})
    

# Utility functions
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'max({input_color}):Q',
                        legend=None,
                        scale=alt.Scale(scheme=input_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=900).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )
    return heatmap

def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_selected_year.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

def calculate_population_difference(df, selected_year):
    df_previous_year = df[df.year == selected_year - 1][['states', 'population']].rename(columns={'population': 'previous_population'})
    df_current_year = df[df.year == selected_year][['states', 'population']].rename(columns={'population': 'current_population'})
    df_population_difference = pd.merge(df_current_year, df_previous_year, on='states')
    df_population_difference['population_difference'] = df_population_difference['current_population'] - df_population_difference['previous_population']
    return df_population_difference

def make_donut(value, label, color):
    donut_chart = alt.Chart(pd.DataFrame({
        'category': [label, ''],
        'value': [value, 100 - value]
    })).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="value", type="quantitative"),
        color=alt.Color(field="category", type="nominal", scale=alt.Scale(range=[color, "lightgray"])),
    ).properties(width=150, height=150)
    return donut_chart

# Main
selected, selected_year, df_accident_count_sorted, selected_color_theme, df_lat_lon_selected_year,df_selected_year = sideBar()

if selected == "Home":
    try:
        home_page(selected_year, df_accident_count_sorted, selected_color_theme,df_selected_year)
    except Exception as e:
        st.warning(f"An error occurred: {e}")

elif selected == "Predicted Spot":
    try:
        progress_page(df_lat_lon_selected_year)
    except Exception as e:
        st.warning(f"An error occurred: {e}")

elif selected == "Analytics":
    try:
        analytics_page()
    except Exception as e:
        st.warning(f"An error occurred: {e}")
