"""List recent eBay My Messages (Trading API GetMyMessages).

Usage:
  python ebay_messages.py            # headers from last 7 days
  python ebay_messages.py 14         # headers from last N days
  python ebay_messages.py body <MessageID> [<MessageID> ...]   # full body of message(s)
"""
import os, sys, re, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("EBAY_AUTH_TOKEN")
APP_ID = os.getenv("EBAY_APP_ID")
DEV_ID = os.getenv("EBAY_DEV_ID")
CERT_ID = os.getenv("EBAY_CERT_ID")
if not TOKEN:
    sys.exit("EBAY_AUTH_TOKEN missing from secrets env")

NS = "urn:ebay:apis:eBLBaseComponents"


def call(call_name, body_xml):
    xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<{call_name}Request xmlns="{NS}">
  <RequesterCredentials><eBayAuthToken>{TOKEN}</eBayAuthToken></RequesterCredentials>
  {body_xml}
</{call_name}Request>"""
    req = urllib.request.Request(
        "https://api.ebay.com/ws/api.dll",
        data=xml_req.encode(),
        headers={
            "X-EBAY-API-CALL-NAME": call_name,
            "X-EBAY-API-SITEID": "0",
            "X-EBAY-API-COMPATIBILITY-LEVEL": "1193",
            "X-EBAY-API-APP-NAME": APP_ID or "",
            "X-EBAY-API-DEV-NAME": DEV_ID or "",
            "X-EBAY-API-CERT-NAME": CERT_ID or "",
            "Content-Type": "text/xml",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return ET.fromstring(r.read())


def t(el, tag):
    x = el.find(f"{{{NS}}}{tag}")
    return x.text if x is not None and x.text else ""


def headers(days, folder=0):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    root = call("GetMyMessages", f"""
  <FolderID>{folder}</FolderID>
  <StartTime>{start.strftime('%Y-%m-%dT%H:%M:%S.000Z')}</StartTime>
  <EndTime>{end.strftime('%Y-%m-%dT%H:%M:%S.000Z')}</EndTime>
  <DetailLevel>ReturnHeaders</DetailLevel>""")
    ack = t(root, "Ack")
    if ack not in ("Success", "Warning"):
        print(ET.tostring(root, encoding="unicode")[:2000])
        sys.exit(f"GetMyMessages failed: {ack}")
    msgs = root.findall(f".//{{{NS}}}Message")
    if not msgs:
        print(f"No messages in the last {days} days.")
        return
    for m in msgs:
        print(f"[{t(m,'ReceiveDate')[:16]}] from={t(m,'Sender'):<25} to={t(m,'RecipientUserID'):<25} "
              f"read={t(m,'Read'):<5} id={t(m,'MessageID')}  {t(m,'Subject')}")


def bodies(ids, folder=0):
    id_xml = "".join(f"<MessageID>{i}</MessageID>" for i in ids)
    root = call("GetMyMessages", f"""
  <FolderID>{folder}</FolderID>
  <MessageIDs>{id_xml}</MessageIDs>
  <DetailLevel>ReturnMessages</DetailLevel>""")
    for m in root.findall(f".//{{{NS}}}Message"):
        print(f"=== {t(m,'MessageID')} | {t(m,'ReceiveDate')} | from {t(m,'Sender')}")
        print(f"Subject: {t(m,'Subject')}")
        text = t(m, "Text") or ""
        text = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
        text = re.sub(r"<[^>]+>", "\n", text)
        text = html.unescape(text)
        lines = [ln.strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln and not re.match(
            r"^(body\[|@media|@-moz|td\.|span\.|\.|\}|\{)", ln)]
        print("\n".join(lines)[:4000])
        print()


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "body":
        bodies(args[1:])
    elif args and args[0] == "bodysent":
        bodies(args[1:], folder=1)
    elif args and args[0] == "sent":
        headers(int(args[1]) if len(args) > 1 else 7, folder=1)
    else:
        headers(int(args[0]) if args else 7)
