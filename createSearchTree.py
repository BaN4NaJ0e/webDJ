# coding: utf-8
import sqlite3
import pprint
import mpdPlayer
from Cheetah.Template import Template
import votedb
import time
import settings


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

# now playing track info
class SingleTrack():
	def __init__(self, artist, title, album, albumart, runtime):
		self.artist = artist
		self.title = title
		self.album = album
		self.albumart = albumart
		self.runtime = runtime
		
class Historyitem:
	def __init__(self, artist, songtitle, album, albumart, lastplayed):
		self.artist = artist
		self.songtitle = songtitle
		self.album = album
		self.albumart = albumart
		self.lastplayed = lastplayed
		

# check and put incoming song vote from user into db
# returncodes 
# 0 = vote eingetrage
# 1 = user hat schon für diesen song gestimmt
# 2 = song ist noch für neue votes gesperrt, weil er erst gespielt wurde
def handleVote(trackid, like, ip):
	# check if user with certain ip has already voted for this song
	if votedb.checkQuota(trackid, ip) :
		# open sqlite db connection
		connection = sqlite3.connect("mucke.db")
		cursor = connection.cursor()
		timestamp = time.time()
		t = (trackid,)
		cursor.execute("""SELECT votes, lastplayed FROM musiclib WHERE id=?;""", t )
		song = cursor.fetchall()
		
		# timeDela in minutes = current time - lastplayed time 
		timeDelta = ( int( timestamp ) - int(song[0][1]) ) / 60
		print "played minutes ago: " +str(timeDelta)
		blockTime = settings.repeatTime - timeDelta
		if timeDelta < settings.repeatTime :
			# song was already played in the last xx minutes
			return (2, blockTime)
		
		#de-/increase number of votes for song with certain id
		if like:
			cursor.execute("""UPDATE musiclib SET votes= votes + 1, votetime=? WHERE id==?;""", (timestamp,trackid) )
		else:
			# keine negative votezahl zulassen
			if int(song[0][0]) > 0 :
				cursor.execute("""UPDATE musiclib SET votes= votes - 1, votetime=? WHERE id==?;""", (timestamp,trackid) )
		connection.commit()
		connection.close()

		# put userip/trackid/timestamp in votedb	
		votedb.insertVote(trackid, ip)
		return ( 0, 0 )
	else:
		# this user has already voted for this song
		return (1, 1)

# get html with all available artists
def buildArtists():
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	#Todo: add numbers too
	alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
	
	artists = []
	
	# get all artist starting with numbers in the name
	cursor.execute(""" SELECT DISTINCT artist FROM musiclib WHERE artist LIKE '1%' 
											  OR artist LIKE '2%'
											  OR artist LIKE '3%'
											  OR artist LIKE '4%'
											  OR artist LIKE '5%'
											  OR artist LIKE '6%'
											  OR artist LIKE '7%'
											  OR artist LIKE '8%'
											  OR artist LIKE '9%'
											  OR artist LIKE '0%'; """)
	artistsTupel = cursor.fetchall()
	
	artistGroup = ["123",[]]
	
	for artist in artistsTupel:
			artistGroup[1].append(artist[0].encode('utf-8', 'replace'))

	if len(artistGroup[1])  > 0 :
		artists.append(artistGroup)
	
	for letter in alphabet:
		
		# all artist with same beginning letter
		artistGroup = [letter,[]]
	
		# abfragen aller artists ohne doppelte eintraege
		cursor.execute("""SELECT DISTINCT artist FROM musiclib WHERE artist LIKE '""" +letter +"""%';""")
		artistsTupel = cursor.fetchall()
		
		for artist in artistsTupel:
			artistGroup[1].append(artist[0].encode('utf-8', 'replace'))
		
		# only add alphebetical groups with artists
		if len(artistGroup[1])  > 0 :
			artists.append(artistGroup)
		
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
		cursor.execute("""SELECT DISTINCT title,id,votes,tracklength FROM musiclib WHERE album=? AND artist=? ORDER BY id ASC;""", alb )
		albumtracksTuple = cursor.fetchall()
		tracks = []
		#pprint.pprint( albumtracksTuple )
		for track in albumtracksTuple:
			myTrack = Track( track[0].encode('utf-8', 'replace'),	# title
							 track[1] ,								# track id
							 track[2],								# votes
							 track[3])								# tracklength
			tracks.append(myTrack)
		
		releaseYear = resultTupel[0][1]
		
		# if no release year was found set it to palceholder
		if releaseYear ==  None:
			releaseYear = "-"
		else :
			releaseYear = resultTupel[0][1].encode('utf-8', 'replace')
		
		myAlbum = Album(album[0].encode('utf-8', 'replace'),			# album name
						resultTupel[0][0].encode('utf-8', 'replace'),	# coverpath
						releaseYear,									# album release year
						tracks )										# all album tracks
		alben.append(myAlbum)
		
	# close db connection
	connection.close()
	
	artistname = artistname.encode('utf-8', 'replace')
	
	nameSpace = {'alben': alben, 'artist': artistname}
	t= Template(file="templates/alben.html", searchList=[nameSpace])
	
	print "## created songtree for: "+ artistname
	return t

