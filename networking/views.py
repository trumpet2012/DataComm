import urllib, os

from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
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
    connect_session_key = request.GET.get('session', None)
    if connect_session_key is not None:
        try:
            connect_session = Session.objects.get(key=connect_session_key)
        except Session.DoesNotExist:
            pass
        else:
            devices = Device.objects.filter(session=connect_session)

    return render(request, 'networking/device_listing.html', context={
        'devices': devices
    })


def trace(request):
    """
        Perform a traceroute to the selected devices. Uses the linux traceroute to do the tracing.
    """
    source_device = request.ip
    device_ids = request.POST.getlist('devices', [])
    target_devices = Device.objects.filter(pk__in=device_ids)
    traces_list = []
    traces = {
        'list': traces_list
    }
    for device in target_devices:
        dst = device.ip
        results = os.popen("traceroute %s -I" % dst).read()  # Run the traceroute command and capture the stdout
        lines = results.splitlines()  # Seperate each line of the output into its own element in an array
        header = lines.pop(0)  # Remove the first element since it is just the traceroute default first line information
        hop_list = []
        # Create the trace object that will hold the traceroute information
        trace = {
            'target': {
                'original': dst,
                'ip': header.split(dst)[1].split(',')[0].strip(' ()')  # Get the ip address of the target device
            },
            'results': hop_list
        }
        linenumber = 1
        # Loop through each line in the string results, each line represents one hop
        for line in lines:
            # Each line contains all of the hop information separated by spaces, so remove them to get each piece
            # of information
            pieces = line.split(' ')
            # There is an extra space for hops below 10 in order for the single hop numbers to align correctly with
            # the double digit hop numbers. This causes the index values for the ip and domain to be different
            # for hops below 10.
            if linenumber < 10:
                domain = pieces[3]
                ip = pieces[4]
            else:
                domain = pieces[2]
                ip = pieces[3]

            # The IP address for the hop is wrapped in parenthesis so remove them.
            ip = ip.strip('()')

            # Change all star responses to say "No Response" instead.
            if domain == '*':
                domain = "No response"
            if ip == '*':
                ip = "No response"

            # Add this hop information to the list of all hops for this trace
            hop_list.append({
                'hop': linenumber,
                'domain': domain,
                'ip': ip
            })

            linenumber += 1

        # Add this trace result to the list of traces being performed.
        traces_list.append(trace)

    return render(request, 'networking/trace_results.html', context={
        'traces': traces
    })
