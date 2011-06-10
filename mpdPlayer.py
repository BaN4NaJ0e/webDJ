import subprocess
import time
import sqlite3
import createSearchTree
import settings
import votedb


currentTopSongs = []
oldCurrentTopSongs = []
lasttrackid = []

def isNotPlaying():
	output = subprocess.Popen(['mpc'], stdout=subprocess.PIPE).communicate()[0]
	if output.find('playing') > 0:
		return False
	else:
		return True
		
def nowPlaying():
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	currentfile = subprocess.Popen(['mpc','-f','"%file%"','current'], stdout=subprocess.PIPE).communicate()[0].replace('"','').rstrip()
	# execute can't handle simple strings for substitution so lets put it in a tuple
	currentpath = [settings.musicfolder + "/" + unicode(currentfile, "utf-8") ]
	cursor.execute("""SELECT artist, title, album, albumart, tracklength FROM musiclib WHERE path == ?;""", currentpath )
	nowPlayingTuple = cursor.fetchall()
	connection.close()
	return nowPlayingTuple

# reset votes to zero and write to db which time this track was played
def resetVotes():
	global lasttrackid
	if not isNotPlaying():
		connection = sqlite3.connect("mucke.db")
		cursor = connection.cursor()
		currentfile = subprocess.Popen(['mpc','-f','"%file%"','current'], stdout=subprocess.PIPE).communicate()[0].replace('"','').rstrip()
		# execute can't handle simple strings for substitution so lets put it in a tuple
		currentpath = [settings.musicfolder + "/" + unicode(currentfile, "utf-8") ]
		cursor.execute("""SELECT id FROM musiclib WHERE path==?;""",currentpath)
		idTuple = cursor.fetchall()
		if len(idTuple) == 1 :
			trackid = idTuple[0]
			if trackid != lasttrackid:
				print "## resetting votes"
				#reset ip/trackid counter
				votedb.resetVotes(trackid)	
				# reset votes for current song
				cursor.execute("""UPDATE musiclib SET votes= 0 WHERE id==?;""",(trackid))
				# set current time to last time played column
				currenttime = [time.time() , trackid[0]]
				cursor.execute("""UPDATE musiclib SET lastplayed= ? WHERE id==?;""",currenttime)
				connection.commit()
				lasttrackid = trackid
		connection.close()


def initMPD():
	retcode = subprocess.call(['mpc','-q','clear'])
	retcode = subprocess.call(['mpc','-q','crossfade','5'])
	
def manager():
	initMPD()
	while(True):
		# TODO das reset muss woanders hin, sonst haben wir staendig db zugriffe
		resetVotes()
		getTopVotedSongs()
		
		if len(currentTopSongs) > 0:
			addSongs()
			if isNotPlaying():
				startPlaylist()
			# just for debugging
			#print nowPlaying()
			# don't let the script eat up all system ressources
			time.sleep(5)	
		else:
			print "top 10 is empty! waiting for incoming votes"
			time.sleep(10)

def addSongs():
	global currentTopSongs	
	global oldCurrentTopSongs	
	# remove previous top hit in playlist, but keep playing current song
	if subprocess.Popen(['mpc','playlist'], stdout=subprocess.PIPE).communicate()[0].count('\n') >= 1 and isNotPlaying():
		retcode = subprocess.call(['mpc','-q','clear'])
	if currentTopSongs != oldCurrentTopSongs:
		print "## updating playlist"	
		if subprocess.Popen(['mpc','playlist'], stdout=subprocess.PIPE).communicate()[0].count('\n') > 1:
			retcode = subprocess.call(['mpc','-q','crop'])
		for currentSongPath in currentTopSongs:
			# make currentsongpath relative to music folder
			mpdSongPath = currentSongPath[0][len(settings.musicfolder)+1:len(currentSongPath[0])]
			retcode = subprocess.call(['mpc','-q','add',mpdSongPath])
	oldCurrentTopSongs = currentTopSongs
	currentTopSongs = []

def startPlaylist():
	retcode = subprocess.call(['mpc','-q','play'])


# lookup the song with most votes in database
def getTopVotedSongs():
	global currentTopSongs
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	# get current top songs
	cursor.execute("""SELECT path FROM musiclib WHERE votes > '0' ORDER BY votes DESC, votetime ASC LIMIT 10;""")
	currentTopSongs = cursor.fetchall()

	#print currentTopSongs	
	connection.close()
