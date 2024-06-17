import httpx, json, logging, os, sys, time

FLARESOLVERR_URL =  "http://localhost:8191/v1"
FLARESOLVERR_NR_SESSIONS = 7
FLARESOLVERR_TIMEOUT = 60000

# send a GET request with FlareSolverr
# Author: https://scrapfly.io/blog/how-to-bypass-cloudflare-with-flaresolverr/
# If you need post_request see self.post_request_with_session below
def create_session(url: str, session_id:str = ""):
    try:
        # basic header content type header
        r_headers = {"Content-Type": "application/json"}

        if session_id == "":
            # request payload
            payload = {
                "cmd": "sessions.create",
                "url": url,
                # Proxies in FlareSolverr can be added for all commands through the proxy parameter:
                # "proxy": {"url": "proxy_url", "username": "proxy_username", "password": "proxy_password"},
                "maxTimeout": FLARESOLVERR_TIMEOUT
            }
        else:            
            # request payload
            payload = {
                "cmd": "sessions.create",
                "url": url,
                "session": session_id,
                # Proxies in FlareSolverr can be added for all commands through the proxy parameter:
                # "proxy": {"url": "proxy_url", "username": "proxy_username", "password": "proxy_password"},
                "maxTimeout": FLARESOLVERR_TIMEOUT
            }
        # send the POST request using httpx
        response = httpx.post(url=FLARESOLVERR_URL, headers=r_headers, json=payload, timeout=FLARESOLVERR_TIMEOUT)
        # Save response
        # self.response = response
        # Save session data for url
        return response
        #async with httpx.AsyncClient() as client:
        #    response = await client.post(url=self.flaresolverr_url, headers=r_headers, json=payload, timeout=self.timeout)
        #    return response
    except Exception as e:
        logging.error(f"Error in send_get_request: {e}")
        return None

# retrieve FlareSolverr sessions
# Author: https://scrapfly.io/blog/how-to-bypass-cloudflare-with-flaresolverr/
def retrieve_sessions() -> list:
    try:
        # basic header content type header
        r_headers = {"Content-Type": "application/json"}
        # request payload
        payload = {
            # Proxies in FlareSolverr can be added for all commands through the proxy parameter:
            # "proxy": {"url": "proxy_url", "username": "proxy_username", "password": "proxy_password"},
            "cmd": "sessions.list"
        }
        # send the POST request using httpx
        response = httpx.post(url=FLARESOLVERR_URL, headers=r_headers, json=payload, timeout=FLARESOLVERR_TIMEOUT)
        return response
        # #return response
        # self.sessions = json.loads(response.text)["sessions"]
    except Exception as e:
        logging.error(f"Error in retrieve_sessions: {e}")
        return []

# send a GET request with a FlareSolverr session
# Author: https://scrapfly.io/blog/how-to-bypass-cloudflare-with-flaresolverr/    
def get_request_with_session(url: str, session_id: str = ""):
    try:
        # basic header content type header
        r_headers = {"Content-Type": "application/json"}
        # request payload
        payload = {
            "cmd": "request.get",
            "session": session_id,
            "url": url,
            # Proxies in FlareSolverr can be added for all commands through the proxy parameter:
            # "proxy": {"url": "proxy_url", "username": "proxy_username", "password": "proxy_password"},
            "maxTimeout": FLARESOLVERR_TIMEOUT
        }   
        # send the POST request using httpx
        response = httpx.post(url=FLARESOLVERR_URL, headers=r_headers, json=payload, timeout=FLARESOLVERR_TIMEOUT)
        return response
        #async with httpx.AsyncClient() as client:
        #    response = await client.post(url=FLARESOLVERR_URL, headers=r_headers, json=payload, timeout=FLARESOLVERR_TIMEOUT)
        #    return response            
    except Exception as e:
        logging.error(f"Error in get_request_with_session: {e}")
        return None

# send a GET request with a FlareSolverr session
# Author: https://scrapfly.io/blog/how-to-bypass-cloudflare-with-flaresolverr/    
def post_request_with_session(url: str, request_payload: str, session_id: str = ""):
    try:
        # basic header content type header
        r_headers = {"Content-Type": "application/json"}
        # request payload
        payload = {
            "cmd": "request.post",
            "session": session_id,
            "url": url,
            "maxTimeout": FLARESOLVERR_TIMEOUT,
            # Proxies in FlareSolverr can be added for all commands through the proxy parameter:
            # "proxy": {"url": "proxy_url", "username": "proxy_username", "password": "proxy_password"},
            "postData": request_payload
        }
        # send the POST request using httpx
        response = httpx.post(url=FLARESOLVERR_URL, headers=r_headers, json=payload, timeout=FLARESOLVERR_TIMEOUT)
        return response
    except Exception as e:
        logging.error(f"Error in post_request_with_session: {e}")
        return None

# destroy FlareSolverr session
# Author: https://scrapfly.io/blog/how-to-bypass-cloudflare-with-flaresolverr/
def delete_session(session_id: str):
    try:
        # basic header content type header
        r_headers = {"Content-Type": "application/json"}
        # request payload
        payload = {
            "cmd": "sessions.destroy",
            "session": session_id
        }
        # send the POST request using httpx
        response = httpx.post(url=FLARESOLVERR_URL, headers=r_headers, json=payload)
        # recreate sessions
        return response
    except Exception as e:
        logging.error(f"Error in delete_session: {e}")
        return None

# Find the newest path in folder
def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)

# Send email
def send_mail(message:str, title:str, scraper:str):
    import smtplib
    from email.message import EmailMessage

    path = "/home/raoul/scrapy/auto24/scraped_files/"

    msg = EmailMessage()
    msg['From'] = "raoul.lattemae@gmail.com"
    msg['To'] = "raoul.lattemae@gmail.com"
    msg["Subject"] = title
    msg.set_content(message)

    file = newest(path + scraper)

    with open(file, 'r') as f:
        data = f.read()
    filename = file.replace(path + scraper + "/", "")
    msg.add_attachment(data, filename = filename)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.ehlo()
    server.login("raoul.lattemae@gmail.com", "jawf fnnw dzml zrcn")
    server.send_message(msg)
    server.quit()