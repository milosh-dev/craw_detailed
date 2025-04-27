# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import json, httpx, time
# from scrapy import signals
import pprint

# ChatGPT
# from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.retry import get_retry_request
# ChatGPT

from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse, Request
from logging import getLogger
from auto24.helpers.helper import (
    create_session,
    delete_session,
    retrieve_sessions
)
# from scrapy.utils.project import get_project_settings

# See peaks olema järjekorras esimene, nt 541
class FlareSolverrGetSolutionStatusMiddleware:
    """
    This middleware extracts the proper solution status from the "solution"
    given by the FlareSolverr proxy server.

    We are doing this because as for today (2023-07-24), FlareSolverr
    always returns a 200 status code and empty headers.
    """

    logger = getLogger(__name__)

    def __init__(self, settings):
        self.retry_http_codes = set(
            int(x) for x in settings.getlist("RETRY_HTTP_CODES")
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        # Disabled logic below by early return
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
        self.retry_http_codes = set(int(x) for x in settings.getlist("RETRY_HTTP_CODES"))
        self.session_id = settings.get('MY_SESSION_ID')
        self.timeout = settings.get('FLARESOLVERR_TIMEOUT')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if request.meta.get("redirected_to_flare_solverr"):
            return None

        if request.meta.get("use_session"):
            body = json.dumps({
                "url": request.url,
                "cmd": "request.get",
                "session": self.session_id,
                "maxTimeout": self.timeout
            }).encode("utf-8")
        else:
            body = json.dumps({
                "url": request.url,
                "cmd": "request.get",
                "maxTimeout": self.timeout
            }).encode("utf-8")

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

    def process_response_old(self, request, response, spider):
        if not request.meta.get("redirected_to_flare_solverr"):
            return response

        try:
            solution_response = json.loads(response.body).get("solution")
            original_request = request.meta["original_request"]
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

        except:
            #self.logger.error(f"Failed to parse JSON response: <{response.status} {response.url}>")
            #self.logger.debug(f"Response body: {response.body}")
            raise IgnoreRequest(f"Failed to parse JSON response: <{response.status} {response.url}>")

    def process_response(self, request, response, spider):
        if not request.meta.get("redirected_to_flare_solverr"):
            return response

        # Kui sa saad HTTP 422 Unprocessable Entity vastuse, logi vastuse keha
        if response.status == 422:
            # Võid logida kogu vastuse sisu või osa sellest, nt esimese 500 märgi
            self.logger.error("Received 422 response from FlareBypasser: %s", response.text[:500])
            self.logger.debug("Response dump: %s", pprint.pformat(response.__dict__))
            # self.logger.debug(f"Response body: {response.body}")
            # Kui soovid, võid siin ka lisaks retry loogikat rakendada või mingit fallback-mehhanismi lisada

        try:
            # Parseeri JSON vastus
            json_response = json.loads(response.body)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON response: <{response.status} {response.url}>")
            self.logger.debug(f"Response body: {response.body}")
            raise IgnoreRequest(f"Failed to parse JSON response: <{response.status} {response.url}>")

        # Kontrolli, kas 'solution' väärtus on olemas
        solution_response = json_response.get("solution")
        if solution_response is None:
            self.logger.error(
                f"Missing 'solution' key in FlareSolverr response: <{response.status} {response.url}>. "
                f"Full request: {request.meta['original_request']}" 
                f"Full response: {json_response}"
            )
            raise IgnoreRequest(
                f"Missing 'solution' key in response: <{response.status} {response.url}>"
            )

        # Jätka HTML vastuse loomist, kui 'solution' oli olemas
        original_request = request.meta["original_request"]
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
        self.retry_http_codes = set(int(x) for x in settings.getlist("RETRY_HTTP_CODES"))
        self.session_id = settings.get('MY_SESSION_ID')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        if not request.meta.get("redirected_to_flare_solverr"):
            return response

        if response.status == 200:
            return response

        self.logger.warning(f"Non 200 response: <{response.status} {response.url}>")

        self.logger.debug(f"""
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

        if int(response.status) in self.retry_http_codes:
            retry_count = request.meta.get("flaresolverr_retry_count", 0) + 1
            self.logger.info("-----------")
            self.logger.debug(f"Proovin uuesti: {retry_count}")

            try:
                if request.meta.get("use_session"):
                    self.logger.info("KUSTUTASIN SESSIOONI")
                    delete_session(self.session_id)
                else:
                    self.logger.info("OTSISIN SESSIOONID ÜLES")
                    sessions = retrieve_sessions()
                    self.logger.debug(f"Sessions response: {sessions}")
                    for session in sessions:
                        delete_session(session)
            except Exception as e:
                self.logger.warning(f"Session cleanup failed: {e}")
                raise IgnoreRequest("Session cleanup failed")

                
            self.logger.info("FlareSolverrRetryMiddleware: Pausing scrape job for 45 seconds...")
            spider.crawler.engine.pause()
            time.sleep(45)
            spider.crawler.engine.unpause()
            self.logger.info("Resuming crawl...")

            try:
                if request.meta.get("use_session"):
                    create_session(url=request.url, session_id=self.session_id)
            except Exception as e:
                self.logger.warning(f"Session creation failed: {e}")
                raise IgnoreRequest("Session creation failed")

            if retry_count < self.retry_times:
                updated_meta = request.meta.copy()
                updated_meta.pop("local_address", None)
                updated_meta.update({
                    "dont_filter": True,
                    "redirected_to_flare_solverr": True,
                    "flaresolverr_retry_count": retry_count,
                })

                retry_request = get_retry_request(
                    request,
                    reason=f"FlareSolverr returned {response.status}",
                    spider=spider
                )

                if retry_request:
                    retry_request.meta.update(updated_meta)
                    retry_request.priority = request.priority - 10
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
