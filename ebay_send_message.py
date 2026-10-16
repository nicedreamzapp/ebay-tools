"""Send an eBay buyer message via AddMemberMessageAAQToPartner — WITH ItemID, then VERIFY.

Usage: python ebay_send_message.py <recipient> <item_id> <subject> <body>

RULE (June 9, 2026): ItemID is REQUIRED — without it eBay returns Success but the
message silently vanishes. After sending, this script verifies the message appears
in the member-message exchange log before declaring success.
"""
import os, sys, time, html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("EBAY_AUTH_TOKEN")
NS = "urn:ebay:apis:eBLBaseComponents"


def call(name, body):
    xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<{name}Request xmlns="{NS}">
  <RequesterCredentials><eBayAuthToken>{TOKEN}</eBayAuthToken></RequesterCredentials>
  {body}
</{name}Request>"""
    req = urllib.request.Request(
        "https://api.ebay.com/ws/api.dll", data=xml_req.encode(),
        headers={
            "X-EBAY-API-CALL-NAME": name,
            "X-EBAY-API-SITEID": "0",
            "X-EBAY-API-COMPATIBILITY-LEVEL": "1193",
            "X-EBAY-API-APP-NAME": os.getenv("EBAY_APP_ID") or "",
            "X-EBAY-API-DEV-NAME": os.getenv("EBAY_DEV_ID") or "",
            "X-EBAY-API-CERT-NAME": os.getenv("EBAY_CERT_ID") or "",
            "Content-Type": "text/xml",
        })
    with urllib.request.urlopen(req, timeout=60) as r:
        return ET.fromstring(r.read())


recipient, item_id, subject, body_text = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

root = call("AddMemberMessageAAQToPartner", f"""
  <ItemID>{item_id}</ItemID>
  <MemberMessage>
    <Subject>{html.escape(subject)}</Subject>
    <Body>{html.escape(body_text)}</Body>
    <QuestionType>General</QuestionType>
    <RecipientID>{recipient}</RecipientID>
  </MemberMessage>""")
ack = root.findtext(f"{{{NS}}}Ack")
print("Send Ack:", ack)
for err in root.findall(f".//{{{NS}}}Errors"):
    print(" ", err.findtext(f"{{{NS}}}SeverityCode"), "-", err.findtext(f"{{{NS}}}LongMessage"))
if ack not in ("Success", "Warning"):
    sys.exit("SEND FAILED")

# Verify: a copy addressed to the recipient must appear in the My Messages Sent
# folder (FolderID 1). This copy only exists when eBay actually threaded and
# delivered the message — a malformed send (e.g. missing ItemID) leaves no copy.
print("Verifying delivery via Sent folder...")
end = datetime.now(timezone.utc)
start = end - timedelta(hours=2)
for attempt in range(6):
    time.sleep(10)
    vroot = call("GetMyMessages", f"""
  <FolderID>1</FolderID>
  <StartTime>{start.strftime('%Y-%m-%dT%H:%M:%S.000Z')}</StartTime>
  <EndTime>{(end + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S.000Z')}</EndTime>
  <DetailLevel>ReturnHeaders</DetailLevel>""")
    ids = [m.findtext(f"{{{NS}}}MessageID", "") for m in vroot.findall(f".//{{{NS}}}Message")
           if item_id in (m.findtext(f"{{{NS}}}Subject", "") or "")]
    if ids:
        id_xml = "".join(f"<MessageID>{i}</MessageID>" for i in ids)
        broot = call("GetMyMessages", f"""
  <FolderID>1</FolderID>
  <MessageIDs>{id_xml}</MessageIDs>
  <DetailLevel>ReturnMessages</DetailLevel>""")
        for m in broot.findall(f".//{{{NS}}}Message"):
            text = m.findtext(f"{{{NS}}}Text", "") or ""
            if recipient in text and body_text[:60] in text:
                print(f"VERIFIED DELIVERED: Sent-folder copy {m.findtext(f'{{{NS}}}MessageID')} "
                      f"addressed to {recipient} contains the message text.")
                sys.exit(0)
    print(f"  not visible yet (attempt {attempt + 1}/6)...")

sys.exit("NOT VERIFIED — no Sent-folder copy found. DO NOT report as sent.")
