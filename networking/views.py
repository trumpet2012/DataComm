import urllib, os, re
from urllib2 import Request, urlopen, URLError
from operator import itemgetter
import json
from django.conf import settings
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from .models import Session, Device


def index(request):

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
    else:
        if connect_session is not None:
            device.session = connect_session
            device.save()

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
    sudo_command = ''
    if settings.IN_PRODUCTION:
        sudo_command = 'sudo '
    results = os.popen("%smtr -l %s | grep '^h'" % (sudo_command, dst)).read()  # Run the mtr command and capture the stdout
    lines = results.splitlines()  # Seperate each line of the output into its own element in an array
    # Remove the first two lines since it is just the mtr header information
    hop_list = []
    new_hop_list = []
    # Create the trace object that will hold the traceroute information
    trace = {
        'target': dst,
        'results': new_hop_list
    }

    # Loop through each line in the string results, each line represents one hop
    for line in lines:
        line_type, hop_number, ip = line.split(' ')

        hop_number = int(hop_number)
        hop_number += 1

        # Get additional information on individual hop through GeoIP API
        try:

            traceurl = 'http://geoip.nekudo.com/api/8.8.8.8/en/short'
            tracerequest = Request(traceurl)
            inforesponse = urlopen(tracerequest)
            stringinfo = json.loads(inforesponse.read())

            latitude = stringinfo['location']['latitude']
            longitude = stringinfo['location']['longitude']
            city = stringinfo['city']
            country = stringinfo['country']['name']
            timezone = stringinfo['location']['time_zone']

        except URLError, e:
            print 'No kittez. Got an error code:', e

        hop_list.append({
            'response': True,
            'hop': hop_number,
            'ip': ip,
            'city': city,
            'country': country,
            'timezone': timezone,
            'latitude': latitude,
            'longitude': longitude
        })

    hop_list = sorted(hop_list, key=itemgetter('hop'))

    hop_counter = 1
    for hop in hop_list:
        hop_difference = hop['hop'] - hop_counter
        print "diff: %s" % hop_difference
        for index_ctr in range(0, hop_difference):
            print "hit loop: %s" % index_ctr
            new_hop_list.append({
                'response': False,
                'hop': hop_counter,
                'ip': 'No response'
            })
            hop_counter += 1

        new_hop_list.append(hop)
        hop_counter += 1

    return trace
