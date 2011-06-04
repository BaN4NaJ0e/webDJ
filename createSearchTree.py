# coding: utf-8
import sqlite3
import pprint
import mpdPlayer
from Cheetah.Template import Template

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
	return song

def buildHTML():
	# get now playing track info
    nowPlayingTuple = mpdPlayer.nowPlaying()
    if len(nowPlayingTuple) > 0:
        currentTrack = SingleTrack(nowPlayingTuple[0][0],nowPlayingTuple[0][1],nowPlayingTuple[0][2],nowPlayingTuple[0][3])
    else:
        currentTrack = SingleTrack('Artist','Title','Album','images/no-album.png')
	
	# open sqlite db connection
    connection = sqlite3.connect("mucke.db")
    cursor = connection.cursor()
	
	# abfragen aller artists ohne doppelte eintraege
    cursor.execute("""SELECT DISTINCT artist FROM musiclib;""")
    artists = cursor.fetchall()
	
	# get current top10 songs
    cursor.execute("""SELECT artist, title, votes, albumart, id FROM musiclib WHERE votes > '0' ORDER BY votes DESC LIMIT 10;""")
    topvotesTuple = cursor.fetchall()
    
    chartList = []
    for i in topvotesTuple:
        myChartItem = Chartitem(i[0],i[1], i[2], i[3], i[4])
        chartList.append(myChartItem)
    
    artistsList = []
	
	# get album names for every artist
    for artist in artists:
        #print(artist[0].encode('latin-1'))
        t = (artist[0],)
        cursor.execute("""SELECT DISTINCT album FROM musiclib WHERE artist=?;""", t )
        albenTuple = cursor.fetchall()
        alben = []
        for album in albenTuple:
			#print "  ->> "+album[0]
            t = (album[0],)
			# get path to albumart folder.jpg
            cursor.execute("""SELECT DISTINCT albumart FROM musiclib WHERE album=?;""", t )
            pathTuple = cursor.fetchall()
			# get album release year
            cursor.execute("""SELECT DISTINCT year FROM musiclib WHERE album=?;""", t )
            yearTuple = cursor.fetchall()
            myAlbum = Album(album[0].encode('latin-1'), str(pathTuple[0][0]), str(yearTuple[0][0]))
			#alben.append(album[0].encode('latin-1'))
            alben.append(myAlbum)
            
            # get all tracknames for this album
            cursor.execute("""SELECT DISTINCT title,id,votes,tracklength FROM musiclib WHERE album=?;""", t )
            trackTuple = cursor.fetchall()
            tracks = []
			#pprint.pprint( trackTuple )
            for track in trackTuple:
                myTrack = Track( track[0], track[1] , track[2], track[3])
                tracks.append(myTrack)
            
            artistsList.append([artist[0],alben,tracks])
	#pprint.pprint(artistsList)
    
    print "## updated index.html"
    # close db connection
    connection.close()
    nameSpace = {'charts': chartList, 'artists': artistsList, 'current': currentTrack }
    t= Template(file="templates/index.html", searchList=[nameSpace])
    return t
