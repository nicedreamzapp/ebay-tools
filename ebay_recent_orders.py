"""List recent eBay orders with buyer, items and variation specifics (color/size).

Usage: python ebay_recent_orders.py [days]
"""
import os, sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("EBAY_AUTH_TOKEN")
NS = "urn:ebay:apis:eBLBaseComponents"
days = int(sys.argv[1]) if len(sys.argv) > 1 else 14
end = datetime.now(timezone.utc)
start = end - timedelta(days=days)

xml_req = f"""<?xml version="1.0" encoding="utf-8"?>
<GetOrdersRequest xmlns="{NS}">
  <RequesterCredentials><eBayAuthToken>{TOKEN}</eBayAuthToken></RequesterCredentials>
  <CreateTimeFrom>{start.strftime('%Y-%m-%dT%H:%M:%S.000Z')}</CreateTimeFrom>
  <CreateTimeTo>{end.strftime('%Y-%m-%dT%H:%M:%S.000Z')}</CreateTimeTo>
  <OrderRole>Seller</OrderRole>
  <OrderStatus>All</OrderStatus>
  <DetailLevel>ReturnAll</DetailLevel>
  <Pagination><EntriesPerPage>100</EntriesPerPage><PageNumber>1</PageNumber></Pagination>
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
with urllib.request.urlopen(req, timeout=60) as r:
    root = ET.fromstring(r.read())


def q(el, tag):
    x = el.find(f".//{{{NS}}}{tag}")
    return x.text if x is not None and x.text else ""


ack = q(root, "Ack")
if ack not in ("Success", "Warning"):
    print("ACK:", ack)
    for e in root.iter(f"{{{NS}}}LongMessage"):
        print("ERR:", e.text)
    sys.exit(1)

orders = root.findall(f".//{{{NS}}}Order")
print(f"{len(orders)} orders in last {days} days\n")
for o in orders:
    oid = q(o, "OrderID")
    created = q(o, "CreatedTime")[:16]
    status = q(o, "OrderStatus")
    total = q(o, "Total")
    buyer_el = o.find(f".//{{{NS}}}BuyerUserID")
    buyer = buyer_el.text if buyer_el is not None else ""
    ship = o.find(f".//{{{NS}}}ShippingAddress")
    name = q(ship, "Name") if ship is not None else ""
    email = q(o, "Email")
    print(f"[{created}] {oid}  {status}  ${total}  buyer={buyer}  name={name}  {email}")
    for tx in o.findall(f".//{{{NS}}}Transaction"):
        title = q(tx, "Title")
        qty = q(tx, "QuantityPurchased")
        item = q(tx, "ItemID")
        price = q(tx, "TransactionPrice")
        specs = []
        for nv in tx.findall(f".//{{{NS}}}VariationSpecifics//{{{NS}}}NameValueList"):
            n = q(nv, "Name")
            vals = [v.text for v in nv.findall(f"{{{NS}}}Value") if v.text]
            specs.append(f"{n}={'/'.join(vals)}")
        var_title = ""
        v = tx.find(f".//{{{NS}}}Variation")
        if v is not None:
            vt = v.find(f"{{{NS}}}VariationTitle")
            if vt is not None and vt.text:
                var_title = vt.text
        line = f"    x{qty} ${price}  {title[:60]}  item={item}"
        if specs:
            line += "  [" + ", ".join(specs) + "]"
        if var_title:
            line += f"  <{var_title[:70]}>"
        print(line)
    print()
