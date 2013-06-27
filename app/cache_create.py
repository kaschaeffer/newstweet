from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

# Creates the cached database for storing tweets

DB_NAME = 'cache'
TABLES={}
TABLES['tweets']= (
   "CREATE TABLE `tweets` ("
   " `tweet_id` int(11) NOT NULL AUTO_INCREMENT,"
   " `time` int(11) NOT NULL,"
   " `text` varchar(140),"
   " `news` int(11),"
   " PRIMARY KEY (`tweet_id`)"
   ") ENGINE=InnoDB")
TABLES['events']= (
   "CREATE TABLE `events` ("
   " `time` int(11) NOT NULL,"
   " `lat` float(11),"
   " `lon` int(11),"
   " PRIMARY KEY (`time`)"
   ") ENGINE=InnoDB")

cnx = mysql.connector.connect(user='kevinschaeffer')
cursor = cnx.cursor()

def create_database(cursor):
    try:
        #cursor.execute("GRANT ALL PRIVILEGES ON `%s`.* TO `kevinschaeffer`@`localhost`;",DB_NAME)
        cursor.execute(
           "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        print("Successfully created database")
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = DB_NAME    
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for name, ddl in TABLES.iteritems():
    cursor.execute("START TRANSACTION")
    try:
        print(name)
        drop_str="DROP TABLE IF EXISTS `"+str(name)+"`"
        cursor.execute(drop_str)
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except:
        print("Error creating tables")
    else:
        print("OK")
    cursor.execute("COMMIT")
cursor.close()
cnx.close()