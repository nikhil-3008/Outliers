import streamlit as st

def analytics_page_1():
    st.title("Analytics Page 1")
    # Add the content for Analytics 1
    st.write("This is the content for Analytics Page 1.")

def analytics_page_2():
    st.title("Analytics Page 2")
    # Add the content for Analytics 2
    st.write("This is the content for Analytics Page 2.")

def analytics_page_3():
    st.title("Analytics Page 3")
    # Add the content for Analytics 3
    st.write("This is the content for Analytics Page 3.")

def analytics_page_4():
    st.title("Analytics Page 4")
    # Add the content for Analytics 4
    st.write("This is the content for Analytics Page 4.")

def analytics_page(analytics_option="Analytics 1"):
    if analytics_option == "Analytics 1":
        analytics_page_1()
    elif analytics_option == "Analytics 2":
        analytics_page_2()
    elif analytics_option == "Analytics 3":
        analytics_page_3()
    elif analytics_option == "Analytics 4":
        analytics_page_4()
    else:
        st.warning(f"Unknown analytics option: {analytics_option}")