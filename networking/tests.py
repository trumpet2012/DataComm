# NECESSARY FIXES
# CSS - don't apply after trace on to devices
# Refresh button needs to not perform trace
# Needs to be mobile friendly

# from scapy.all import *
# import os, re
# #Test Here
# dst = 'fpvmodel.com'
# results = os.popen("mtr -rwb4 %s " % dst).read()
# # print results
# # print "------------------------------------"
# lines = results.splitlines()
# # print lines
# header = lines.pop(0) + lines.pop(0)
# hop_list = []
# trace = {
#     'target': {
#         'original': dst,
#     },
#     'results': hop_list
# }
# # print header
# linenumber = 1
# for line in lines:
#     print line
#     response = True
#     matches = re.search(r'\-\-\s((?P<domain>[a-zA-Z0-9\.\-_?]*) (?P<ip>\(?[\d\.]*\)?)?)', line)
#     domain = matches.group('domain')
#     ip = matches.group('ip').strip('()')
#
#     if domain == '???':
#         domain = ''
#         response = False
#     elif ip == "":
#         # Sometimes the domain will be the IP address and the ip will be empty
#         tmp = domain
#         domain = ip
#         ip = tmp
#
#     hop_list.append({
#         'response': response,
#         'hop': linenumber,
#         'domain': domain,
#         'ip': ip
#     })
#
#     print "Hop %s: %s %s" % (linenumber, domain, ip)
#     linenumber += 1
#
# print trace
#
#
#
# ##### GEOIPAPI IMPLEMENTATION #####
# from urllib2 import Request, urlopen, URLError
# import json
# import webbrowser
#
# traceurl = 'http://geoip.nekudo.com/api/'
# mapsurl = 'http://maps.google.com/?q='
#
# try:
#     traceurl += '8.8.8.8/en/short'
#
#     request = Request(traceurl)
#     response = urlopen(request)
#     kittens = json.loads(response.read())
#
#
#     latitude = kittens['location']['latitude']
#     longitude = kittens['location']['longitude']
#     city = kittens['city']
#     country = kittens['country']['name']
#     timezone = kittens['location']['time_zone']
#     print country, city, longitude, latitude, timezone
#
# except URLError, e:
#     print 'No kittez. Got an error code:', e