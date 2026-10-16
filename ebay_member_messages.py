"""GetMemberMessages — member-to-member conversations (includes API-sent messages).

Usage:
  python ebay_member_messages.py <ItemID> [days]
"""
import os, sys, re, html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("EBAY_AUTH_TOKEN")
NS = "urn:ebay:apis:eBLBaseComponents"

item_id = sys.argv[1]
days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
end = datetime.now(timezone.utc)
start = end - timedelta(days=days)

xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<GetMemberMessagesRequest xmlns="{NS}">
  <RequesterCredentials><eBayAuthToken>{TOKEN}</eBayAuthToken></RequesterCredentials>
  <ItemID>{item_id}</ItemID>
  <MailMessageType>All</MailMessageType>
  <StartCreationTime>{start.strftime('%Y-%m-%dT%H:%M:%S.000Z')}</StartCreationTime>
  <EndCreationTime>{end.strftime('%Y-%m-%dT%H:%M:%S.000Z')}</EndCreationTime>
  <Pagination><EntriesPerPage>50</EntriesPerPage><PageNumber>1</PageNumber></Pagination>
</GetMemberMessagesRequest>"""
req = urllib.request.Request(
    "https://api.ebay.com/ws/api.dll", data=xml_req.encode(),
    headers={
        "X-EBAY-API-CALL-NAME": "GetMemberMessages",
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "1193",
        "X-EBAY-API-APP-NAME": os.getenv("EBAY_APP_ID") or "",
        "X-EBAY-API-DEV-NAME": os.getenv("EBAY_DEV_ID") or "",
        "X-EBAY-API-CERT-NAME": os.getenv("EBAY_CERT_ID") or "",
        "Content-Type": "text/xml",
    })
with urllib.request.urlopen(req, timeout=30) as r:
    root = ET.fromstring(r.read())

def t(el, tag):
    x = el.find(f".//{{{NS}}}{tag}")
    return x.text if x is not None and x.text else ""

ack = t(root, "Ack")
print("Ack:", ack)
if ack not in ("Success", "Warning"):
    print(ET.tostring(root, encoding="unicode")[:3000])
    sys.exit(1)

msgs = root.findall(f".//{{{NS}}}MemberMessageExchange")
if not msgs:
    print(f"No member messages on item {item_id} in last {days} days.")
for ex in msgs:
    mm = ex.find(f".//{{{NS}}}Question")
    created = t(ex, "CreationDate")
    sender = t(mm, "SenderID") if mm is not None else "?"
    recip = t(mm, "RecipientID") if mm is not None else "?"
    subj = t(mm, "Subject") if mm is not None else ""
    body = t(mm, "Body") if mm is not None else ""
    body = html.unescape(re.sub(r"<[^>]+>", " ", body))
    body = re.sub(r"\s+", " ", body).strip()
    mid = t(mm, "MessageID") if mm is not None else ""
    print(f"\n[{created[:16]}] {sender} -> {recip} (MessageID: {mid})")
    print(f"  Subject: {subj}")
    print(f"  Body: {body[:500]}")
    resp = t(ex, "MessageStatus")
    print(f"  Status: {resp}")
    for rsp in ex.findall(f".//{{{NS}}}Response"):
        rtext = html.unescape(re.sub(r"<[^>]+>", " ", rsp.text or ""))
        print(f"  Response: {re.sub(r'%s+', ' ', rtext).strip()[:500]}" % r"\s")
