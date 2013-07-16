import pickle
import numpy as np
import re

#Import (unpickle) the trained Naive Bayes model...
#Set root directory
root_dir='./'

pkl_file = open(root_dir+'app/model/naiveb_model.pkl', 'rb')
clf = pickle.load(pkl_file)
pkl_file.close()

pkl_file = open(root_dir+'app/model/word_ind.pkl', 'rb')
word_ind = pickle.load(pkl_file)
pkl_file.close()

#import filter for removing any tweets containing offensive content
filter_words = [line.strip() for line in open(root_dir+"app/model/filter-words.txt").readlines()]

def process(tweet):
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
    return tweet_out

def processfilter(tweet):
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
    regex=re.compile(r'\_')
    tweet_out = regex.sub(' _ ',tweet_out)
    regex=re.compile(r"'")
    tweet_out = regex.sub(r" ' ",tweet_out)
    regex=re.compile(r'"')
    tweet_out = regex.sub(r' " ',tweet_out)
    regex=re.compile(r'\@')
    tweet_out = regex.sub(' @ ',tweet_out)
    regex=re.compile(r'\#')
    tweet_out = regex.sub(' # ',tweet_out)
    regex=re.compile(r'\\U')
    tweet_out = regex.sub(r' \\U ',tweet_out)
    return tweet_out

def classify(tweets):
    text_tweets=[]
    for tweet in tweets:
      if 'text' in tweet:
        text_tweets.append(tweet['text'])
    text_tweets=list(set(text_tweets))
    print 'number of any raw tweets pulled in: '+str(len(text_tweets))

    # If the sample size of fresh tweets is too low (<200) 
    # its unlikely that any newsworthy tweets will appear
    # in this case, we look for slightly older
    # cached tweets
    #
    if len(text_tweets)<200:
      #try to pull tweets from cache
      print 'going to cache...'
      news_tweets,other_tweets = loader(lat,lon)
      print news_tweets
      print other_tweets
      if len(news_tweets)>0:
        return jsonify(result={'other_tweets': zip(*other_tweets)[0],'other_tweets_names': zip(*other_tweets)[1],
          'news_tweets': zip(*news_tweets)[0],'news_tweets_names': zip(*news_tweets)[1],'errors': 0})
      else:
        print 'nothing in cache...'
        return jsonify(result={'other_tweets': '','news_tweets': '','errors': 1})
    live_tweets=[]

    for tweet in tweets:
      if 'text' in tweet and 'retweet_count' in tweet:
        # Only keep tweets with > 100 characters
        # (performance of the classification algorithm
        # degrades significantly for very short tweets)
        if len(tweet['text'])>100:
          screen_name=''
          tweet_text=tweet['text']
          tweet_rtcount=tweet['retweet_count']
          if 'user' in tweet:
            if 'screen_name' in tweet['user']:
              screen_name=tweet['user']['screen_name']

          # check to see if its a retweet
          # if so use the original message
          if 'retweeted_status' in tweet:
            if 'text' in tweet['retweeted_status']:
              tweet_text=tweet['retweeted_status']['text']
            if 'user' in tweet['retweeted_status'] and 'screen_name' in tweet['retweeted_status']['user']:
              screen_name=tweet['retweeted_status']['user']['screen_name']
          live_tweets.append((tweet_text,tweet_rtcount,tweet['id_str'],screen_name))
          


    # Remove duplicates
    tweet_text_list=[]
    live_tweets2=[]
    try:
      for tweet in live_tweets:
        if tweet[0] not in tweet_text_list:
          live_tweets2.append(tweet)
          tweet_text_list.append(tweet[0])
      print 'with duplicates removed: '+str(len(live_tweets2))
      print 'with no duplicates: '+str(len(live_tweets))
    except:
      print 'error removing duplicates'

    live_tweets=live_tweets2
    live_tweets=list(set(live_tweets))

    # Sort the tweets by retweet count first
    # and only keep the 150 most popular tweets
    # this will be our sample that gets passed through the 
    # Naive Bayes Classifier
    live_tweets.sort(key=(lambda x: x[1]),reverse=True)
    max_size=150
    if len(live_tweets)>max_size:
      live_tweets=live_tweets[:max_size]
    just_tweets=[]

    for tweet in live_tweets:
      just_tweets.append((tweet[0],tweet[2],tweet[3]))

    live_tweets=list(set(just_tweets))

    # Filter out any offensive content
    # in non-news tweets
    good_tweets=[]
    for tweet in live_tweets:
      filterout=False
      tsplit = processfilter(tweet[0]).split()
      for word in tsplit:
        if word.lower() in filter_words:
          filterout=True
          break
      if filterout==False:
        good_tweets.append(tweet)


    live_tweets=good_tweets
    nfeatures=len(word_ind)
    nlive=len(live_tweets)
    live_mat=np.zeros((nlive,nfeatures))


    for n_ind in range(len(live_tweets)):
        tsplit = process(live_tweets[n_ind][0]).split()
        for word in tsplit:
            if word in word_ind:
                lword=word.lower()
                live_mat[n_ind,word_ind[lword]]+=1
    live_pred = list(clf.predict(live_mat))
    live_pred_prob = list(clf.predict_proba(live_mat))
    live_news=[]
    live_other=[]
    for i in range(len(live_pred)):
        if live_pred[i]:
            live_news.append((live_tweets[i][0],live_tweets[i][1],live_pred_prob[i][0],live_tweets[i][2]))
        else:
            live_other.append((live_tweets[i][0],live_tweets[i][1],live_pred_prob[i][0],live_tweets[i][2]))

    # Sort the news stories (live_news) by news-worthiness
    # as measured by the probability that they're news
    # according to my Naive Bayes Classifier model.
    #
    # However, keep the non-news stories (live_other) sorted
    # by retweet count.
    live_news.sort(key=(lambda x:x[2]))

    # Use ntweets_send to set how many tweets 
    # I want to display in each category
    ntweets_send=3
    if len(live_news)>ntweets_send:
        live_news=live_news[:ntweets_send]
    if len(live_other)>ntweets_send:
        live_other=live_other[:ntweets_send]


    return live_news, live_other