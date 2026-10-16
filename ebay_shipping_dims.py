"""View / set eBay listing package weight + dimensions (Trading API).

Usage:
  python ebay_shipping_dims.py list                 # all active listings (id, title)
  python ebay_shipping_dims.py show <itemid>        # current weight + package dims
  python ebay_shipping_dims.py set <itemid> <oz> <L> <W> <D>
"""
import os, sys
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TOKEN = os.getenv("EBAY_AUTH_TOKEN")
NS = "urn:ebay:apis:eBLBaseComponents"
Q = lambda t: f"{{{NS}}}{t}"


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
    with urllib.request.urlopen(req, timeout=90) as r:
        return ET.fromstring(r.read())


def errors(root):
    out = []
    for err in root.findall(f".//{Q('Errors')}"):
        out.append(f"{err.findtext(Q('SeverityCode'))}: {err.findtext(Q('LongMessage'))}")
    return out


def active():
    page, items = 1, []
    while True:
        root = call("GetMyeBaySelling",
                    "<ActiveList><Include>true</Include><Pagination>"
                    f"<EntriesPerPage>200</EntriesPerPage><PageNumber>{page}</PageNumber>"
                    "</Pagination></ActiveList>")
        found = root.findall(f".//{Q('ActiveList')}//{Q('Item')}")
        for it in found:
            items.append((it.findtext(Q('ItemID')), it.findtext(Q('Title'))))
        total = root.findtext(f".//{Q('ActiveList')}/{Q('PaginationResult')}/{Q('TotalNumberOfPages')}")
        if not total or page >= int(total):
            break
        page += 1
    return items


def pkg(item_id):
    root = call("GetItem", f"<ItemID>{item_id}</ItemID><DetailLevel>ReturnAll</DetailLevel>")
    it = root.find(f".//{Q('Item')}")
    d = it.find(f"{Q('ShippingPackageDetails')}") if it is not None else None
    g = (lambda t: (d.findtext(Q(t)) if d is not None else None))
    return {
        "title": it.findtext(Q('Title')) if it is not None else "?",
        "lbs": g('WeightMajor'), "oz": g('WeightMinor'),
        "L": g('PackageLength'), "W": g('PackageWidth'), "D": g('PackageDepth'),
        "package": g('ShippingPackage'), "unit": g('MeasurementUnit'),
        "type": it.findtext(f"{Q('ShippingDetails')}/{Q('ShippingType')}") if it is not None else None,
    }


def set_dims(item_id, oz, L, W, D):
    lbs, rem = divmod(int(oz), 16)
    body = f"""<Item><ItemID>{item_id}</ItemID>
  <ShippingPackageDetails>
    <MeasurementUnit>English</MeasurementUnit>
    <PackageLength>{L}</PackageLength>
    <PackageWidth>{W}</PackageWidth>
    <PackageDepth>{D}</PackageDepth>
    <WeightMajor measurementSystem="English" unit="lbs">{lbs}</WeightMajor>
    <WeightMinor measurementSystem="English" unit="oz">{rem}</WeightMinor>
  </ShippingPackageDetails></Item>"""
    root = call("ReviseFixedPriceItem", body)
    return root.findtext(Q('Ack')), errors(root)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "list":
        for iid, title in active():
            print(iid, "|", title)
    elif cmd == "show":
        print(pkg(sys.argv[2]))
    elif cmd == "set":
        iid, oz, L, W, D = sys.argv[2:7]
        ack, errs = set_dims(iid, oz, L, W, D)
        print(iid, "Ack:", ack)
        for e in errs:
            print("   ", e)