# build seachpage html
def buildSearchpage():
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	##############################
	# get all artists
	##############################
	cursor.execute("""SELECT DISTINCT artist FROM musiclib ;""")
	artistsTuple = cursor.fetchall()
	
	artistList = []
	
	for i in artistsTuple:
		artistList.append(i[0].encode('utf-8', 'replace'))
	
	# close db connection
	connection.close()
	
	nameSpace = {'artists': artistList }
	t= Template(file="templates/search.html", searchList=[nameSpace])
	
	print "## build search.html"
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
		timeDelta =  int( round((time.time()-float(i[4]))/60) )
		
		myHistoryItem = Historyitem(i[0].encode('utf-8', 'replace'), #artist
									i[1].encode('utf-8', 'replace'), #songtitle
									i[2].encode('utf-8', 'replace'), #album
									i[3].encode('utf-8', 'replace'), #albumart
									timeDelta)						 #lastplayed
		historyList.append(myHistoryItem)
	
	# remove item that is playing now from list
	if len(historyList) > 1 and not mpdPlayer.isNotPlaying(): 
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
		# runtime conversion from seconds to min:sec
		minutes = int(nowPlayingTuple[0][4]) / 60
		seconds = int(nowPlayingTuple[0][4]) % 60
		if seconds < 9:
			runtime = str(minutes) + ":0" + str(seconds)
		else:
			runtime = str(minutes) + ":" + str(seconds)
			
		currentTrack =  SingleTrack(nowPlayingTuple[0][0].encode('utf-8', 'replace'), #artist
									nowPlayingTuple[0][1].encode('utf-8', 'replace'), #title
									nowPlayingTuple[0][2].encode('utf-8', 'replace'), #album
									nowPlayingTuple[0][3].encode('utf-8', 'replace'), #albumart path
									runtime)											# runtime
	else:
		currentTrack = SingleTrack('Artist','Title','Album','images/no-album.png', "0:00")
	
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	##############################
	# get current top10 voted songs
	##############################
	cursor.execute("""SELECT artist, title, votes, albumart, id FROM musiclib WHERE votes > '0' ORDER BY votes DESC, votetime ASC LIMIT 10;""")
	topvotesTuple = cursor.fetchall()
	
	chartList = []
	for i in topvotesTuple:
		myChartItem = Chartitem(i[0].encode('utf-8', 'replace'), # artist
								i[1].encode('utf-8', 'replace'), # title
								i[2], 							 # votes
								i[3].encode('utf-8', 'replace'), # albumartpath
								i[4])							 # id
		chartList.append(myChartItem)
	
	# close db connection
	connection.close()
	
	nameSpace = {'charts': chartList, 'current': currentTrack }
	t= Template(file="templates/index.html", searchList=[nameSpace])
	
	print "## updated index.html"
	return t
