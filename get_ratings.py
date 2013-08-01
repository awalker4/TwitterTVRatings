import urllib2
import re
import htmlentitydefs

#initial variables
flag = 0
base_url = "http://tvbythenumbers.zap2it.com/page/"
page = 1
junk = "/?s="
query = "sunday cable ratings"
for_query = "sunday+cable+ratings"
i = 0 

if __name__ == "__main__":
	while (not flag):
		response = urllib2.urlopen(base_url + str(page) + junk + for_query).read().decode('utf-8')
		
		#we're only interested in the #excerpt
		my_regex = r'\<div class\=\"excerpt\"\>\s*\<a href="([^"]*)\"\s*title\=\"' + re.escape(query)
		urls = re.findall(my_regex, response, re.I)
		
		for url in urls:
			print "opening " + url
			response = urllib2.urlopen(url).read().decode('utf-8')
			
			#first find the posting date, of the format STR_MONTH DATE{1,2}_STR, YEAR{4}
			date = re.search(r'([^\s\>]* [0-9]{1,2}\w*, [0-9]{4})', response)
			date = date.group(0)
			
			#anything between <td> tags 
			my_regex = r'\<td[^\>]*\>(.*?)\<\/td\>'
			ratings = re.findall(my_regex, response, re.I)
			
			j = 0
			k = 1						#We know there are 4 fields per tag
			output = ""
			
			for rating in ratings:
				#Basically, skip first four junk lines
				if not (j < 5):
					#Now let's strip out all the remaining HTML tags and the stupid dashes
					rating = re.sub(r'\<[^\>]*\>', '', rating)
					rating = re.sub(r'\-\s*L?', '', rating, re.I)
					rating = re.sub(r'\&amp;', '&', rating)																												#where is my CSC401 work?
					output += rating + "\t"
					if (k < 5):			#While we haven't completed a string, concantenate it
						k = k + 1
					elif (k == 5):		#Else print it out and reset
						k = 1
						print date + "\t" + output
						output = ""
						
				else:
					j = j + 1
			
			
			#we need to strip first 4 lines, and then remove html
			
		if (i == 0):
			flag = 1
			
