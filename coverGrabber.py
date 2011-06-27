import pylast
import urllib2


def downloadAlbumArt(artist, album):
	"""Use last.fm for album art fetching"""
	# You have to have your own unique two values for API_KEY and API_SECRET
	# Obtain yours from http://www.last.fm/api/account for Last.fm
	API_KEY = "b25b959554ed76058ac220b7b2e0a026" # this is a sample key
	API_SECRET = "425b55975eed76058ac220b7b4e8a054"


	network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET)

	album_object = network.get_album(artist, album)
	
	# Get the url of the cover art
	try:
		cover_url = album_object.get_cover_image(size=3)
	except pylast.WSError:
		cover_url = None
	
	if cover_url != None:
		coverfile = urllib2.urlopen(cover_url)

		# Replace disallowed characters with an underscore in the artist and album parts of the filename
		disallowed = ['\\','/',':','<','>','?','*','|']
		artist_filename = artist
		album_filename = album
		for character in disallowed:
			artist_filename = artist_filename.replace(character,'_')
			album_filename = album_filename.replace(character,'_')

		output = open("images/" + '/%s_%s.%s'%(artist_filename,album_filename,cover_url.split('.')[-1]),'wb')
		output.write(coverfile.read())
		output.close()
		print "downloaded " +str(artist) +"_" +str(album) +".png"
		return True
	else:
		print "failed to find album art for: "+str(artist) +"_" +str(album)
		return False

