from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from config.middleware import FrontendErrorMiddleware, RequestRateLimitMiddleware


class SecurityMiddlewareTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def tearDown(self):
        cache.clear()

    def test_rate_limit_allows_first_ten_requests(self):
        middleware = RequestRateLimitMiddleware(lambda request: HttpResponse("ok"))

        responses = [middleware(self.factory.get("/candidate/dashboard/", REMOTE_ADDR="10.10.10.10")) for _ in range(10)]

        self.assertTrue(all(response.status_code == 200 for response in responses))

    def test_rate_limit_blocks_eleventh_request(self):
        middleware = RequestRateLimitMiddleware(lambda request: HttpResponse("ok"))

        for _ in range(10):
            middleware(self.factory.get("/candidate/dashboard/", REMOTE_ADDR="10.10.10.11"))

        response = middleware(self.factory.get("/candidate/dashboard/", REMOTE_ADDR="10.10.10.11"))

        self.assertEqual(response.status_code, 429)
        self.assertIn(b"Too Many Requests", response.content)
        self.assertEqual(response["Retry-After"], "1")

    def test_rate_limit_returns_json_for_ajax(self):
        middleware = RequestRateLimitMiddleware(lambda request: HttpResponse("ok"))

        for _ in range(10):
            middleware(self.factory.get("/candidate/dashboard/", REMOTE_ADDR="10.10.10.12"))

        request = self.factory.get(
            "/candidate/dashboard/",
            REMOTE_ADDR="10.10.10.12",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = middleware(request)

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn(b"Too many requests", response.content)

    def test_frontend_error_middleware_returns_friendly_500(self):
        def failing_view(request):
            raise RuntimeError("internal test failure")

        middleware = FrontendErrorMiddleware(failing_view)
        response = middleware(self.factory.get("/candidate/dashboard/"))

        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Something went wrong", response.content)

    def test_frontend_error_middleware_returns_json_for_ajax(self):
        def failing_view(request):
            raise RuntimeError("internal test failure")

        middleware = FrontendErrorMiddleware(failing_view)
        request = self.factory.get(
            "/candidate/dashboard/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        response = middleware(request)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn(b"Something went wrong", response.content)
