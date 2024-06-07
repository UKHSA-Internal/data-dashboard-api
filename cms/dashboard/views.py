from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from wagtail.admin.views.chooser import BrowseView


class LinkBrowseView(BrowseView):
    def get(
        self, request: WSGIRequest, parent_page_id: int | None = None
    ) -> JsonResponse:
        request: WSGIRequest = self._intercept_request_and_switch_off_extra_links(
            request=request
        )
        return super().get(request=request, parent_page_id=parent_page_id)

    @classmethod
    def _intercept_request_and_switch_off_extra_links(
        cls, request: WSGIRequest
    ) -> WSGIRequest:
        intercepted_query_params = request.GET.copy()
        intercepted_query_params["allow_email_link"] = False
        intercepted_query_params["allow_phone_link"] = False
        request.GET = intercepted_query_params
        return request
