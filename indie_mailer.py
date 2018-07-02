'''
Subscribe with your email.
You will receive a weekly or monthly email with a list of new indie movies
Can set threshold to only mail movies >x% rating (RT, IMDB, etc)
Will also notify if they are on netflix
'''
#APIs used:
#OMDb: http://www.omdbapi.com/
#TMDB: https://www.themoviedb.org

#Examples:https://www.themoviedb.org/documentation/api/discover

import urllib.request
import json
from datetime import date, timedelta
from time import sleep

class MovieDB():

    def __init__(self):
        #Initialize API keys (transfer to separate file)
        self.OMDb_key = '642d00de'
        self.TMDb_key = 'bdae228db10da126a4c1bb25e7ecba2d'
        self.today = date.today()

    def get_movie_list(self, time_delta = 7):
        #Get list of movies from last week
        movie_list = []
        end_date = str(self.today)
        start_date = str(self.today - timedelta(days=time_delta))

        #Probably break the next two calls into differnet functions
        try:
            movie_results = json.loads(urllib.request.urlopen( \
            "https://api.themoviedb.org/3/discover/movie?primary_release_date.gte={sd}&primary_release_date.lte={ed}&api_key={ak}"\
            .format(ak = self.TMDb_key, ed = end_date, sd = start_date))\
            .read())

            total_results = movie_results['total_results']
            print("Number of movies: {}".format(total_results))
            total_pages = movie_results['total_pages']
        except:
            print("Error in fetching list of movies: ")

        for page in range(1,int(total_pages)+1):
            try:
                print("Parsing page {}.".format(page))
                page_results = json.loads(urllib.request.urlopen( \
                "https://api.themoviedb.org/3/discover/movie?primary_release_date.gte={sd}&primary_release_date.lte={ed}&api_key={ak}&page={pg}"\
                .format(ak = self.TMDb_key, ed = end_date, sd = start_date, pg = page))\
                .read())

                for movie in page_results['results']:
                    mv = Movie(movie['id'], movie['title'], movie['genre_ids'], movie['release_date'], movie['overview'], movie['original_language'], self.OMDb_key, self.TMDb_key)
                    mv.get_TMDb_data()
                    mv.get_OMDb_data()
                    movie_list.append(mv)

                sleep(10) #each page contains ~20 movies, can only do 40 requests every 10 seconds
            except:
                print("Error in pagination")

        return movie_list

class Movie:


    def __init__(self, TMDb_id, title, genres, release_date, synopsis_l, language, OMDb_key, TMDb_key):
        #initialize movie
        self.TMDb_id = TMDb_id
        self.title = title
        self.genres = genres
        self.release_date = release_date
        self.synopsis_l = synopsis_l #long synpsis
        self.language = language
        self.OMDb_key = OMDb_key
        self.TMDb_key = TMDb_key

    def get_TMDb_data(self):
        #Get more info from TMDb
        try:
            movie_results = json.loads(urllib.request.urlopen( \
            "https://api.themoviedb.org/3/movie/{id}?api_key={ak}"\
            .format(ak = self.TMDb_key, id = self.TMDb_id))\
            .read())

            self.imdb_id = movie_results['imdb_id']
            self.budget = movie_results['budget']
            self.status = movie_results['status']


        except:
            print("Error in get_TMDb_data: {}".format(self.title))

    def get_OMDb_data(self):
        #Get info from OMDb
        
        try:
            movie_results = json.loads(urllib.request.urlopen( \
            "http://www.omdbapi.com/?apikey={ak}&i={id}"\
            .format(ak = self.OMDb_key, id = self.imdb_id))\
            .read())

            self.synopsys_s = movie_results['Plot']
            self.RT_rating = None
            for rating_source in movie_results['Ratings']:
                if rating_source['Source'] == 'Rotten Tomatoes':
                    self.RT_rating = rating_source['Value']

            self.metascore = movie_results['Metascore']
            self.imdb_rating = movie_results['imdbRating']
            self.imdb_votes = movie_results['imdbVotes']
            self.dvd_date = movie_results['DVD']
            self.box_office = movie_results['BoxOffice']
        except:
            print("Error in get_OMDb_data: {}".format(self.title))
        



if __name__ == '__main__':
        
    moviedb = MovieDB()
    a = moviedb.get_movie_list()


    #for movie in a:
        #print(movie.title)
    movie = a[1]
    print(movie.title)
    print(movie.TMDb_id)
    print(movie.genres)
    print(movie.release_date)
    print(movie.synopsis_l)
    print(movie.language)
    print(movie.status)
    print(movie.imdb_id)
    print("$", movie.budget)
    print(movie.synopsys_s)
    print(movie.RT_rating)
    print(movie.metascore)
    print(movie.imdb_rating)
    print(movie.imdb_votes)
    print(movie.dvd_date)
    print(movie.box_office)
    print("")


'''
def OMDb_movie_example(OMDb_key, movie = "The Matrix"):
    movie = json.loads(urllib.request.urlopen("http://www.omdbapi.com/?apikey={}&t={}&y=2018".format(OMDb_key, movie)).read())
    title = movie['Title']
    genre = movie['Genre']
    plot = movie['Plot'] #there is also a long plot option
    RT_rating = ['Ratings'][1]['Value']
    IM_rating = ['Ratings'][0]['Value']

def TMDB_movie_example():
    pass
    a = json.loads(urllib.request.urlopen("https://api.themoviedb.org/3/discover/movie?primary_release_date.gte=2018-03-15&primary_release_date.lte=2018-07-01&api_key={}&query=".format(apikey)).read())
'''

#from discover:
#movie title -- title
#id     -- id
#genre       -- genre_ids
#release dt  -- release_date
#synopsis(long)  -- overview
#lang        -- original_language

#from id search search: 'https://api.themoviedb.org/3/movie/351286?api_key=bdae228db10da126a4c1bb25e7ecba2d'

#budget     -- budget
#imdb_id    -- imdb_id
#status     -- status 