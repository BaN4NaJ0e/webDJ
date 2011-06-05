# coding: utf-8
import sqlite3
import pprint
import mpdPlayer
from Cheetah.Template import Template
import votedb

class Album:
	def __init__(self, name, coverpath, year):
		self.name = name
		self.coverpath = coverpath
		self.year = year

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


def handleVote(trackid, like, ip):
	# check if user has enough votes left
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

def buildHTML():
	# get now playing track info from mpd
	nowPlayingTuple = mpdPlayer.nowPlaying()
	if len(nowPlayingTuple) > 0:
		currentTrack = SingleTrack(nowPlayingTuple[0][0],nowPlayingTuple[0][1],nowPlayingTuple[0][2],nowPlayingTuple[0][3])
	else:
		currentTrack = SingleTrack('Artist','Title','Album','images/no-album.png')
	
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	# get current top10 voted songs
	cursor.execute("""SELECT artist, title, votes, albumart, id FROM musiclib WHERE votes > '0' ORDER BY votes DESC LIMIT 10;""")
	topvotesTuple = cursor.fetchall()
	
	chartList = []
	for i in topvotesTuple:
		myChartItem = Chartitem(i[0],i[1], i[2], i[3], i[4])
		chartList.append(myChartItem)
	
	####################
	# REQUEST SONG TREE
	####################
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
			myAlbum = Album(album[0].encode('latin-1'), str(resultTupel[0][0]), str(resultTupel[0][1]))
			alben.append(myAlbum)
			
			# get all tracks for each album
			cursor.execute("""SELECT DISTINCT title,id,votes,tracklength FROM musiclib WHERE album=?;""", t )
			trackTuple = cursor.fetchall()
			tracks = []
			#pprint.pprint( trackTuple )
			for track in trackTuple:
				myTrack = Track( track[0], track[1] , track[2], track[3])
				tracks.append(myTrack)
			
		# add all informations to tree
		requestSongTree.append([artist[0],alben,tracks])
	pprint.pprint(requestSongTree)
	
	# close db connection
	connection.close()
	
	nameSpace = {'charts': chartList, 'artists': requestSongTree, 'current': currentTrack }
	t= Template(file="templates/index.html", searchList=[nameSpace])
	
	print "## updated index.html"
	return t
