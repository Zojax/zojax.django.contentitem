from django.contrib.sites.models import RequestSite, Site


class SiteMiddleware(object):

    def process_request(self, request):
        requestsite = RequestSite(request)
        try:
            request.site = Site.objects.get_current()
        except Site.DoesNotExist:
            request.site = requestsite

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        return response