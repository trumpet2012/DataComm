import urllib

from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from scapy.all import *
from scapy import route
from scapy.layers.inet import IP, TCP, traceroute, ICMP
from scapy.sendrecv import sr, sr1
from scapy.volatile import RandShort
from .models import Session, Device


def index(request):
    # ans = sr1(IP(dst="www.google.com", ttl=(1,10))/ICMP(), timeout=10)
    # print ans
    # summary = ans.summary(lambda(s, r): r.sprintf("%IP.src\t{ICMP:%ICMP.type%}\t{TCP:%TCP.flags%}"))

    connect_session_key = request.GET.get('session', None)
    connect_session = None
    if connect_session_key is not None:
        try:
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
    return render(request, 'networking/index.html', {
        'connect_url': connect_url,
        'session_key': device.session.key,
    })


def device_listing(request):
    """
        Ajax view for listing all devices attached to the specified session. Session key must be passed as a
        get parameter.
    """
    devices = []
    my = None

    connect_session_key = request.GET.get('session', None)
    if connect_session_key is not None:
        try:
            connect_session = Session.objects.get(key=connect_session_key)
        except Session.DoesNotExist:
            pass
        else:
            devices = Device.objects.filter(session=connect_session).exclude(ip=request.ip)
            try:
                my = Device.objects.get(session=connect_session, ip=request.ip)
            except Device.DoesNotExist:
                pass

    return render(request, 'networking/device_listing.html', context={
        'devices': devices, 'my': my
    })


