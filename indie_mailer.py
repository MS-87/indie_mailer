'''
Subscribe with your email.
You will receive a weekly or monthly email with a list of new indie movies
Can set threshold to only mail movies >x% rating (RT, IMDB, etc)
Will also notify if they are on netflix
'''
#Full credit to:
#OMDb: http://www.omdbapi.com/
#TMDB: https://www.themoviedb.org

import urllib.request
import json

def OMDb_movie_example(OMDb_key, movie = "The Matrix"):
    movie = json.loads(urllib.request.urlopen("http://www.omdbapi.com/?apikey={}&t={}&y=2018".format(OMDb_key, movie)).read())
    title = movie['Title']
    genre = movie['Genre']
    plot = movie['Plot'] #there is also a long plot option
    RT_rating = ['Ratings'][1]['Value']
    IM_rating = ['Ratings'][0]['Value']

def TMDB_movie_example():
    pass