from ipware.ip import get_ip


class IpMiddleware:

    def process_request(self, request):
        request.ip = get_ip(request)
