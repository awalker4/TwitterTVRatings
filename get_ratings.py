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

#Handles the command line arguments and returns them in a useful format
def handle_args():
	if (len(sys.argv) < 2):
		print "Usage... getratings.py DAY_OF_WEEK <opt> STOP_DATE (MM/DD/YYYY)"
		exit(1)
	else:
		dow = sys.argv[1]
		query = sys.argv[1] + " cable ratings"
		formatted_query = re.sub(r'\s+', '+', query)		
		stop_date = 1
		
		if (len(sys.argv) == 3):
			try:
				stop_date = time.strptime(sys.argv[2], "%m/%d/%Y")
			except:
				print "Please supply the date in the format MM/DD/YYYY..."
				exit(1)
		else:
			stop_date = time.strptime('1/1/1900', "%m/%d/%Y")
			
		return dow, query, formatted_query, stop_date

		
#Takes a date of the form July 31st, 2001 (as supplied by tvbtn) and converts it to the form 07/31/2001
#We "presume" that if the query was for "Sunday" that the implied Sunday will be the first occurrence before my_time
#Also returns a struct so that we can compare dates for termination		
def format_site_date(posting_time, day_of_week):
	posting_time = re.sub('([0-9]+)[a-zA-Z]+', '\\1', posting_time)		#Strip any character after the date, ie July 1st => July 1
	posting_struct = time.strptime(posting_time, "%B %d, %Y")		#Create a struct of the requisite files [tm_wday contains DOW, and tm_yday contains position in year]
	query_time = time.strptime(day_of_week, "%A")				#Sunday is being parsed as 6th day of the week, specs say it should be 0....
	
	if not(query_time.tm_wday == posting_struct.tm_wday):
		diff = (posting_struct.tm_wday - query_time.tm_wday) % 7

		last_year = posting_struct.tm_year
		try:								#Try just naively subtracting the time difference
			posting_struct = time.strptime(str(posting_struct.tm_yday - diff) + " " + str(last_year), "%j %Y")
		except:
			#If we roll over a year....
			last_year = str(last_year - 1)
			remainder = diff - posting_struct.tm_yday
			last_year_days = time.strptime('12 31 ' + last_year,  "%m %d %Y")
			posting_struct = time.strptime(str(last_year_days.tm_yday - remainder) + " " + last_year, "%j %Y")		
			
	display_time = time.strftime("%m/%d/%Y", posting_struct)	#Format it back to MM/DD/YYYY

	return display_time, posting_struct
	
	
if __name__ == "__main__":
	
	reload(sys)
	sys.setdefaultencoding('utf-8')
	
	dow, query, formatted_query, stop_date = handle_args()
	
	while (not flag):
		try:
			response = urllib2.urlopen(base_url + str(page) + junk + formatted_query).read().decode('utf-8')
		except:
			#404 will throw an error for urllib2
			flag = 1
			break

		#we're only interested in the #excerpt
		my_regex = r'\<div class\=\"excerpt\"\>\s*\<a href="([^"]*)\"\s*title\=\"' + re.escape(query)
		urls = re.findall(my_regex, response, re.I)
		
		for url in urls:
		
			response = urllib2.urlopen(url).read().decode('utf-8')
			
			#first find the posting date, of the format STR_MONTH DATE{1,2}_STR, YEAR{4}
			date = re.search(r'\<p\>\s*([^\s\>]* [0-9]{1,2}\w*, [0-9]{4})\<', response)
			date = date.group(1)
			
			display_date, date_struct = format_site_date(date, dow)
			
			#Check we haven't passed our stop date
			if (date_struct < stop_date):
				flag = 1
				break
			
			#anything between <td> tags 
			my_regex = r'\<td[^\>]*\>(.*?)\<\/td\>'
			ratings = re.findall(my_regex, response, re.I)
			
			j = 0
			k = 0					#We know there are 4 fields per tag
			output = ""
			
			for rating in ratings:
				#Basically, skip first four junk lines laying out the table headings
				if not (j < 5):
					#Now let's strip out all the remaining HTML tags and the stupid dashes...and replace &amp;....
					rating = re.sub(r'\<[^\>]*\>', '', rating)
					rating = re.sub(r'\-\s*L?', '', rating, re.I)
					rating = re.sub(r'\&amp;', '&', rating)													#where is my CSC401 work?
					output += rating + "\t"
					if (k < 4):		#While we haven't completed a string, concantenate it
						k = k + 1
					elif (k == 4):		#Else print it out and reset
						k = 0
						print display_date + "\t" + output
						output = ""
						
				else:
					j = j + 1
			
		page = page + 1
			
