"""GetItem via Trading API -> title, price, qty, full description text.

Usage: python ebay_item_api.py <ItemID>
"""
import os, sys, re, html
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("EBAY_AUTH_TOKEN")
NS = "urn:ebay:apis:eBLBaseComponents"
item_id = sys.argv[1]

xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<GetItemRequest xmlns="{NS}">
  <RequesterCredentials><eBayAuthToken>{TOKEN}</eBayAuthToken></RequesterCredentials>
  <ItemID>{item_id}</ItemID>
  <DetailLevel>ReturnAll</DetailLevel>
  <IncludeItemSpecifics>true</IncludeItemSpecifics>
</GetItemRequest>"""

req = urllib.request.Request(
    "https://api.ebay.com/ws/api.dll", data=xml_req.encode(),
    headers={
        "X-EBAY-API-CALL-NAME": "GetItem",
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "1193",
        "X-EBAY-API-APP-NAME": os.getenv("EBAY_APP_ID") or "",
        "X-EBAY-API-DEV-NAME": os.getenv("EBAY_DEV_ID") or "",
        "X-EBAY-API-CERT-NAME": os.getenv("EBAY_CERT_ID") or "",
        "Content-Type": "text/xml",
    })
with urllib.request.urlopen(req, timeout=60) as r:
    root = ET.fromstring(r.read())


def q(el, tag):
    x = el.find(f".//{{{NS}}}{tag}")
    return x.text if x is not None and x.text else ""


print("Ack:", q(root, "Ack"))
for e in root.iter(f"{{{NS}}}LongMessage"):
    print("MSG:", e.text)
print("Title:", q(root, "Title"))
print("Price:", q(root, "StartPrice"), "| Qty:", q(root, "Quantity"), "| Sold:", q(root, "QuantitySold"))
print("Listed:", q(root, "StartTime")[:16])
print("\n-- Item specifics --")
for nv in root.findall(f".//{{{NS}}}ItemSpecifics/{{{NS}}}NameValueList"):
    n = q(nv, "Name")
    vals = [v.text for v in nv.findall(f"{{{NS}}}Value") if v.text]
    print(f"  {n}: {', '.join(vals)}")
desc = q(root, "Description")
txt = re.sub(r"<[^>]+>", "\n", desc)
txt = html.unescape(txt)
txt = re.sub(r"\n{2,}", "\n", txt).strip()
print("\n-- Description --")
print(txt)
