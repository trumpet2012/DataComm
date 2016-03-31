from scapy.all import *
#Test Here
#Change plee
hostname = "georgiasouthern.edu"
for i in range(1, 28):
    pkt = sr(IP(dst=hostname, ttl=i) / ICMP())
    # Send the packet and get a reply
    response = sr1(pkt, verbose=0)
    if response is None:
        # No reply =(
        continue
    elif response.type == 3:
        # We've reached our destination
        print "Done!", response.src
        break
    else:
        # We're in the middle somewhere
        print "%d hops away: " % i , response.src