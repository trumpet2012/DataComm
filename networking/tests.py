from scapy.all import *
import os
#Test Here
dst = 'fpvmodel.com'
results = os.popen("traceroute %s -I" % dst).read()
print results
print "------------------------------------"
lines = results.splitlines()
header = lines.pop(0)
hop_list = []
trace = {
    'target': {
        'original': dst,
        'ip': header.split(dst)[1].split(',')[0].strip(' ()')
    },
    'results': hop_list
}
print header
linenumber = 1
for line in lines:
    pieces = line.split(' ')
    if linenumber < 10:
        domain = pieces[3]
        ip = pieces[4].strip('()')
    else:
        domain = pieces[2]
        ip = pieces[3].strip('()')

    if domain == '*':
        domain = "No response"
    if ip == '*':
        ip = "No response"

    hop_list.append({
        'hop': linenumber,
        'domain': domain,
        'ip': ip
    })

    print "Hop %s: %s %s" % (linenumber, domain, ip)
    linenumber += 1

print trace