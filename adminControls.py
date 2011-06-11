# coding: utf-8
import sqlite3



# set number of votes for all songs back to 0
def resetAllVotes() :
		
		# open sqlite db connection
		connection = sqlite3.connect("mucke.db")
		cursor = connection.cursor()
		cursor.execute("""UPDATE musiclib SET votes= 0 ;""")
		connection.commit()
		
		# close db connection
		connection.close()
		print "## reset all votes to zero!"


# set number of votes for all songs back to 0
def resetLastPlayed() :
		
		# open sqlite db connection
		connection = sqlite3.connect("mucke.db")
		cursor = connection.cursor()
		cursor.execute("""UPDATE musiclib SET lastplayed = 0, votetime = 0 ;""")
		connection.commit()
		
		# close db connection
		connection.close()
		print "## reset lastPlayed to zero!"

