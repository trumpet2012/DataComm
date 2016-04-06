from scapy.all import *
import os, re
#Test Here
dst = 'fpvmodel.com'
results = os.popen("mtr -rwb4 %s " % dst).read()
# print results
# print "------------------------------------"
lines = results.splitlines()
# print lines
header = lines.pop(0) + lines.pop(0)
hop_list = []
trace = {
    'target': {
        'original': dst,
    },
    'results': hop_list
}
# print header
linenumber = 1
for line in lines:
    print line
    response = True
    matches = re.search(r'\-\-\s((?P<domain>[a-zA-Z0-9\.\-_?]*) (?P<ip>\(?[\d\.]*\)?)?)', line)
    domain = matches.group('domain')
    ip = matches.group('ip').strip('()')

    if domain == '???':
        domain = ''
        response = False
    elif ip == "":
        # Sometimes the domain will be the IP address and the ip will be empty
        tmp = domain
        domain = ip
        ip = tmp

    hop_list.append({
        'response': response,
        'hop': linenumber,
        'domain': domain,
        'ip': ip
    })

    print "Hop %s: %s %s" % (linenumber, domain, ip)
    linenumber += 1

print trace

