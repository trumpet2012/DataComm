import urllib, os, re

from operator import itemgetter

from django.http import HttpResponse
from django.shortcuts import render

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
    source_device_ip = request.ip
    device_ids = request.POST.getlist('devices', [])
    try:
        source_device = Device.objects.get(ip=source_device_ip)
    except Device.DoesNotExist:
        return HttpResponse("Source device not found.")

    target_devices = Device.objects.filter(pk__in=device_ids)
    traces_list = []
    traces = {
        'list': traces_list
    }

    # Get the route to the source device
    source_trace = trace_device(source_device)
    source_hops = source_trace.get('results')
    num_source_hops = len(source_hops)

    for device in target_devices:
        trace = trace_device(device=device)
        node_list = trace.get('results')
        for node in node_list:
            # Increment all of the hop numbers in the destination trace
            # since we are about to add the source trace to the beginning
            node['hop'] += num_source_hops

        # Add the source trace to the beginning of the destination trace
        node_list.extend(source_hops)
        # Sort the list by the hop number
        trace['results'] = sorted(node_list, key=itemgetter('hop'))
        # Add this trace result to the list of traces being performed.
        traces_list.append(trace)

    return render(request, 'networking/trace_results.html', context={
        'traces': traces
    })


def trace_device(device):
    """
        Performs a mtr trace to the specified device.

    :param device: The device that the trace should target.
    :return a dictionary containing the results of the trace.
    """
    dst = device.ip
    results = os.popen("mtr -rwb4 %s " % dst).read()  # Run the mtr command and capture the stdout
    lines = results.splitlines()  # Seperate each line of the output into its own element in an array
    # Remove the first two lines since it is just the mtr header information
    lines.pop(0) + lines.pop(0)
    hop_list = []
    # Create the trace object that will hold the traceroute information
    trace = {
        'target': dst,
        'results': hop_list
    }
    linenumber = 1
    # Loop through each line in the string results, each line represents one hop
    for line in lines:
        response = True
        # Parse the hop line information to get the domain and ip address
        matches = re.search(r'\-\-\s((?P<domain>[a-zA-Z0-9\.\-_?]*) (?P<ip>\(?[\d\.]*\)?)?)', line)
        domain = matches.group('domain')
        ip = matches.group('ip').strip('()')

        if domain == '???':
            domain = ""
            response = False
        elif ip == "":
            # Sometimes the domain will contain the IP address and ip will be empty
            # This only happens when the domain has a value and ip does not.
            # We switch their values to fix this.
            tmp = domain
            domain = ip
            ip = tmp

        hop_list.append({
            'response': response,
            'hop': linenumber,
            'domain': domain,
            'ip': ip
        })

        linenumber += 1
    return trace
