# coding: utf-8
import sqlite3
import pprint
import mpdPlayer
from Cheetah.Template import Template
import votedb
import time

class Album:
	def __init__(self, name, coverpath, year, tracks):
		self.name = name
		self.coverpath = coverpath
		self.year = year
		self.tracks = tracks

class Track:
	def __init__(self, name, trackid, votes, runtime):
		self.name = name
		self.id = trackid
		self.votes = votes
		self.runtime = runtime

class Chartitem:
	def __init__(self, artist, song, votes, albumart, trackid):
		self.artist = artist
		self.song = song
		self.votes = votes
		self.albumart = albumart
		self.id = trackid

class SingleTrack():
	def __init__(self, artist, title, album, albumart):
		self.artist = artist
		self.title = title
		self.album = album
		self.albumart = albumart
		
class Historyitem:
	def __init__(self, artist, songtitle, album, albumart, lastplayed):
		self.artist = artist
		self.songtitle = songtitle
		self.album = album
		self.albumart = albumart
		self.lastplayed = lastplayed

# put incoming song vote from user into db
def handleVote(trackid, like, ip):
	# check if user has already voted for this song
	if votedb.checkQuota(trackid, ip):
		# open sqlite db connection
		connection = sqlite3.connect("mucke.db")
		cursor = connection.cursor()
		t = (trackid,)
		cursor.execute("""SELECT  artist,title,album,votes FROM musiclib WHERE id=?;""", t )
		song = cursor.fetchall()
		#de-/increase number of votes for song with certain id
		if like:
			cursor.execute("""UPDATE musiclib SET votes= votes + 1 WHERE id==?;""", t )
		else:
			# keine negative votezahl zulassen
			if int(song[0][3]) > 0 :
				cursor.execute("""UPDATE musiclib SET votes= votes - 1 WHERE id==?;""", t )
		connection.commit()
		connection.close()

		# put userip/trackid/timestamp in votedb	
		votedb.insertVote(trackid, ip)
		return True
	else: 
		return False

# get html with all available artists
def buildArtists():
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	# abfragen aller artists ohne doppelte eintraege
	cursor.execute("""SELECT DISTINCT artist FROM musiclib;""")
	artistsTupel = cursor.fetchall()
	
	artists = []
	
	for artist in artistsTupel:
		artists.append(artist[0])
	
	# close db connection
	connection.close()
	
	nameSpace = {'artists': artists}
	t= Template(file="templates/artists.html", searchList=[nameSpace])
	
	print "## updated artists.html"
	return t

# get all albums and tracks for the given artist
def buildAlben(artistname):
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	t = (artistname,)
	# frage vom künstler alle alben ab
	cursor.execute("""SELECT DISTINCT album FROM musiclib WHERE artist=?;""", t )
	albenTuple = cursor.fetchall()
	alben = []
	
	# von jedem album die tracks abfragen
	for album in albenTuple:
		t = (album[0],)
		# get path to albumart folder.jpg and release year
		cursor.execute("""SELECT DISTINCT albumart, year FROM musiclib WHERE album=?;""", t )
		resultTupel = cursor.fetchall()
		
		# get all tracks for each album
		alb = (album[0],artistname)
		cursor.execute("""SELECT DISTINCT title,id,votes,tracklength FROM musiclib WHERE album=? AND artist=?;""", alb )
		albumtracksTuple = cursor.fetchall()
		tracks = []
		#pprint.pprint( albumtracksTuple )
		for track in albumtracksTuple:
			#				title , 	id , 		votes, 	tracklength
			myTrack = Track( track[0], track[1] , track[2], track[3])
			tracks.append(myTrack)
		
		#						name					coverpath				year				all tracks
		myAlbum = Album(album[0].encode('latin-1'), str(resultTupel[0][0]), str(resultTupel[0][1]), tracks )
		alben.append(myAlbum)
		
	# close db connection
	connection.close()
	
	nameSpace = {'alben': alben, 'artist': artistname}
	t= Template(file="templates/alben.html", searchList=[nameSpace])
	
	print "## created songtree for: "+ artistname
	return t

