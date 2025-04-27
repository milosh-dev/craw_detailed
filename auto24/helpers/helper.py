import httpx, json, logging, os, sys, time
from auto24.settings import (
    FLARESOLVERR_URL,
    FLARESOLVERR_NR_SESSIONS,
    FLARESOLVERR_TIMEOUT,
    PATH
)
from datetime import datetime

# FLARESOLVERR_URL =  "http://localhost:8191/v1"
# FLARESOLVERR_NR_SESSIONS = 7
# FLARESOLVERR_TIMEOUT = 60000

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
        logging.info("Saatsin FLARESOLVERR_URL aadressile")
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

# Prepare email text
def prepare_message(json_str):
    #data = json.loads(json_str)

    # Defineeri kuupäevaformaat
    def format_datetime(value):
        """
        Kui 'value' on kuupäeva/kellaaeg ISO 8601 kujul, tagastab funktsioon selle vormindatuna kujule "dd.mm.yyyy hh:mm".
        Kui pole, tagastatakse väärtus muutmata.
        """
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
                return dt.strftime("%d.%m.%Y %H:%M")
            except ValueError:
                # Kui stringi ei saa kuupäevaks parsida, tagastame algse väärtuse
                return value
        return value

    # Algatame tühjad andmestruktuurid tabelite ja üldiste (slash-vabade) väljade jaoks
    tables = {}         # Näiteks: {'log_count': {'WARNING': 1, 'DEBUG': 3610, 'INFO': 71}, ...}
    general_fields = {} # Väljad, mis ei sisalda kaldkriipsu võtmes

    # Itereerime läbi kõik andmed
    for key, value in json_str.items():
        # Proovime vormindada võimalikke kuupäeva/kellaaja väärtusi
        value = format_datetime(value)
        
        if "/" in key:
            # Jagame võtme esimese kaldkriipsu juures: esimene osa on tabeli nimi, teine osa reali nimetus
            table_name, sub_key = key.split("/", 1)
            if table_name not in tables:
                tables[table_name] = {}
            tables[table_name][sub_key] = value
        else:
            general_fields[key] = value

    # Koostame e‑kirja tekstilise sisu
    email_body = ""

    # Lisame üldised väljad (ilma kaldkriipsuta võtmetena)
    if general_fields:
        email_body += "Üldinfo:\n"
        for k, v in general_fields.items():
            email_body += f"  {k}: {v}\n"
        email_body += "\n"

    # Itereerime tabelite üle ja lisame iga tabeli andmed
    for table, rows in tables.items():
        email_body += f"Tabel: {table}\n"
        for sub_key, val in rows.items():
            email_body += f"  {sub_key}: {val}\n"
        email_body += "\n"

    # Väljundiks saab välja näha midagi sellist:
    # General fields:
    #   start_time: 07.04.2025 19:47
    #   item_scraped_count: 1786
    #   elapsed_time_seconds: 3597.978227
    #   finish_time: 07.04.2025 20:47
    #   finish_reason: finished
    #   responses_per_minute: None
    #   items_per_minute: None
    #
    # Table: log_count
    #   WARNING: 1
    #   DEBUG: 3610
    #   INFO: 71
    #   ERROR: 11
    #
    # Table: memusage
    #   startup: 64778240
    #   max: 135413760
    #
    # Table: scheduler
    #   enqueued/memory: 3630
    #   enqueued: 3630
    #   dequeued/memory: 3630
    #   dequeued: 3630
    #
    # ... ja nii edasi.
    return email_body


# Send email
def send_mail(message:str, title:str, scraper:str):
    import smtplib
    from email.message import EmailMessage

    #path = "/home/raoul/scrapy/auto24/scraped_files/"
    path = PATH

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
