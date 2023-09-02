# -*- coding: utf-8 -*-
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

# Documentation at https://www.notion.so/abhishm20/Throttling-8ffe64fb352b4833b01fef971fce1c1f


class UserWiseRateThrottle(UserRateThrottle):
    def __init__(self):
        super().__init__()
        self.now = None
        self.history = None
        self.key = None

    def allow_request(self, request, view):
        """
        Give special access to a few special accounts.

        Mirrors code in super class with minor tweaks.
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Adjust if user has special privileges.
        if request.user.throttling_rate:
            self.num_requests, self.duration = self.parse_rate(request.user.throttling_rate)

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()


class StaticAnonThrottle(AnonRateThrottle):
    scope = "static-anon"


class DL1AnonThrottle(AnonRateThrottle):
    scope = "dl-1-anon"


class StaticUserThrottle(UserRateThrottle):
    scope = "static-user"


class DL1UserThrottle(UserRateThrottle):
    scope = "dl-1-user"


class DL2UserThrottle(UserRateThrottle):
    scope = "dl-2-user"


class DL3UserThrottle(UserRateThrottle):
    scope = "dl-3-user"


class DL4UserThrottle(UserRateThrottle):
    scope = "dl-4-user"


class DL5UserThrottle(UserRateThrottle):
    scope = "dl-5-user"


class DL6UserThrottle(UserRateThrottle):
    scope = "dl-6-user"
