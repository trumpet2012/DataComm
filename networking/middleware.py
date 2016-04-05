from ipware.ip import get_real_ip


class IpMiddleware:

    def process_request(self, request):
        request.ip = get_real_ip(request)
