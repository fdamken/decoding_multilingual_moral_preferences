import time
from datetime import datetime, timedelta


class RateLimit:
    _calls = []

    @staticmethod
    def wait(max_calls: int, period: int) -> None:
        """Rate limit API requests. At most :param:`max_calls` are allowed in
        :param:`period` seconds."""

        # use 10% margin to be sure we do not exceed the rate limit
        delta = timedelta(seconds=1.1 * period)

        rate_limit_exceeded = True
        while rate_limit_exceeded:
            expired_calls = datetime.now() - delta
            RateLimit._calls = [call for call in RateLimit._calls if call >= expired_calls]
            rate_limit_exceeded = len(RateLimit._calls) >= max_calls
            if rate_limit_exceeded:
                # on average, we need to wait period/max_calls seconds per call
                time.sleep(period / max_calls)
        RateLimit._calls.append(datetime.now())
