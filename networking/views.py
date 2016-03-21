from django.http import HttpResponse
from django.shortcuts import render
from scapy import route
from scapy.layers.inet import IP, TCP, traceroute
from scapy.sendrecv import sr
from scapy.volatile import RandShort

def index(request):
    ans, unanswered = traceroute(target='www.github.com', dport=[90,443], verbose=True)
    image = ans.graph()
    help(image)
    return HttpResponse(image)
