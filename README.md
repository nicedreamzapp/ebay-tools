# ebay-tools

<a id="what"></a>
<picture><source media="(max-width: 610px), (min-width: 768px) and (max-width: 895px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s01-banner-m.svg"><source media="(max-width: 1149px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s01-banner-mid.svg"><img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s01-banner.svg" width="100%" alt="01. What it does. eBay store work from the command line"></picture>
<picture><source media="(max-width: 610px), (min-width: 768px) and (max-width: 895px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s01-r1-m.svg"><source media="(max-width: 1149px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s01-r1-mid.svg"><img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s01-r1.svg" width="100%" alt="No Seller Hub. Everything runs through eBay&#x27;s official APIs. No browser. Plain Python scripts, one job each. Agent-ready. Claude Code calls these from the command line for the day to day store work."></picture>

Small Python scripts that run an eBay store entirely through eBay's official APIs. No Seller Hub, no browser.

An AI agent (Claude Code) calls these from the command line to do the day to day store work.

<img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s01-rule.svg" width="100%" alt="">


<a id="scripts"></a>
<picture><source media="(max-width: 610px), (min-width: 768px) and (max-width: 895px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s02-banner-m.svg"><source media="(max-width: 1149px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s02-banner-mid.svg"><img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s02-banner.svg" width="100%" alt="02. The scripts. Two kinds of eBay credentials, two jobs"></picture>
<picture><source media="(max-width: 610px), (min-width: 768px) and (max-width: 895px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s02-r1-m.svg"><source media="(max-width: 1149px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s02-r1-mid.svg"><img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s02-r1.svg" width="100%" alt="Trading API. XML, EBAY_AUTH_TOKEN. Listings and orders. REST APIs. OAuth user token. Promotions and fulfillment."></picture>

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

<img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s02-rule.svg" width="100%" alt="">


<a id="setup"></a>
<picture><source media="(max-width: 610px), (min-width: 768px) and (max-width: 895px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s03-banner-m.svg"><source media="(max-width: 1149px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s03-banner-mid.svg"><img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s03-banner.svg" width="100%" alt="03. Setup. Python 3.7 or newer"></picture>
<picture><source media="(max-width: 610px), (min-width: 768px) and (max-width: 895px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s03-r1-m.svg"><source media="(max-width: 1149px)" srcset="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s03-r1-mid.svg"><img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s03-r1.svg" width="100%" alt="Python 3.7+. Get keys at developer.ebay.com. Hard-won lesson. AddMemberMessageAAQToPartner must include ItemID."></picture>

```
pip install python-dotenv requests
cp .env.example .env                    # fill in your keys
cp ebay_oauth.env.example ebay_oauth.env
python ebay_recent_orders.py
```

Get keys at developer.ebay.com. Needs Python 3.7 or newer.

One lesson learned the hard way: `AddMemberMessageAAQToPartner` must include `<ItemID>`. Leave it out and eBay replies `Ack=Success`, but the message is never delivered. `ebay_send_message.py` includes it and checks the Sent folder afterward.

<img src="https://raw.githubusercontent.com/nicedreamzapp/ebay-tools/1242efcc0a416e714f5f5110cbfa26a6b9b66f3f/assets/readme/s03-rule.svg" width="100%" alt="">

