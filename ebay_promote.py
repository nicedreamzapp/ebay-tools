"""eBay Promoted Listings (Marketing API) — campaigns and ads.

Auth: OAuth user token in ebay_oauth.env (refresh token good ~18 months);
access token is refreshed automatically and written back.

Usage:
  python ebay_promote.py campaigns                       # list campaigns
  python ebay_promote.py ads <campaign_id>               # list ads in a campaign
  python ebay_promote.py create "<name>"                 # new COST_PER_SALE campaign
  python ebay_promote.py add <campaign_id> <bid%> <itemid> [itemid ...]
  python ebay_promote.py bid <campaign_id> <bid%> <itemid> [itemid ...]
"""
import os, sys, json, base64, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_ENV = os.path.join(HERE, ".env")
OAUTH_ENV = os.path.join(HERE, "ebay_oauth.env")
load_dotenv(BASE_ENV)
load_dotenv(OAUTH_ENV, override=True)

API = "https://api.ebay.com/sell/marketing/v1"


def _refresh():
    cid, csec = os.getenv("EBAY_APP_ID"), os.getenv("EBAY_CERT_ID")
    auth = base64.b64encode(f"{cid}:{csec}".encode()).decode()
    scopes = " ".join([
        "https://api.ebay.com/oauth/api_scope",
        "https://api.ebay.com/oauth/api_scope/sell.marketing",
        "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "https://api.ebay.com/oauth/api_scope/sell.account",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    ])
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("EBAY_OAUTH_REFRESH_TOKEN"),
        "scope": scopes}).encode()
    req = urllib.request.Request("https://api.ebay.com/identity/v1/oauth2/token", data=data,
        headers={"Authorization": f"Basic {auth}",
                 "Content-Type": "application/x-www-form-urlencoded"})
    tok = json.load(urllib.request.urlopen(req, timeout=30))["access_token"]
    lines = []
    for line in open(OAUTH_ENV, encoding="utf-8"):
        if line.startswith("EBAY_OAUTH_ACCESS_TOKEN="):
            line = f"EBAY_OAUTH_ACCESS_TOKEN={tok}\n"
        lines.append(line)
    open(OAUTH_ENV, "w", encoding="utf-8").writelines(lines)
    os.environ["EBAY_OAUTH_ACCESS_TOKEN"] = tok
    return tok


def call(method, path, body=None, _retry=True):
    tok = os.getenv("EBAY_OAUTH_ACCESS_TOKEN")
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                 "Accept": "application/json", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {"status": r.status}
    except urllib.error.HTTPError as e:
        if e.code == 401 and _retry:
            _refresh()
            return call(method, path, body, _retry=False)
        return {"error": e.code, "body": e.read().decode()[:1200]}


def campaigns():
    return call("GET", "/ad_campaign?limit=50")


def create(name):
    start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return call("POST", "/ad_campaign", {
        "campaignName": name,
        "startDate": start,
        "marketplaceId": "EBAY_US",
        "fundingStrategy": {"fundingModel": "COST_PER_SALE"},
    })


def add(campaign_id, bid, item_ids):
    return call("POST", f"/ad_campaign/{campaign_id}/bulk_create_ads_by_listing_id",
                {"requests": [{"listingId": str(i), "bidPercentage": str(bid)} for i in item_ids]})


def bid(campaign_id, pct, item_ids):
    return call("POST", f"/ad_campaign/{campaign_id}/bulk_update_ads_bid_by_listing_id",
                {"requests": [{"listingId": str(i), "bidPercentage": str(pct)} for i in item_ids]})


def remove(campaign_id, item_ids):
    return call("POST", f"/ad_campaign/{campaign_id}/bulk_delete_ads_by_listing_id",
                {"requests": [{"listingId": str(i)} for i in item_ids]})


def ads(campaign_id):
    return call("GET", f"/ad_campaign/{campaign_id}/ad?limit=200")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "campaigns":
        out = campaigns()
    elif cmd == "create":
        out = create(sys.argv[2])
    elif cmd == "ads":
        out = ads(sys.argv[2])
    elif cmd == "add":
        out = add(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif cmd == "bid":
        out = bid(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif cmd == "remove":
        out = remove(sys.argv[2], sys.argv[3:])
    else:
        out = {"error": f"unknown command {cmd}"}
    print(json.dumps(out, indent=1)[:4000])
