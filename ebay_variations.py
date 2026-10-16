"""View or zero eBay variation stock on a listing.

Usage:
  python ebay_variations.py <ITEM_ID>                      # list variations + qty
  python ebay_variations.py <ITEM_ID> zero "<Color>" <size>  # set Color/Size variation qty to 0
"""
import os, sys
import urllib.request
import xml.etree.ElementTree as ET

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


def show(item_id):
    root = call("GetItem", f"<ItemID>{item_id}</ItemID><DetailLevel>ReturnAll</DetailLevel>")
    print("Ack:", root.findtext(f"{{{NS}}}Ack"))
    for v in root.findall(f".//{{{NS}}}Variation"):
        qty = v.findtext(f"{{{NS}}}Quantity", "0")
        sold = v.findtext(f".//{{{NS}}}QuantitySold", "0")
        specs = {nv.findtext(f"{{{NS}}}Name"): nv.findtext(f"{{{NS}}}Value")
                 for nv in v.findall(f".//{{{NS}}}VariationSpecifics/{{{NS}}}NameValueList")}
        avail = int(qty) - int(sold)
        print(f"  {specs}  listed_qty={qty} sold={sold} available={avail}")


def zero(item_id, color, size):
    body = f"""<Item><ItemID>{item_id}</ItemID>
  <Variations><Variation>
    <VariationSpecifics>
      <NameValueList><Name>Color</Name><Value>{color}</Value></NameValueList>
      <NameValueList><Name>sizes</Name><Value>{size}</Value></NameValueList>
    </VariationSpecifics>
    <Quantity>0</Quantity>
  </Variation></Variations></Item>"""
    root = call("ReviseFixedPriceItem", body)
    ack = root.findtext(f"{{{NS}}}Ack")
    print("Revise Ack:", ack)
    for err in root.findall(f".//{{{NS}}}Errors"):
        print(" ", err.findtext(f"{{{NS}}}SeverityCode"), "-",
              err.findtext(f"{{{NS}}}LongMessage"))


if __name__ == "__main__":
    item = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "zero":
        zero(item, sys.argv[3], sys.argv[4])
        show(item)
    else:
        show(item)
