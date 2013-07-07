''' 
tokenizer.py
Kevin Schaeffer
(newstweet project)
June 2013

XXXXXXXXX

'''
import unittest
import re
import nltk


class Tokenizer(unittest.TestCase):
    '''
    Tokenizer for tweets. Builds the features that are used for classifying tweets

    __init__(xxx)        -the constructor takes oAuth keys and tokens ( all strings)
                                    that are generated when registering the app with Twitter.

    _request(url)                   -private method that sends an oAuth GET request
                                    to url (string) and returns a dictionary

    get_geotweets(location,radius)  -returns a list of tweets (each a dictionary) coming from 
                                    location (dict with keys 'lat' and 'lon').  Inludes everything 
                                    that is at most a distance radius (int) in miles away from 
                                    the location.
    '''

    replacement_rules=[[':',' : '],
                        [';',' ; '],
                        [',',' , '],
                        ['-',' - '],
                        ['?',' ? '],
                        ['!',' ! '],
                        ['.',' . '],
                        ['"',' " '],
                        ["' "," ' "],
                        [" '"," ' "],
                        [r'\U',r'\U']]

    regex_rules=[[r'http:[\S]+',' '],
                    [r'@[A-Za-z0-9_]*','@'],
                    [r'#[A-Za-z0-9_]*','#']]

    def __init(self):
        pass

    def clean(self,document):
    
        for rule in self.replacement_rules:
            document=document.replace(rule[0],rule[1])

        for rule in self.regex_rules:
            regex=re.compile(rule[0])
            document=regex.sub(rule[1],document)

        return document

        tweet_out=tweet
        regex=re.compile(r'http:')
        tweet_out = (regex.split(tweet_out))[0]
        regex=re.compile(r':')
        tweet_out = regex.sub(' : ',tweet_out)
        regex=re.compile(r';')
        tweet_out = regex.sub(' ; ',tweet_out)
        regex=re.compile(r',')
        tweet_out = regex.sub(' , ',tweet_out)
        regex=re.compile(r'-')
        tweet_out = regex.sub(' - ',tweet_out)
        regex=re.compile(r'\?')
        tweet_out = regex.sub(' \? ',tweet_out)
        regex=re.compile(r'!')
        tweet_out = regex.sub(' ! ',tweet_out)
        regex=re.compile(r'\.')
        tweet_out = regex.sub(r' . ',tweet_out)
        regex=re.compile(r'-')
        tweet_out = regex.sub(' - ',tweet_out)
        regex=re.compile(r"'")
        tweet_out = regex.sub(r" ' ",tweet_out)
        regex=re.compile(r'"')
        tweet_out = regex.sub(r' " ',tweet_out)
        regex=re.compile(r'@[A-Za-z0-9_]*')
        tweet_out = regex.sub('@',tweet_out)
        regex=re.compile(r'#[A-Za-z0-9_]*')
        tweet_out = regex.sub('#',tweet_out)
        regex=re.compile(r'\\U')
        tweet_out = regex.sub(r' \\U ',tweet_out)
        return document

    def tokenize(self,document):
        document=self.clean(document)
        document=document.lower()
        words=document.split()
        return words

    # def runTest(self):
    #     t=Tokenizer()
    #     # tweet='.?-.,;:\U http://www.dontshowthis.com/index @foobar #bs'
    #     # self.assertEqual(' .  ?  -  .  ,  ;  :  \U    @ #',t.clean(tweet),'tweet cleaned incorrectly')
    #     tweet='.?-.,;:'
    #     clean_tweet=' .  ?  -  .  ,  ;  : '
    #     self.assertEqual(clean_tweet,t.clean(tweet),'tweet cleaned incorrectly')
    #     self.assertEqual(5,5,'just a test')

    def test_clean(self):
        t=Tokenizer()
        # tweet='.?-.,;:\U http://www.dontshowthis.com/index @foobar #bs'
        # self.assertEqual(' .  ?  -  .  ,  ;  :  \U    @ #',t.clean(tweet),'tweet cleaned incorrectly')
        tweet='.?-.,;:'
        clean_tweet=' .  ?  -  .  ,  ;  : '
        self.assertEqual(clean_tweet,t.clean(tweet),'tweet cleaned incorrectly')

if __name__=='__main__':
    unittest.main(verbosity=2)
