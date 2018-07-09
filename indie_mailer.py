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
import datetime
from time import sleep
import unicodecsv
import API_keys #.gitignored .py file

class MovieDB():

    def __init__(self):
        #Initialize API keys (transfer to separate file)
        self.OMDb_key = API_keys.keys['OMDb_KEY']
        self.TMDb_key = API_keys.keys['TMDb_KEY']
        self.today = date.today()
        self.query_count = 0

    def get_movie_list(self, time_delta = 7):
        #Get list of movies from last week
        movie_list = []
        end_date = str(self.today)
        start_date = str(self.today - timedelta(days=time_delta))

        #end_date = "2018-01-01"
        #start_date = "2017-11-01"


        #Probably break the next two calls into differnet functions
        try:
            self.query_count_check()
            movie_results = json.loads(urllib.request.urlopen( \
            "https://api.themoviedb.org/3/discover/movie?primary_release_date.gte={sd}"\
            "&primary_release_date.lte={ed}&without_genres=99,10770,10402&include_adult=false"\
            "&with_original_language=en&api_key={ak}"\
            .format(ak = self.TMDb_key, ed = end_date, sd = start_date))\
            .read())


            total_results = movie_results['total_results']
            print("Number of movies: {}".format(total_results))
            total_pages = movie_results['total_pages']
        except:
            print("Error in fetching list of movies: ")

        for page in range(1,int(total_pages)+1):
            try:
                self.query_count_check()
                print("Parsing page {}.".format(page))
                page_results = json.loads(urllib.request.urlopen( \
                "https://api.themoviedb.org/3/discover/movie?primary_release_date.gte={sd}"\
                "&primary_release_date.lte={ed}&without_genres=99,10770,10402&include_adult=false"\
                "&with_original_language=en&api_key={ak}&page={pg}"\
                .format(ak = self.TMDb_key, ed = end_date, sd = start_date, pg = page))\
                .read())

                for movie in page_results['results']:
                    mv = Movie(movie['id'], movie['title'], movie['genre_ids'], movie['release_date'], movie['overview'], movie['original_language'], self.OMDb_key, self.TMDb_key)
                    self.query_count_check()
                    mv.get_TMDb_data()
                    if mv.imdb_id: #check to see if movie has an IMDB ID
                        mv.get_OMDb_data()
                        movie_list.append(mv)

            except:
                print("Error in pagination")

        return movie_list

    def query_count_check(self):
        #Keep track of the number of queries to TMDb
        #will error out if more than 40 are done in 10 seconds
        #this will pause 10 seconds at 39 queries
        self.query_count += 1
        
        if self.query_count >= 39:
            print("Pausing for 10 seconds...")
            self.query_count = 0
            sleep(10)


class Movie:


    def __init__(self, TMDb_id = None, title= None, genres = None, release_date = None, synopsis_l = None, language = None, OMDb_key = None, TMDb_key = None):
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
        self.imdb_id = None
        self.budget = None
        self.status = None
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
        self.synopsys_s = None
        self.RT_rating = None
        self.metascore = None
        self.imdb_rating = None
        self.imdb_votes = None
        self.dvd_date = None
        self.box_office = None

        if self.status == 'Released' and self.imdb_id: #only query if movie is 'released' and has IMDB_id
            
            #request
            movie_response = urllib.request.urlopen("http://www.omdbapi.com/?apikey={ak}&i={id}"\
            .format(ak = self.OMDb_key, id = self.imdb_id))

            #http response code (200 = OK)
            http_code = movie_response.getcode()
            movie_results = json.loads(movie_response.read()) #read data

            response = movie_results['Response'] #OMDB DB response. if found = true, if not = false

            if response == "True" and http_code == 200:
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
                #end of new code
            else:  
                print("{}, || Response:{} Code:{}".format(self.title, response, http_code))
        

def print_list(movie_list):
    #Print full list of movies to CSV (as a validation test)
    date_time = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')

    csv_filename = ('movie_lists/{}-movie_list.csv'.format(date_time))
    fh = open(csv_filename,"wb")
    csv_out = unicodecsv.writer(fh, encoding='utf-8')
    csv_out.writerow(["Title", "TMDb_id", "IMDb_id", "Release Date", "Synopsis Short", "Synopsis Long", "Language", "Status", "Budget", "RT Rating", "Metascore", "IMDb Rating", "IMDb Votes", "DVD Date", "Box Office", "Genre IDs"])
    for movie in movie_list:
        if movie.status == 'Released':
            csv_out.writerow([movie.title, movie.TMDb_id, movie.imdb_id, movie.release_date, movie.synopsys_s, movie.synopsis_l, movie.language, movie.status, movie.budget, movie.RT_rating, movie.metascore, movie.imdb_rating, movie.imdb_votes, movie.dvd_date, movie.box_office, str(movie.genres)])

    fh.close()

if __name__ == '__main__':
        
    moviedb = MovieDB()
    a = moviedb.get_movie_list(7)
    print_list(a)

#TODO - create permanent DB. Store results, don't search already existing movies.
#must be able to update values though (esp dvd dates, ratings)
#create additional fields for watched_status(watched, interested, not interested), filter off that
#db gets filtered based on dvd dates, ratings, etc... can print said lists

#TODO - after that, need to make UI which shows uer list of movies, and can set watched_status
#Website maybe? Email?