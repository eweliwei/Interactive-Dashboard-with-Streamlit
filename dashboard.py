# Developed using virtual environment
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np


# Webpage title, header and subtitle
st.set_page_config(page_title="IMDb Movies Analysis", layout='wide')
st.header("IMDB Movie Dashboard With Streamlit")

# --- Read CSV file ---
movie_df = pd.read_csv("https://raw.githubusercontent.com/danielgrijalva/movie-stats/7c6a562377ab5c91bb80c405be50a0494ae8e582/movies.csv")

# ---  Data Understanding  ---
# --- View dataset info ---
print(movie_df.info())

# --- Detect Missing Values ---

# Calculate the total number of missing values per column
missing_values_count = movie_df.isnull().sum()

# Calculate the percentage of missing values per column
missing_values_percentage = (missing_values_count / len(movie_df)) * 100

# Create a DataFrame to display the results
missing_data = pd.DataFrame({
    'Total Missing Values': missing_values_count,
    'Percentage of Missing Values': missing_values_percentage
})

# Print the missing data information
print(missing_data)

# --- Detect Duplicated Values ---
print('Total duplicated records: ', movie_df.duplicated().sum())

# --- Drop Missing Values ---
movie_df = movie_df.dropna()

# --- View Current Number of Columns and Rows ---
num_rows, num_columns = movie_df.shape

# Print the total number of rows and columns
print("Number of rows:", num_rows)
print("Number of columns:", num_columns)

# --- Streamlit App Development Starts Here ---

# --- Create filters ---
movie_release_year = movie_df['year'].unique().tolist()
movie_country = movie_df['country'].unique().tolist()
movie_score_rating = movie_df['score'].unique().tolist()
movie_genre_list = movie_df['genre'].unique().tolist()

# --- Sidebar widgets ---
with st.sidebar:
    # Dropbox - Unique Year Values
    year = st.selectbox('Choose a Year', movie_release_year, 0)
    
    # Dropbox - Unique Country Values
    country = st.selectbox('Choose a Country', movie_country, 0)
    
    # Slider - Score Range
    st.write("Select score range to view the movie genre")
    selected_score_rating = st.slider(label = "Select Score Range:",
                                  min_value = 1.0,
                                  max_value = 10.0,
                                 value = (1.0,5.0))
    # MultiSelection - Movie Genre
    st.write("Select your preferred genre(s) and year to view the movies released that year and on that genre")
    selected_genres = st.multiselect('Choose Preferred Genre:',
                                        movie_genre_list, default = ['Animation', 'Horror', 'Fantasy', 'Romance'])


# --- Configure Slider Widget For Interactivity ---
# Score Range
score_info = (movie_df['score'].between(*selected_score_rating))

# Genre + Year
new_genre_year = (movie_df['genre'].isin(selected_genres)) & (movie_df['year'] == year)

# Genre + Year + Country
genre_year_country = (movie_df['genre'].isin(selected_genres)) & (movie_df['country'] == country)

# --- Configure Visualisations ---

# Row 1
col1, col2, col3 = st.columns(3)

with col1:  
    st.write("#### Average rating for selected genre(s)")
    average_rating = movie_df[movie_df['genre'].isin(selected_genres)]['score'].mean()
    st.metric(label="", value=f"{average_rating:.2f}")
    
with col2:
    st.write("#### Average runtime for selected genre(s)")
    average_runtime = movie_df[movie_df['genre'].isin(selected_genres)]['runtime'].mean()
    st.metric(label="", value=f"{average_runtime:.2f} minutes")

with col3:
    st.write("#### Total movies in selected genre(s)")
    filtered_movies = movie_df[movie_df['genre'].isin(selected_genres)]
    total_movies = len(filtered_movies)
    st.metric(label="", value=total_movies)

# Row 2
col1, col2 = st.columns(2)
with col1:
    st.write("""#### Lists of movies filtered by Year and Genre """)
    df_genre_year = movie_df[new_genre_year].groupby(['name', 'genre'])['year'].sum()
    df_genre_year = df_genre_year.reset_index()
    st.dataframe(df_genre_year, width = 600)

with col2:
    st.write("""#### Lists of movies filtered by Genre and Score """)
    df_genre_score = movie_df[new_genre_year].groupby(['name', 'genre'])['score'].sum()
    df_genre_score = df_genre_score.reset_index()
    st.dataframe(df_genre_score, width = 600)

# Row 3
col1, col2 = st.columns(2)

with col1:
    st.write("#### Average Movie Budget Grouped by Genre")
    avg_budget = movie_df.groupby('genre')['budget'].mean().round().reset_index()
    fig = px.bar(avg_budget, x='genre', y='budget', color='genre', labels={'genre': 'Genre', 'budget': 'Average Budget'})
    fig.update_layout(barmode='overlay', showlegend=True, height=400, width=550)
    st.plotly_chart(fig)
    
with col2:
    st.write("#### Movie runtime distribution for genre(s)")
    genre_runtime = movie_df[movie_df['genre'].isin(selected_genres)][['runtime', 'genre']]
    fig = px.histogram(genre_runtime, nbins=20, x='runtime', color='genre',
                       labels={'runtime': 'Runtime', 'genre': 'Genre', 'count': 'Count'})
    fig.update_layout(showlegend=True, height=400, width=550)
    fig.update_traces(opacity=0.7)
    st.plotly_chart(fig)

# Row 4
col1, col2 = st.columns(2)

with col1:
    st.write("""#### Movie Score By Genre """)
    rating_count_year = movie_df[score_info].groupby('genre')['score'].count()
    rating_count_year = rating_count_year.reset_index()
    fig = px.line(rating_count_year, x = 'genre', y = 'score')
    fig.update_layout(showlegend=True, height=500, width=550)
    st.plotly_chart(fig)
    
with col2:
    filtered_data = movie_df[genre_year_country]
    fig = px.bar(filtered_data,  x='score', y='name', color='genre', labels={'score': 'Score', 'name': 'Movie'})
    fig.update_layout(title=f"Movies in {country} released in {year} ({', '.join(selected_genres)})",
                    yaxis_title='Movie',
                    xaxis_title='Cumulative Score', height=500, width=550)
    st.plotly_chart(fig)