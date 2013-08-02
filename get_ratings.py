import urllib2
import re
import htmlentitydefs			#so yeah, need to use this...
import sys
import time

#initial variables
flag = 0
base_url = "http://tvbythenumbers.zap2it.com/page/"
page = 1
junk = "/?s="
i = 0 


#Handles the command line arguments and returns them in a useful format
def handle_args():
	if (len(sys.argv) < 2):
		print "Usage... getratings.py DAY_OF_WEEK <opt> STOP_DATE (MM/DD/YY)"
		exit(1)
	else:
		dow = sys.argv[1]
		query = sys.argv[1] + " cable ratings"
		formatted_query = re.sub(r'\s+', '+', query)		
		stop_date = ""
		return dow, query, formatted_query, stop_date

		
#Takes a date of the form July 31st, 2001 (as supplied by tvbtn) and converts it to the form 07/31/2001
#We "presume" that if the query was for "Sunday" that the implied Sunday will be the first occurrence before my_time
#Also returns a struct so that we can compare dates for termination		
def format_site_date(my_time, day_of_week):
	my_time = re.sub('([0-9]+)[a-zA-Z]+', '\\1', my_time)		#Strip any character after the date, ie July 1st => July 1
	my_time_struct = time.strptime(my_time, "%B %d, %Y")		#Create a struct of the requisite files [tm_wday contains DOW, and tm_yday contains position in year]
	query_time = time.strptime(day_of_week, "%A")				#Sunday is being parsed as 6th day of the week, specs say it should be 0....
	if not(query_time.tm_wday == my_time_struct.tm_wday):
		diff = my_time_struct.tm_wday + 1
		print diff
		print query_time, query_time.tm_wday
		print my_time_struct, my_time_struct.tm_wday
		try:													#Try just naively subtracting the time difference
			my_time_struct = time.strptime(str(my_time_struct.tm_yday - diff) + " " + str(my_time_struct.tm_year), "%j %Y")
		except:
			#This is still borked
			#if we cross over a year it is gonna fail :(
			#
			print my_time_struct.tm_yday, diff, str(my_time_struct.tm_yday - diff)
			my_time_struct = time.strptime(str(my_time_struct.tm_yday - diff) + " " + str(my_time_struct.tm_year - 1), "%j %Y")		
	display_time = time.strftime("%m/%d/%Y", my_time_struct)	#Format it back to MM/DD/YYYY
	return display_time, my_time_struct
	
	
if __name__ == "__main__":
	dow, query, formatted_query, stop_date = handle_args()
	#date = "July 31rd, 2013"

	while (not flag):
		response = urllib2.urlopen(base_url + str(page) + junk + formatted_query).read().decode('utf-8')
		
		#we're only interested in the #excerpt
		my_regex = r'\<div class\=\"excerpt\"\>\s*\<a href="([^"]*)\"\s*title\=\"' + re.escape(query)
		urls = re.findall(my_regex, response, re.I)
		
		for url in urls:
			#print "opening " + url
			response = urllib2.urlopen(url).read().decode('utf-8')
			
			#first find the posting date, of the format STR_MONTH DATE{1,2}_STR, YEAR{4}
			date = re.search(r'([^\s\>]* [0-9]{1,2}\w*, [0-9]{4})', response)
			date = date.group(0)
			display_date, date_struct = format_site_date(date, dow)
			
			#anything between <td> tags 
			my_regex = r'\<td[^\>]*\>(.*?)\<\/td\>'
			ratings = re.findall(my_regex, response, re.I)
			
			j = 0
			k = 1					#We know there are 4 fields per tag
			output = ""
			
			for rating in ratings:
				#Basically, skip first four junk lines
				if not (j < 5):
					#Now let's strip out all the remaining HTML tags and the stupid dashes...and replace &amp;....
					rating = re.sub(r'\<[^\>]*\>', '', rating)
					rating = re.sub(r'\-\s*L?', '', rating, re.I)
					rating = re.sub(r'\&amp;', '&', rating)													#where is my CSC401 work?
					output += rating + "\t"
					if (k < 5):		#While we haven't completed a string, concantenate it
						k = k + 1
					elif (k == 5):		#Else print it out and reset
						k = 1
						print display_date + "\t" + output
						output = ""
						
				else:
					j = j + 1
			
		#Just read 1st page for the moment
		if (i == 1):
			flag = 1
			
		i = i + 1
		page = page + 1
			
