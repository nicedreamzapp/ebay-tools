import sys, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import ebay_promote as p
tok = p._refresh()
for oid in sys.argv[1:]:
    req = urllib.request.Request(f"https://api.ebay.com/sell/fulfillment/v1/order/{oid}", headers={"Authorization": "Bearer "+tok})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    ps = d.get("paymentSummary", {})
    print("==", oid, d.get("orderPaymentStatus"), d.get("orderFulfillmentStatus"), "total", ps.get("totalDueSeller"), "refunds:", json.dumps(ps.get("refunds", [])), "cancel:", d.get("cancelStatus",{}).get("cancelState"))
    for li in d.get("lineItems", []):
        print("   ", li.get("quantity"), "x", li.get("title")[:60], li.get("variationAspects"), "refunds:", li.get("refunds"))
