import hashlib

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render


class RequestRateLimitMiddleware:
    """Limit each client IP to a small burst of requests per second."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 10
        self.window = 1

    def __call__(self, request):
        if self._should_skip(request):
            return self.get_response(request)

        client_ip = self._get_client_ip(request)
        key = "campushire_rate:" + hashlib.sha256(client_ip.encode()).hexdigest()

        if not cache.add(key, 1, timeout=self.window):
            try:
                count = cache.incr(key)
            except ValueError:
                cache.set(key, 1, timeout=self.window)
                count = 1
            if count > self.limit:
                response = self._rate_limited_response(request)
                response["Retry-After"] = "1"
                response["X-RateLimit-Limit"] = str(self.limit)
                response["X-RateLimit-Remaining"] = "0"
                return response

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(self.limit)
        return response

    @staticmethod
    def _get_client_ip(request):
        # X-Forwarded-For should only be trusted when set by a trusted proxy.
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    @staticmethod
    def _should_skip(request):
        path = request.path
        return (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path == "/favicon.ico"
        )

    @staticmethod
    def _rate_limited_response(request):
        accepts_json = (
            "application/json" in request.headers.get("Accept", "")
            or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        )
        if accepts_json:
            return JsonResponse(
                {
                    "error": "Too many requests. Please wait a moment and try again."
                },
                status=429,
            )
        return render(
            request,
            "errors/rate_limited.html",
            {"retry_after": 1},
            status=429,
        )


class FrontendErrorMiddleware:
    """Convert unexpected backend exceptions into a user-friendly frontend response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            accepts_json = (
                "application/json" in request.headers.get("Accept", "")
                or request.headers.get("X-Requested-With") == "XMLHttpRequest"
            )
            if accepts_json:
                return JsonResponse(
                    {"error": "Something went wrong. Please try again."},
                    status=500,
                )
            return render(
                request,
                "errors/500.html",
                status=500,
            )
