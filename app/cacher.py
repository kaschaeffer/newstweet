import mysql.connector
from mysql.connector import errorcode
import time

# This module is used for storing past geographical search queries.
# Can be useful if the twitter API fails and we need backup data...

DB_NAME='cache'

def cacher(tweets,lat,lon):
  cnx = mysql.connector.connect(user='kevinschaeffer')
  cursor = cnx.cursor()
  cursor.execute('USE '+DB_NAME)
  now=int(time.time())
  #insert_str="INSERT INTO events(time,lat,lon) VALUES(%f,%f,%f);"
  insert_str="INSERT INTO events(time,lat,lon) VALUES("+str(now)+","+str(lat)+","+str(lon)+")"
  print insert_str
  data = [now,lat,lon]
  cursor.execute("START TRANSACTION;")
  try:
    cursor.execute(insert_str)
  except mysql.connector.Error as err:
    print("Failed to insert event data")
  cursor.execute("COMMIT;")
  cursor.execute("START TRANSACTION;")

  for tweet in tweets:
    try:
      #text=str(tweet[0])
      text=tweet[0]
      text=text.replace('"',"'")
      username=tweet[1]
      usernmae=username.replace('"',"'")
      insert_str='INSERT INTO tweets(time,text,username,news) VALUES('+str(now)+',"'+text+'","'+username+'",'+str(tweet[2])+')'
      #print insert_str
      print ("Successfully cached tweet data")
      cursor.execute(insert_str)
      cnx.commit()
    except:
      print("Failed to cache tweet data")
  cursor.close()
  cnx.close()
  return

def loader(lat,lon):
  cnx = mysql.connector.connect(user='kevinaschaeffer')
  cursor = cnx.cursor()
  cursor.execute('USE '+DB_NAME)
  select_str="SELECT text, username, news FROM tweets WHERE time ="
  select_str+="(SELECT time FROM events WHERE (("+str(lat)+"-lat)*("+str(lat)+"-lat)+("
  select_str+=str(lon)+"-lon)*("+str(lon)+"-lon))<2.0 ORDER BY time DESC LIMIT 1)"
  cursor.execute(select_str)
  news_tweets=[]
  other_tweets=[]
  for (text,username,news) in cursor:
    if news==1:
      news_tweets.append([text,username])
    else:
      other_tweets.append([text,username])
  cursor.close()
  cnx.close()
  return (news_tweets,other_tweets)



