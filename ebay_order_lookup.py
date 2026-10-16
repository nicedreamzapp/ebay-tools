"""Look up an eBay order by extended order ID -> buyer username + status.

Usage: python ebay_order_lookup.py <ORDER_ID>
"""
import os, sys
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("EBAY_AUTH_TOKEN")
NS = "urn:ebay:apis:eBLBaseComponents"

order_id = sys.argv[1]
xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<GetOrdersRequest xmlns="{NS}">
  <RequesterCredentials><eBayAuthToken>{TOKEN}</eBayAuthToken></RequesterCredentials>
  <OrderIDArray><OrderID>{order_id}</OrderID></OrderIDArray>
  <DetailLevel>ReturnAll</DetailLevel>
</GetOrdersRequest>"""
req = urllib.request.Request(
    "https://api.ebay.com/ws/api.dll", data=xml_req.encode(),
    headers={
        "X-EBAY-API-CALL-NAME": "GetOrders",
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

print("Ack:", t(root, "Ack"))
for o in root.findall(f".//{{{NS}}}Order"):
    print("OrderID:", t(o, "OrderID"))
    print("Buyer:", t(o, "BuyerUserID"))
    print("Status:", t(o, "OrderStatus"), "| Paid:", t(o, "PaidTime"), "| Shipped:", t(o, "ShippedTime"))
    name = o.find(f".//{{{NS}}}ShippingAddress/{{{NS}}}Name")
    print("Ship to:", name.text if name is not None else "?")
    for txn in o.findall(f".//{{{NS}}}Transaction"):
        title = t(txn, "Title")
        print("Item:", title[:80])
