import pylast
import urllib2
import settings


def skipAlbumArt():
	return True

def downloadAlbumArt(artist, album):
	
	# check in settings.py album art download is enabled
	if settings.artdownload :
		"""Use last.fm for album art fetching"""
		
		API_KEY = settings.API_KEY
		API_SECRET = settings.API_SECRET
		
		network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET)
		
		album_object = network.get_album(artist, album)
	
		# Get the url of the cover art
		try:
			cover_url = album_object.get_cover_image(size=3)
		except pylast.WSError:
			# try again with new artist name / useful in case of sampler album
			album_object = network.get_album("Various Artists", album)
			try:
				cover_url = album_object.get_cover_image(size=3)
			except pylast.WSError:
				album_object = network.get_album("Various Artists", album)
				cover_url = None
			
		if cover_url != None:
			try:
				coverfile = urllib2.urlopen(cover_url)
			
			except urllib2.HTTPError:
				print "httperror"
				return False

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
				print "downloaded " +unicode(artist) +"_" +unicode(album) +".png"
				return True
		else:
			print "failed to find album art for: "+unicode(artist) +"_" +unicode(album)
			return False
			
	else :
		return False

