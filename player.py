import pygame
import time
import sqlite3

nextSongPath = ""
currentSongPath = "/home/joe/Musik/test.mp3"

def playSong( runtime ):
	
	print "\nplaying song with runtime " +str(runtime)
	pygame.mixer.init()
	pygame.mixer.music.load(currentSongPath)
	pygame.mixer.music.play()
	
	while pygame.mixer.music.get_busy():
	    time.sleep(1)
	
	print "song finshed"
