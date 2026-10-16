# ebay-tools

Small Python scripts that run an eBay store entirely through eBay's official APIs. No Seller Hub, no browser.
An AI agent (Claude Code) calls these from the command line to do the day to day store work.

Two kinds of eBay credentials, two jobs:

**Trading API** (XML, `EBAY_AUTH_TOKEN`) handles listings and orders:

| Script | What it does |
|---|---|
| `ebay_variations.py` | list a listing's color/size variations and set their stock |
| `ebay_shipping_dims.py` | read or set package weight and dimensions |
| `ebay_item_api.py` | read a listing's details |
| `ebay_recent_orders.py` | recent orders with buyer and the variation they bought |
| `ebay_order_lookup.py` | look up one order |
| `ebay_order_full.py` | ship-to address and tracking for orders |
| `ebay_messages.py` | read buyer messages |
| `ebay_send_message.py` | reply to a buyer, then confirm it actually landed |
| `ebay_member_messages.py` | check the messages on a listing |

**REST APIs** (OAuth user token) handle the rest:

| Script | What it does |
|---|---|
| `ebay_promote.py` | Promoted Listings campaigns, ads and bid percentages (refreshes its own token) |
| `ebay_fulfill_order.py` | order payment and fulfillment state |

## Setup

```
pip install python-dotenv requests
cp .env.example .env                    # fill in your keys
cp ebay_oauth.env.example ebay_oauth.env
python ebay_recent_orders.py
```

Get keys at developer.ebay.com. Needs Python 3.7 or newer.

One lesson learned the hard way: `AddMemberMessageAAQToPartner` must include `<ItemID>`. Leave it out and eBay replies `Ack=Success`, but the message is never delivered. `ebay_send_message.py` includes it and checks the Sent folder afterward.
