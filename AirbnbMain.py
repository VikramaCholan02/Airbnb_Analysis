#importing libraries
import pandas as pd
import pymongo
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image 
import os
import base64
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import STOPWORDS, WordCloud

st.set_page_config(layout= "wide")
# Center the title
st.markdown(
    """
    <style>
    .title {
        display: flex;
        justify-content: center;
        font-size: 40px;
        color: red;
    }
    </style>
    <div class="title">AIRBNB DATA VISUALIZATION</div>
    """,
    unsafe_allow_html=True
)

select = option_menu(None, ["Home","Overview","Explore","Powerbi Dashboard"],
                        orientation="horizontal", 
                        icons=["house","graph-up-arrow","bar-chart-line"],
                        menu_icon= "menu-button-wide",
                        default_index=0,
                        styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#FF5A5F"},
                                "nav-link-selected": {"background-color": "#FF5A5F"}})
    
# CREATING CONNECTION WITH MONGODB ATLAS AND RETRIEVING THE DATA
client = pymongo.MongoClient("mongodb_connection")
db = client.airbnb_analysis
col = db.airbnb_data


# READING THE CLEANED DATAFRAME
df = pd.read_csv("Sa.Airbnb_data.csv")

# HOME PAGE
if select == "Home":
   
    col1,col2 = st.columns(2,gap= 'medium')
    col1.markdown("## :blue[Domain] : Travel Industry, Property Management and Tourism.")
    col1.markdown("## :blue[Technologies used] : Python, Pandas, Plotly, Streamlit, MongoDB , Powerbi.")
    col1.markdown("## :blue[Overview] : This project aims to analyze Airbnb data using MongoDB Atlas, perform data cleaning and preparation, develop interactive geospatial visualizations, and create dynamic plots to gain insights into pricing variations, availability patterns, and location-based trends.")
    image_path = r"C:\Users\user2\OneDrive\Desktop\Airbnb Analysis Pr\airbnb image\airbnb_image_1.png"

    image = Image.open(image_path)

    # Resize the image using the PIL resize method
    new_width = 600
    new_height = 400
    image_resized = image.resize((new_width, new_height))

    with col2:
        # Display the resized image in Streamlit
        st.image(image_resized)

