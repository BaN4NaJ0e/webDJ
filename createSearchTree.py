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
     def __init__(self, artist, song, votes, albumart):
         self.artist = artist
         self.song = song
	 self.votes = votes	
	 self.albumart = albumart
	
class SingleTrack():
	def __init__(self, artist, title, album, albumart):
		self.artist = artist
		self.title = title
		self.album = album
		self.albumart = albumart
		


# ToDO: jquery scripte offline lagern

templateDef = """
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>vote your song!</title>
	 <meta charset="utf-8">
	<link rel="stylesheet" href="http://code.jquery.com/mobile/1.0a4.1/jquery.mobile-1.0a4.1.min.css" />
	<script src="http://code.jquery.com/jquery-latest.js"></script>
	<script type="text/javascript" src="http://code.jquery.com/jquery-1.5.2.min.js"></script>
	<script type="text/javascript" src="http://code.jquery.com/mobile/1.0a4.1/jquery.mobile-1.0a4.1.min.js"></script>

</head>
<body class="index">

<div data-role="page" id="home" >
 
	 <div data-role="header">
	 <h2>App Name</h2>
	 </div><!-- /header -->

<div data-role="content">
    <ul data-role="listview" data-theme="c"> 		
	<li data-theme="e">Now Playing:
			<img src="../$current.albumart" alt="AlbumArt"> 
			<h3 class="ui-li-heading">$current.title</h3>
			<p class="ui-li-heading""> <b>$current.artist</b> </p> 
			<p class="ui-li-heading"">$current.album</p>
	</li>

	<li data-theme="e">Top 10 Songs
		<ol data-role="listview" data-theme="c">
			#for $item in $charts
			  <li>
				<img src="../$item.albumart" alt="albumart" class="ui-li-thumb">
				<h2 class="ui-li-heading"> <b>$item.artist</b> <br> <i>$item.song</i> </h2>
				<span class="ui-li-count"> <h2> $item.votes </h2> </span>
			  </li>
			#end for
		</ol>
	</li>

	<li data-theme="b">select song
		<ul data-role="listview" data-theme="d" data-filter="true">
		
		<li data-role="list-divider">choose artist</li>

	#for $artist in $artists
		<li> $artist[0] 
		<ul data-role="listview" data-theme="c">
			<li data-role="list-divider">choose album</li>	
			#for $album in $artist[1]			
					<li>
					<img src="../$album.coverpath" alt="albumart" class="ui-li-thumb">
					<h3 class="ui-li-heading">$album.name</h3>
					<p class="ui-li-desc">$album.year</p>
						<ul data-role="listview" data-theme="c">
						<li data-role="list-divider">choose song</li>						
						#for $track in $artist[2]									
						<li> 
						    <h2 class="ui-li-heading"> $track.name </h2>
						    <span class="ui-li-count">$track.votes</span>	      
						      <ul data-role="listview" data-theme="c">
							<li>
							<img src="../$album.coverpath" alt="albumart" class="ui-li-thumb">
							<h3 class="ui-li-heading">$artist[0] <br><i>$track.name</i>  </h3>
							<p class="ui-li-desc">$album.name ($album.year)</p>
							<span class="ui-li-count">$track.votes</span>
							</li>
							
							<div data-role="controlgroup" >
							<a href="../voted/?like=$track.id" data-ajax="false" data-role="button" data-icon="plus">Yeah!<br>I like it!</a>
							<a href="../voted/?hate=$track.id" data-ajax="false" data-role="button" data-icon="minus">Naah!<br>Not my taste!</a>
							<a href="../index/" rel="external" data-role="button" data-icon="delete">Cancel</a>
							</div>
							
						    </ul>
						</li>
						#end for
						</ul>
				</li>
			#end for
		</ul>				
		</li>
	#end for
	</li>
	</ul>

 </div><!-- /content -->

 <div data-role="footer">
 <h4> &copy 2011 </h4>
 </div><!-- /footer -->

</div><!-- /page -->

</body>

</html>"""

# thumbnails machen die nested liste kaputt aber warum
#					<img src="$album.coverpath/folder.jpg" class="ui-li-thumb">

def handleVote(trackid, like):
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
		if int(song[0][3]) > 0 :
			cursor.execute("""UPDATE musiclib SET votes= votes - 1 WHERE id==?;""", t )
	connection.commit()
	connection.close()
	return song

def buildHTML():
	# get current track info
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
	cursor.execute("""SELECT artist,title,votes,albumart FROM musiclib WHERE votes > '0' ORDER BY votes DESC;""")
	topvotesTuple = cursor.fetchall()

	chartList = []
	for i in topvotesTuple:	
		myChartItem = Chartitem(i[0],i[1], i[2], i[3])	
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
				myTrack = Track( str(track[0]), track[1] , track[2], track[3])
				tracks.append(myTrack)

		artistsList.append([artist[0],alben,tracks])

	#pprint.pprint(artistsList)

	nameSpace = {'charts': chartList, 'artists': artistsList, 'current': currentTrack }
	t = Template(templateDef, searchList=[nameSpace])
	#print t

	f = open('artists_gen.html', 'w')
	f.write(str(t))
	print "updated html files"
	connection.close()

