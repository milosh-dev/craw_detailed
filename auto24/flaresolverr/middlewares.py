    # Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import json, httpx, time
#from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse, Request
from logging import getLogger
from auto24.helpers.helper import (
    create_session,
    delete_session,
    retrieve_sessions
)
#from scrapy.utils.project import get_project_settings

# See peaks olema järjekrorras esimene, nt 541
class FlareSolverrGetSolutionStatusMiddleware:
    """
    This middleware extracts the proper solution status from the "solution"
    given by the FlareSolverr proxy server.

    We are doing this because as for today (2023-07-24), FlareSolverr
    always returns a 200 status code and empty headers.
    See https://github.com/FlareSolverr/FlareSolverr/blob/7728f2ab317ea4b1a9a417b65465e130eb3f337f/src/flaresolverr_service.py#L392
    """

    logger = getLogger(__name__)

    def __init__(self, settings):
        self.retry_http_codes = set(
            int(x) for x in settings.getlist("RETRY_HTTP_CODES")
        )

    @classmethod
    # The main entry point is the from_crawler class method, which receives a Crawler instance. 
    # The Crawler object gives you access, for example, to the settings.
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        """
        This method processes the response object and returns a new response
        object with a status code that we can retry, as defined in
        the RETRY_HTTP_CODES setting.

        This allows the retry middleware to retry the request if the response
        from our URL is not 200.
        """
        # print(response.text)
        return response

        for status_code in self.retry_http_codes:
            if str(status_code) in response.css("title::text").get():
                self.logger.warning(f"Non 200 response: <{status_code} {response.url}>")
                return response.replace(status=status_code)

        return response

# See peaks olema järjekorras teine, nt 542
class FlareSolverrRedirectMiddleware:
    """
    This middleware redirects to and handles responses from a FlareSolverr
    proxy server to bypass Cloudflare's anti-bot protection.
    """

    logger = getLogger(__name__)
    session = ""

    def __init__(self, settings):
        self.proxy_url = settings.get("FLARESOLVERR_URL")
        self.retry_times = settings.getint("RETRY_TIMES")
        self.retry_http_codes = set(
            int(x) for x in settings.getlist("RETRY_HTTP_CODES")
        )
        self.session_id = settings.get('MY_SESSION_ID')
        self.timeout = settings.get('FLARESOLVERR_TIMEOUT')

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create spiders.
        return cls(crawler.settings)

    def process_request(self, request, spider):
        """
        This method modifies the request object to use the FlareSolverr
        proxy server.
        """

        # If the request was redirected to FlareSolverr, don't process it again
        if request.meta.get("redirected_to_flare_solverr"):
            return None

        if request.meta.get("use_session"):
            body = json.dumps(
                {
                    "url": request.url,
                    "cmd": "request.get",
                    "session": self.session_id,
                    "maxTimeout": self.timeout
                }
            ).encode("utf-8")
        else:
            body = json.dumps(
                {
                    "url": request.url,
                    "cmd": "request.get",
                    "maxTimeout": self.timeout
                }
            ).encode("utf-8")

        new_request = request.replace(
            url=self.proxy_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=body,
            meta={
                "original_request": request,
                "dont_filter": True,
                "handle_httpstatus_all": True,
                "redirected_to_flare_solverr": True,
                "download_slot": self.proxy_url,
            },
        )
        return new_request

    def process_response(self, request, response, spider):
        """
        This method processes the response from the FlareSolverr proxy server.
        If the response is from the proxy server, it will be used to create a
        new HtmlResponse object. Otherwise, the original response will be
        returned.
        """
        # If the request was not redirected to FlareSolverr, return the original response
        if not request.meta.get("redirected_to_flare_solverr"):
            return response

        try:
            solution_response = json.loads(response.body).get("solution")
            original_request = request.meta["original_request"]

        except json.JSONDecodeError:
            self.logger.error(
                f"Failed to parse JSON response: <{response.status} {response.url}>"
            )
            self.logger.debug(f"Response body: {response.body}")
            raise IgnoreRequest(
                f"Failed to parse JSON response: <{response.status} {response.url}>"
            )

        # NOTE: we are using the headers from the FlareSolverr response
        # instead of the headers from FlareSolverr's solution response.
        # We are doing this because as for today (2023-07-24), FlareSolverr
        # always returns a 200 status code and empty headers.
        # In the future, we should use the headers from the solution response
        # like this: headers=solution_response.get("headers")
        html_response = HtmlResponse(
            url=solution_response.get("url"),
            status=solution_response.get("status"),
            body=solution_response.get("response"),
            headers=response.headers,
            request=original_request,
            protocol=response.protocol,
            encoding="utf-8",
        )
        return html_response


class FlareSolverrRetryMiddleware:
    """
    This middleware retries requests that failed due to a FlareSolverr error.
    """

    logger = getLogger(__name__)

    def __init__(self, settings):
        self.retry_times = settings.getint("RETRY_TIMES")
        self.retry_http_codes = set(
            int(x) for x in settings.getlist("RETRY_HTTP_CODES")
        )
        self.session_id = settings.get('MY_SESSION_ID')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        """
        This method processes responses from the FlareSolverr proxy server.

        If the response from FlareSolverr is not 200, the request will be
        retried up to retry_times times if the HTTP status code is in the
        retry_http_codes list in the settings.py file.
        """

        if not request.meta.get("redirected_to_flare_solverr"):
            return response

        if response.status == 200:
            return response

        self.logger.warning(f"Non 200 response: <{response.status} {response.url}>")

        print(f"""
            ----------------
            REQUEST HEADERS:
            {request.headers}
            ----------------
            REQUEST META:
            {request.meta}
            ----------------
            RESPONSE HEADERS:
            {response.headers}
            ----------------
            RESPONSE BODY:
            {response.text}
            ----------------
        """)

        # If the HTTP status code is in the retry_http_codes list, retry the request
        if response.status in self.retry_http_codes:
            original_request = request.meta["original_request"]
            retry_count = request.meta.get("flaresolverr_retry_count", 0) + 1

            # Delete current session
            if request_meta.get("use_session"):
                delete_session(self.session_id)
            else:
                sessions = retrieve_sessions()
                for session in sessions:
                    delete_session(session)

            # Pause for a while
            self.logger.info(f"FlareSolverrRetryMiddleware: Pausing scrape job for 45 seconds...")
            spider.crawler.engine.pause()
            time.sleep(45)
            spider.crawler.engine.unpause()
            self.logger.info(f"Resuming crawl...")

            # Recreate session
            if request_meta.get("use_session"):
                create_session(url=request.url, session_id = self.session_id)

            if retry_count < self.retry_times:
                updated_meta = request.meta.copy()
                updated_meta.update(
                    {
                        "dont_filter": True,
                        "redirected_to_flare_solverr": False,
                        "flaresolverr_retry_count": retry_count,
                    }
                )
                retry_request = original_request.replace(
                    meta=updated_meta, priority=original_request.priority - 10
                )

                self.logger.debug(
                    f"Retrying request. Retry count: {retry_count}: <{response.status} {request.url}>"
                )
                return retry_request

            self.logger.error(
                f"Request failed after {retry_count} retries: <{response.status} {request.url}>"
            )
            self.logger.debug(f"Response body: {response.status} {response.body}")
            raise IgnoreRequest(
                f"Request failed after {retry_count} retries: <{response.status} {request.url}>"
            )

        return response
