import urllib2
import re

#initial variables
flag = 0
base_url = "http://tvbythenumbers.zap2it.com/page/"
page = 1
query = "/?s=sunday+cable+ratings"
i = 0 

if __name__ == "__main__":
	
	while (not flag):
		response = urllib2.urlopen(base_url + str(page) + query).read().decode('utf-8')
		
		urls = re.findall(r'\<div class\=\"excerpt\"\>\s*\<a href="([^"]*)\"', response)
		#we're only interested in the #excerpt
		
		for url in urls:
			print url
			
		if (i == 1):
			flag = 1
			
		i = i + 1
		page = page + 1
	
