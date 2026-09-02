from silk.profiling.profiler import silk_profile


class SilkProfileAllViewsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        return silk_profile()(view_func)(request, *view_args, **view_kwargs)
