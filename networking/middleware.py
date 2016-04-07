from ipware.ip import get_real_ip, get_ip


class IpMiddleware:

    def process_request(self, request):
        ip = get_real_ip(request)
        if ip is None:
            ip = get_ip(request=request)
            print "Non real IP: %s" % ip
        else:
            print "Real IP: %s" % ip

        request.ip = ip
