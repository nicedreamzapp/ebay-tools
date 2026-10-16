"""Dump ship-to address + tracking for eBay orders. Usage: python ebay_order_full.py ID [ID...]"""
import os, sys, urllib.request, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
NS = "urn:ebay:apis:eBLBaseComponents"
ids = "".join(f"<OrderID>{i}</OrderID>" for i in sys.argv[1:])
xml_req = f"""<?xml version="1.0" encoding="utf-8"?><GetOrdersRequest xmlns="{NS}"><RequesterCredentials><eBayAuthToken>{os.getenv("EBAY_AUTH_TOKEN")}</eBayAuthToken></RequesterCredentials><OrderIDArray>{ids}</OrderIDArray><DetailLevel>ReturnAll</DetailLevel></GetOrdersRequest>"""
req = urllib.request.Request("https://api.ebay.com/ws/api.dll", data=xml_req.encode(), headers={"X-EBAY-API-CALL-NAME": "GetOrders","X-EBAY-API-SITEID": "0","X-EBAY-API-COMPATIBILITY-LEVEL": "1193","Content-Type": "text/xml"})
root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
def t(el, tag):
    x = el.find(f".//{{{NS}}}{tag}"); return x.text if x is not None and x.text else ""
for o in root.findall(f".//{{{NS}}}Order"):
    a = o.find(f".//{{{NS}}}ShippingAddress")
    print("==", t(o,"OrderID"), t(o,"OrderStatus"), "paid", t(o,"PaidTime"), "shipped", t(o,"ShippedTime"))
    print("  to:", " | ".join(t(a,k) for k in ["Name","Street1","Street2","CityName","StateOrProvince","PostalCode"]))
    for st in o.findall(f".//{{{NS}}}ShipmentTrackingDetails"):
        print("  tracking:", t(st,"ShippingCarrierUsed"), t(st,"ShipmentTrackingNumber"))
