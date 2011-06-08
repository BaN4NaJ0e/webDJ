# coding: utf-8
import sqlite3
import time


def setupDB():
	# open sqlite db connection
	connection = sqlite3.connect("uservotedb.db")
	cursor = connection.cursor()
	cursor.execute("""DROP TABLE IF EXISTS votedb """)

	cursor.execute("""CREATE TABLE IF NOT EXISTS votedb ( 
    		trackid INTEGER, userip TEXT, timestamp FLOAT)""")
	# commit all new entries
	connection.commit()

	#close db
	connection.close()

def insertVote(trackid, ip):
	connection = sqlite3.connect("uservotedb.db")
	cursor = connection.cursor()	

	timestamp = time.time()
	voteinfos = [trackid, ip, timestamp]	

	sql = "INSERT INTO votedb VALUES (?, ?, ?)" 	
	cursor.execute(sql, voteinfos)
	# commit all new entries
	connection.commit()

	#close db
	connection.close()

def checkQuota(trackid, ip):
	connection = sqlite3.connect("uservotedb.db")
	cursor = connection.cursor()

	t = (trackid, ip)
	# check if user voted for this song in the past
	cursor.execute("""SELECT timestamp FROM votedb WHERE trackid=? AND userip=?;""", t )
	pathTuple = cursor.fetchall()
	if len(pathTuple) > 0 :
	# user already voted for this song
		return False
	else:
	# first vote for this song by user
		return True

# after song was played, trackid/ip will be deleted so user can vote it again
def resetVotes(trackid):
	connection = sqlite3.connect("uservotedb.db")
	cursor = connection.cursor()
	
	t = (trackid)
	cursor.execute("""DELETE FROM votedb WHERE trackid=? ;""", t )
	# commit delete
	connection.commit()

	#close db
	connection.close()




	