##############################
# alte methode die gesamten baum abfragt! laaangsaaam
##############################

# build request song html
def buildRequest():
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	# abfragen aller artists ohne doppelte eintraege
	cursor.execute("""SELECT DISTINCT artist FROM musiclib;""")
	artists = cursor.fetchall()
	
	requestSongTree = []
	
	# get all album names for every single artist
	for artist in artists:
		t = (artist[0],)
		# frage von jedem künstler alle alben ab
		cursor.execute("""SELECT DISTINCT album FROM musiclib WHERE artist=?;""", t )
		albenTuple = cursor.fetchall()
		alben = []
		for album in albenTuple:
			t = (album[0],)
			# get path to albumart folder.jpg and release year
			cursor.execute("""SELECT DISTINCT albumart, year FROM musiclib WHERE album=?;""", t )
			resultTupel = cursor.fetchall()
			
			# get all tracks for each album
			alb = (album[0],artist[0])
			cursor.execute("""SELECT DISTINCT title,id,votes,tracklength FROM musiclib WHERE album=? AND artist=?;""", alb )
			albumtracksTuple = cursor.fetchall()
			tracks = []
			#pprint.pprint( albumtracksTuple )
			for track in albumtracksTuple:
				#				title , 	id , 		votes, 	tracklength
				myTrack = Track( track[0], track[1] , track[2], track[3])
				tracks.append(myTrack)
			
			#						name					coverpath				year				all tracks
			myAlbum = Album(album[0].encode('latin-1'), str(resultTupel[0][0]), str(resultTupel[0][1]), tracks )
			alben.append(myAlbum)
			
			
		# add all informations to tree
		requestSongTree.append([artist[0], alben])
		
	# close db connection
	connection.close()
	
	nameSpace = {'artists': requestSongTree}
	t= Template(file="templates/request.html", searchList=[nameSpace])
	
	print "## updated index.html"
	return t


# build playlist history html
def buildHistory():
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	##############################
	# get last 10 played songs
	##############################
	cursor.execute("""SELECT artist, title, album, albumart, lastplayed FROM musiclib WHERE lastplayed > '0' ORDER BY lastplayed DESC LIMIT 10;""")
	historyTuple = cursor.fetchall()
	
	historyList = []
	
	for i in historyTuple:
		# calculate time between now and moment song was played
		timeDelta =  int( time.time()-float(i[4]) )
		timeDelta = timeDelta / 60
		#  artist, songtitle, album, albumart, lastplayed
		myHistoryItem = Historyitem(i[0],i[1], i[2], i[3], timeDelta)
		historyList.append(myHistoryItem)
	
	# remove item that is playing now from list
	if len(historyList) > 1: 
		historyList.pop(0)
	
	# close db connection
	connection.close()
	
	nameSpace = {'history': historyList }
	t= Template(file="templates/history.html", searchList=[nameSpace])
	
	print "## updated history.html"
	return t

# build main page
def buildIndex():
	##############################
	# get now playing track info from mpd
	##############################
	nowPlayingTuple = mpdPlayer.nowPlaying()
	if len(nowPlayingTuple) > 0:
		currentTrack = SingleTrack(nowPlayingTuple[0][0],nowPlayingTuple[0][1],nowPlayingTuple[0][2],nowPlayingTuple[0][3])
	else:
		currentTrack = SingleTrack('Artist','Title','Album','images/no-album.png')
	
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	##############################
	# get current top10 voted songs
	##############################
	cursor.execute("""SELECT artist, title, votes, albumart, id FROM musiclib WHERE votes > '0' ORDER BY votes DESC LIMIT 10;""")
	topvotesTuple = cursor.fetchall()
	
	chartList = []
	for i in topvotesTuple:
		myChartItem = Chartitem(i[0],i[1], i[2], i[3], i[4])
		chartList.append(myChartItem)
	
	# close db connection
	connection.close()
	
	nameSpace = {'charts': chartList, 'current': currentTrack }
	t= Template(file="templates/index.html", searchList=[nameSpace])
	
	print "## updated index.html"
	return t
