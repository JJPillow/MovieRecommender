# Jennifer Pillow pillje@hotmail.com
# This script cleans raw movie rating data for use with the capstone project
# Data sourced from publicly available datasets on Kaggle.com

import pandas as pd

# get raw data
# movies.csv, ratings.csv, and links.csv sourced from:
# https://www.kaggle.com/shubhammehta21/movie-lens-small-latest-dataset
movie_data = pd.read_csv('movies.csv')
rating_data = pd.read_csv('ratings.csv')
link_data = pd.read_csv('links.csv')

# movies_metadata.csv sourced from:
# https://www.kaggle.com/rohan4050/movie-recommendation-data?select=movies_metadata.csv
movie_plots = pd.read_csv('movies_metadata.csv', low_memory=False)

# remove unneeded columns
movie_plots = movie_plots.drop(columns=['popularity', 'poster_path', 'production_companies', 'production_countries',
                                        'adult', 'belongs_to_collection', 'budget', 'genres', 'homepage', 'id',
                                        'tagline', 'original_language', 'original_title', 'revenue', 'spoken_languages',
                                        'status', 'video', 'vote_average', 'vote_count'])


# remove rows from movie_plots that do not have a value for imdb_id
movie_plots = movie_plots[movie_plots['imdb_id'].notna()]

# remove leading 't' from imdb_id strings and convert to integer type
movie_plots['imdb_id'] = movie_plots['imdb_id'].str.replace('t', '')
imdb_id_list = link_data['imdbId'].tolist()
movie_plots['imdb_id'] = movie_plots['imdb_id'].astype(str).astype(int)

# join movie plots with link data on imdbid
movie_plots = link_data.merge(movie_plots, left_on='imdbId', right_on='imdb_id')
# Visually inspect data
# print("movie_data: ")
# print(movie_data)
# print("movie_plots: ")
# print(movie_plots)
# print("rating_data: ")
# print(rating_data)

# The 'ratings.csv' file only contains ratings for users who have rated 20 movies or more,
# so there is no need to adjust for that.
# However, it is advantageous to filter out movies that have been rated only a few times.

num_ratings_by_movie = rating_data.groupby('movieId')['rating'].agg('count')
# print("num_ratings_by_movie: ")
# print(num_ratings_by_movie)

# remove movies with less than 20 ratings
m_rate_thold = 20

movies_to_keep = num_ratings_by_movie[num_ratings_by_movie >= m_rate_thold]
# print("movies_to_keep: ")
# print(movies_to_keep)

keep_plots = movie_plots[movie_plots.movieId.isin(movies_to_keep.index)]
# print("keep_plots: ")
# print(keep_plots)

keep_movies = movie_data[movie_data.movieId.isin(keep_plots['movieId'].to_list())]
# print("keep_movies: ")
# print(keep_movies)

keep_ratings = rating_data[rating_data.movieId.isin(keep_plots['movieId'].to_list())]
# print("keep_ratings: ")
# print(keep_ratings)
# print("num_ratings_by_movie: ")
# print(num_ratings_by_movie)

# save transformed data to new files
keep_movies.to_csv(r'..\movie_data.csv', index=False)
keep_ratings.to_csv(r'..\rating_data.csv', index=False)
keep_plots.to_csv(r'..\movie_plots.csv', index=False)
