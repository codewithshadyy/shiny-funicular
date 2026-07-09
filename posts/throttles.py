

from rest_framework.throttling import ScopedRateThrottle


class PostCreateRateThrottle(ScopedRateThrottle):
    scope = "post_create"