## OVERVIEW PAGE
if select == "Overview":
    tab1,tab2 = st.tabs(["$\huge 📝 RAW DATA $", "$\huge🚀 INSIGHTS $"])
    
    # RAW DATA TAB
    with tab1:
        # Create a select box
        option = st.selectbox(
            'Select Data to View',
            ('Raw Data', 'Dataframe'))
        
        # Display the corresponding data based on the selection
        if option == 'Raw Data':
            st.write(col.find_one())
        elif option == 'Dataframe':
            st.write(df)
                
    # INSIGHTS TAB
    with tab2:
        # Drop NaN values
        df = df.dropna(subset=['Country'])

        col1, col2 = st.columns(2)
        with col1:
            # Use the selectbox widget with 'All' option
            countries = ['All'] + sorted(df['Country'].unique().tolist())
            country = st.selectbox('Select a Country', countries)
        with col2:
            properties = ['All'] + sorted(df['Property_type'].unique().tolist())
            prop = st.selectbox('Select Property_type', properties)

        col3, col4 = st.columns(2)
        with col3:
            price = st.slider('Select Price', df['Price'].min(), df['Price'].max(), (df['Price'].min(), df['Price'].max()))
        with col4:
            room = st.multiselect('Select Room_type', sorted(df['Room_type'].unique()))

        # CONVERTING THE USER INPUT INTO QUERY
        query = ' & '.join(filter(None, [
            f'Country == "{country}"' if country != 'All' else None,
            f'Property_type == "{prop}"' if prop != 'All' else None,
            f'Room_type in {room}' if room else None,
            f'Price >= {price[0]}',
            f'Price <= {price[1]}'
        ]))
        
        # CREATING COLUMNS
        col1,col2 = st.columns(2,gap='medium')
        
        with col1:
            
            # TOP 10 PROPERTY TYPES BAR CHART
            df1 = df.query(query).groupby(["Property_type"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df1,
                         title='Top 10 Property Types',
                         x='Listings',
                         y='Property_type',
                         orientation='h',
                         color='Property_type',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            st.plotly_chart(fig,use_container_width=True) 
        
            # TOP 10 HOSTS BAR CHART
            df2 = df.query(query).groupby(["Host_name"]).size().reset_index(name="Listings").sort_values(by='Listings',ascending=False)[:10]
            fig = px.bar(df2,
                         title='Top 10 Hosts with Highest number of Listings',
                         x='Listings',
                         y='Host_name',
                         orientation='h',
                         color='Host_name',
                         color_continuous_scale=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
        
        with col2:
            
            # TOTAL LISTINGS IN EACH ROOM TYPES PIE CHART
            df1 = df.query(query).groupby(["Room_type"]).size().reset_index(name="counts")
            fig = px.pie(df1,
                         title='Total Listings in each Room_types',
                         names='Room_type',
                         values='counts',
                         color_discrete_sequence=px.colors.sequential.Rainbow
                        )
            fig.update_traces(textposition='outside', textinfo='value+label')
            st.plotly_chart(fig,use_container_width=True)
            
            # TOTAL LISTINGS BY COUNTRY CHOROPLETH MAP
            country_df = df.query(query).groupby(['Country'],as_index=False)['Name'].count().rename(columns={'Name' : 'Total_Listings'})
            fig = px.choropleth(country_df,
                                title='Total Listings in each Country',
                                locations='Country',
                                locationmode='country names',
                                color='Total_Listings',
                                color_continuous_scale=px.colors.sequential.Plasma
                               )
            st.plotly_chart(fig,use_container_width=True)
        
# EXPLORE PAGE
if select == "Explore":
    st.markdown("## Explore more about the Airbnb data")
    
    # Drop NaN values
    df = df.dropna(subset=['Country'])

    col1, col2 = st.columns(2)
    with col1:
        # Use the selectbox widget with 'All' option
        countries = ['All'] + sorted(df['Country'].unique().tolist())
        country = st.selectbox('Select a Country', countries)
    with col2:
        properties = ['All'] + sorted(df['Property_type'].unique().tolist())
        prop = st.selectbox('Select Property_type', properties)

    col3, col4 = st.columns(2)
    with col3:
        price = st.slider('Select Price', df['Price'].min(), df['Price'].max(), (df['Price'].min(), df['Price'].max()))
    with col4:
        room = st.multiselect('Select Room_type', sorted(df['Room_type'].unique()))

    # CONVERTING THE USER INPUT INTO QUERY
    query = ' & '.join(filter(None, [
        f'Country == "{country}"' if country != 'All' else None,
        f'Property_type == "{prop}"' if prop != 'All' else None,
        f'Room_type in {room}' if room else None,
        f'Price >= {price[0]}',
        f'Price <= {price[1]}'
    ]))
    
    # HEADING 1
    st.markdown("## Price Analysis")
    
    # CREATING COLUMNS
    col1,col2 = st.columns(2,gap='medium')
    
    with col1:
        
        # AVG PRICE BY ROOM TYPE BARCHART
        pr_df = df.query(query).groupby('Room_type',as_index=False)['Price'].mean().sort_values(by='Price')
        fig = px.bar(data_frame=pr_df,
                     x='Room_type',
                     y='Price',
                     color='Price',
                     title='Avg Price in each Room type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
        # HEADING 2
        st.markdown("## Availability Analysis")
        
        # AVAILABILITY BY ROOM TYPE BOX PLOT
        # box
        fig = px.bar(data_frame=df.query(query),
                     x='Room_type',
                     y='Availability_365',
                     color='Room_type',
                     title='Availability by Room_type'
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    with col2:
        
        # AVG PRICE IN COUNTRIES SCATTERGEO
        country_df = df.query(query).groupby('Country',as_index=False)['Price'].mean()
        fig = px.scatter_geo(data_frame=country_df,
                                       locations='Country',
                                       color= 'Price', 
                                       hover_data=['Price'],
                                       locationmode='country names',
                                       size='Price',
                                       title= 'Avg Price in each Country',
                                       color_continuous_scale='agsunset'
                            )
        col2.plotly_chart(fig,use_container_width=True)
        
        # BLANK SPACE
        st.markdown("#   ")
        st.markdown("#   ")
        
        # AVG AVAILABILITY IN COUNTRIES SCATTERGEO
        country_df = df.query(query).groupby('Country',as_index=False)['Availability_365'].mean()
        country_df.Availability_365 = country_df.Availability_365.astype(int)
        fig = px.scatter_geo(data_frame=country_df,
                                       locations='Country',
                                       color= 'Availability_365', 
                                       hover_data=['Availability_365'],
                                       locationmode='country names',
                                       size='Availability_365',
                                       title= 'Avg Availability in each Country',
                                       color_continuous_scale='agsunset'
                            )
        st.plotly_chart(fig,use_container_width=True)


#ABOUT        
if select == "Powerbi Dashboard":
    
    # Define the image path
    image_path = r"C:\Users\user2\OneDrive\Desktop\Airbnb Analysis Pr\airbnb image\power_bi.png"

    # Open the image
    image = Image.open(image_path)

    # Display the image with caption and alignment
    st.image(image, caption='Power BI Image', use_column_width=True)

    # Centering the image with markdown
    st.markdown(
        """
        <style>
        .element-container {
            display: flex;
            justify-content: center;
        }
        .element-container img {
            display: block;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.write("**:violet[Check My GitHub]** ⬇️")
    st.write("https://github.com/VikramaCholan02")
    st.write("**:violet[Linkedin]** ⬇️")
    st.write("https://www.linkedin.com/in/vikrama-cholan-188542251/")
