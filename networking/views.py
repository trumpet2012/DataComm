import urllib, os
from urllib2 import Request, urlopen, URLError
from operator import itemgetter
import json
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from .models import Session, Device, TraceHistory


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
    connect_session_key = request.POST.get('session', None)
    device_name = request.POST.get('deviceName', None)
    my_device_ip = request.POST.get('myDeviceIp', request.ip)

    device_kwargs = {
        'ip': my_device_ip,
        'defaults': {
            'name': device_name,
        },
    }
    connect_session = None
    if connect_session_key is not None:
        try:
            connect_session = Session.objects.get(key=connect_session_key)
        except Session.DoesNotExist:
            pass
        else:
            device_kwargs['defaults']['session'] = connect_session

    current_device, created = Device.objects.get_or_create(**device_kwargs)

    if not created and not current_device.ip == request.ip:
        current_device.ip = request.ip

    if device_name is not None and not current_device.name == device_name:
        current_device.name = device_name

    try:
        current_device.save()
    except IntegrityError:
        current_device = Device.objects.get(ip=request.ip)

        if connect_session:
            current_device.session = connect_session
            current_device.save()

    devices = Device.objects.filter(session=current_device.session).exclude(ip=my_device_ip)

    return render(request, 'networking/device_listing.html', context={
        'devices': devices, 'current_device': current_device
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

    for hop_counter in range(0, num_source_hops):
        # Loop through and flip all of the hop numbers so that we effectively reverse
        # the perspective of the traceroute
        source_hops[hop_counter]['hop'] = num_source_hops - hop_counter

    for device in target_devices:
        device_trace = trace_device(device=device)
        node_list = device_trace.get('results')
        for node in node_list:
            # Increment all of the hop numbers in the destination trace
            # since we are about to add the source trace to the beginning
            node['hop'] += num_source_hops

        # Add the source trace to the beginning of the destination trace
        node_list.extend(source_hops)

        # Sort the list by the hop number
        device_trace['results'] = sorted(node_list, key=itemgetter('hop'))
        # Add this trace result to the list of traces being performed.
        traces_list.append(device_trace)

        #create TraceHistory object
        TraceHistory.objects.create(source=source_device, destination=device, session=source_device.session, hops=json.dumps(device_trace['results']))


    return render(request, 'networking/trace_results.html', context={
        'tracesjson':   json.dumps(traces), 'traces': traces
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
        hop_response = {}
        line_type, hop_number, ip = line.split(' ')

        hop_number = int(hop_number)
        hop_number += 1

        hop_response.update({
            'response': True,
            'hop': hop_number,
            'ip': ip,
        })
        api_key = 'ab27fe914126e5049df74f35caac7ff84888921adc682dd704112261facf4f62'
        #Get additional information on individual hop through GeoIP API
        try:
            traceurl = 'http://api.ipinfodb.com/v3/ip-city/?key=%s&ip=%s&format=json' % (api_key, ip)
            tracerequest = Request(traceurl)
            inforesponse = urlopen(tracerequest)
            stringinfo = json.loads(inforesponse.read())
            print "Response: %s" % stringinfo
            message_status = stringinfo.get('statusCode')
            message = stringinfo.get('statusMessage')
            if message_status == 'fail':
                print "Error getting location information[%s]: %s" % (ip, message)
                latitude = longitude = city = country = timezone = region = zip = ""
            else:
                latitude = float(stringinfo.get('latitude', 0))
                longitude = float(stringinfo.get('longitude', 0))
                timezone = stringinfo.get('timeZone', '')

                zip = stringinfo.get('zipCode', '')
                city = stringinfo.get('cityName', '')
                region = stringinfo.get('regionName', '')
                country = stringinfo.get('countryName', '')

            hop_response.update({
                'zip': zip,
                'city': city,
                'region': region,
                'country': country,
                'timezone': timezone,
                'latitude': latitude,
                'longitude': longitude
            })

        except URLError, e:
            print 'No kittez. Got an error code:', e

        hop_list.append(hop_response)

    hop_list = sorted(hop_list, key=itemgetter('hop'))


    hop_counter = 1
    for hop in hop_list:
        hop_difference = hop['hop'] - hop_counter
        for index_ctr in range(0, hop_difference):
            new_hop_list.append({
                'response': False,
                'hop': hop_counter,
                'ip': 'No response'
            })
            hop_counter += 1

        new_hop_list.append(hop)
        hop_counter += 1

    return trace

#change this to fetch from TraceHistory table
def trace_history(request):
    #request.post filter by a session
    history = TraceHistory.objects.filter(session__key=request.POST.get("session"))
    return render(request, 'networking/trace_history.html', context={
        'tracehistory':history
    })



def delete_devices(request):
    device_ids = request.POST.getlist('devices', [])
    connect_session_key = request.POST.get('session', None)

    if connect_session_key is not None:
        devices_to_delete = Device.objects.filter(pk__in=device_ids, session__key=connect_session_key)
    else:
        devices_to_delete = Device.objects.filter(pk__in=device_ids)

    devices_to_delete.delete()

    return HttpResponse("Success")
