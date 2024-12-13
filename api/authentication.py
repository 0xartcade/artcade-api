from django.conf import settings
from knox.auth import TokenAuthentication as KnoxTokenAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import PermissionDenied


class TokenAuthentication(KnoxTokenAuthentication):
    def authenticate(self, request):
        # check for cookie
        if auth_cookie := request.COOKIES.get(settings.AUTH_COOKIE_NAME):
            # cookie exists, set auth header
            request.META["HTTP_AUTHORIZATION"] = f"Token {auth_cookie}"

            # enforce csrf
            self.enforce_csrf(request)
        return super().authenticate(request)

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        """

        def dummy_get_response(request):  # pragma: no cover
            return None

        check = CSRFCheck(dummy_get_response)
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise PermissionDenied("CSRF Failed: %s" % reason)
