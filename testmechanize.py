import mechanize
#url = 'http://textfiles.com/fun/acronym.txt'
#url = "https://kite.trade/connect/login?api_key=5o9woasu1obrhsj4" 
url = 'https://kite.zerodha.com/connect/login?api_key=5o9woasu1obrhsj4'
br = mechanize.Browser()
#br.set_all_readonly(False)    # allow everything to be written to
br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
#br.addheaders =   	      	# [('User-agent', 'Firefox')]
response = br.open(url)
print response.read()      # the text of the page
#response1 = br.response()  # get the response again
#print response1.read()     # can apply lxml.html.fromstring()