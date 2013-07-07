''' 
tweet_classifier.py
Kevin Schaeffer
(newstweet project)
June 2013

XXXXXXXXX

'''

import sklearn


class TweetClassifier(object):
    '''
    Classifier for separating newsworthy tweets from other popular tweets.

    __init__(xxx)        -the constructor takes oAuth keys and tokens ( all strings)
                                    that are generated when registering the app with Twitter.

    _request(url)                   -private method that sends an oAuth GET request
                                    to url (string) and returns a dictionary

    get_geotweets(location,radius)  -returns a list of tweets (each a dictionary) coming from 
                                    location (dict with keys 'lat' and 'lon').  Inludes everything 
                                    that is at most a distance radius (int) in miles away from 
                                    the location.
    '''

    def load_model(self,pkl_file):
        pass

    def fit(self,training_data):
        # specify the kind of input !!!!!!!!!

        pass

    def predict(self,data):
        pass

