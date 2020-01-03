# You can copy this file and paste it directly into ipython.
# tweak it as necessary for testing things.

# test these:
# ensure return data for voice recording is valid after json de/serialization

# tested as of 11/11/15:
# admin is not credentialed for this study (requires modifying a study)
# incorrect secret key
# admin dne
# invalid study id
# access key DNE/invalid
# user (patient) DNE/invalid
# invalid time string supplied

# API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
# slightly more human notation: YYYY-MM-DDThh:mm:ss
# (that is the letter T between date and time)
# 1990-01-31T07:30:04 gets you jan 31 1990 at 7:30:04am
# time ranges actually constrain results (note: time ranges are inclusive searches for those values)

cpaste
API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
import urllib, urllib2, locale, json
locale.setlocale(locale.LC_ALL, 'en_US')
print "\n\n"
def println(x): print x
# e = Admins()[0] #Local debugging
# access_key, secret_key = e.reset_access_credentials() #local debugging
# url = 'http://localhost:8080/get-data/v1' #local debugging
url = 'https://studies.beiwe.org/get-data/v1' #production debugging
values = {
          #REQUIRED
          'access_key' : "IWz6ABsGxx9+NrgWquIM5wbm0gE1R11pKkfPS8/xhPhZo+LoszVXudhDAfVjlVbD", #production testing for eli user
          'secret_key' : "M1w1/EldtCw0hiE7Wi6VqVNiwCNlx/41SaSGqyrsnn9mCCBDGBkF0HlSVJhP5DY1", #production testing for eli user
          # 'access_key' : access_key,
          # 'secret_key' : secret_key,
          # 'access_key' : "steve", #invalid access key
          # 'secret_key' : "steve", #incorrect secret key
          'study_id' : '55d3826297013e3a1c9b8c3e', #study id for debugging study
          # 'study_id' : 'steve', #invalid study id
          
          #OPTIONAL.  data_streams defaults to all, user_ids defaults to all in this study
          'user_ids' : json.dumps(["h6fflp"]), #user id for eli's test user
          # 'user_ids' : json.dumps(["steve"]), #invalid user (patient) id
          'data_streams' : json.dumps(["logFile"]),
          # 'data_streams' : json.dumps(["logFile"]), #the logFile is not currently chunked, use to test worse case lag
          # "data_streams": json.dumps(['accel'])#,'bluetoothLog','callLog','gps','identifiers','powerState','surveyTimings','textsLog']),
          # "data_streams": json.dumps(['bluetoothLog','callLog','gps','identifiers','powerState','surveyTimings','textsLog']),
          # 'time_start': "aoeukea", #invalid time string
          'time_start': "2015-09-17T20:00:00",
          'time_end': "2015-09-25T20:00:00",
          }

req = urllib2.Request(url, urllib.urlencode(values))
response = urllib2.urlopen(req)
page = response.read()
data = json.loads(page)
#if you get html return print out html but exclude lines consisting of only whitespace
if page[:15] == "<!DOCTYPE html>":
	[println(line) for line in page.splitlines() if not line.isspace() and line]
else:
	#when return data is in the correct form from the api call, print out the length of the data.
	print "total size:", locale.format("%d", sum(len(key) + len(item) for key, item in data.items() ), grouping=True)
--

