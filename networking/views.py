import urllib

from django.http import HttpResponse
from django.shortcuts import render
from scapy import route
from scapy.layers.inet import IP, TCP, traceroute, ICMP
from scapy.sendrecv import sr, sr1
from scapy.volatile import RandShort

from .models import Session, Device


def index(request):
    print "Calling index"
    # ans = sr1(IP(dst="www.google.com", ttl=(1,10))/ICMP(), timeout=10)
    # print ans
    # summary = ans.summary(lambda(s, r): r.sprintf("%IP.src\t{ICMP:%ICMP.type%}\t{TCP:%TCP.flags%}"))

    connect_session_key = request.GET.get('session', None)
    connect_session = None
    if connect_session_key is not None:
        try:
            print connect_session_key
            connect_session = Session.objects.get(key=connect_session_key)
        except Session.DoesNotExist:
            return render(request, 'networking/index.html', {'error': 'Invalid session key provided.'})

    try:
        device = Device.objects.get(ip=request.ip)
    except Device.DoesNotExist:
        if connect_session is None:
            connect_session = Session.objects.create()
        device = Device.objects.create(ip=request.ip, session=connect_session)

    connect_url = "http://%s?%s" % (request.META['HTTP_HOST'], urllib.urlencode({'session': device.session.key}))
    print connect_url
    return render(request, 'networking/index.html', {
        'connect_url': connect_url
    })
