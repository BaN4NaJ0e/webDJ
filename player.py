import pygame
import time
import sqlite3

import createSearchTree

currentSongPath = ""


def manager():
	while(True):
		getTopVotedSong()

		if currentSongPath != "":
			playSong()
		else :
			print "top 10 is empty! waiting for incoming votes"
			time.sleep(5)


def playSong():

	global currentSongPath	
	print "\nplaying song: " +str(currentSongPath)

	pygame.mixer.init()
	pygame.mixer.music.load(currentSongPath)
	pygame.mixer.music.play()
	#pygame.mixer.music.queue(nextSongPath)
	
	while pygame.mixer.music.get_busy():
	    time.sleep(1)
	
	currentSongPath = ""
	print "song finshed"


# lookup the song with most votes in database
def getTopVotedSong():
	global currentSongPath
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	# get current top songs
	cursor.execute("""SELECT path FROM musiclib WHERE votes > '0' ORDER BY votes DESC;""")
	topvotesTuple = cursor.fetchall()

	# set number of votes back to 0
	if len(topvotesTuple) != 0:
		t = (topvotesTuple[0])
		cursor.execute("""UPDATE musiclib SET votes= 0 WHERE path==?;""", t )
		connection.commit()

		currentSongPath = str(topvotesTuple[0][0])

	print currentSongPath	
	connection.close()
	# update html top10 list
	createSearchTree.buildHTML()
