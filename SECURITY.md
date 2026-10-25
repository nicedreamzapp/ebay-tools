# Security policy

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report them privately through GitHub: go to the **Security** tab of this repo and click **Report a vulnerability** ([direct link](https://github.com/nicedreamzapp/ebay-tools/security/advisories/new)). Only the maintainer sees the report.

Helpful details: what you found, how to reproduce it, which script and commit, and your Python version and OS. Leave out real tokens, buyer names and addresses.

I aim to reply within 3 days and to ship a fix or a clear plan within 30 days, depending on severity. You will be credited in the advisory unless you ask not to be.

## Supported versions

Fixes go into the latest version on `main`. Please update before reporting if you are on an older commit.

## What matters most here

The parts where a mistake could hurt someone:

- eBay credentials read from `.env` and `ebay_oauth.env` (app keys, the Trading API token and the OAuth refresh token), which must never be committed or printed
- `ebay_promote.py`, which refreshes the OAuth access token and writes it back to `ebay_oauth.env`
- buyer data returned by `ebay_order_full.py`, `ebay_order_lookup.py` and `ebay_recent_orders.py` (names and ship-to addresses)
- scripts that change the live store or contact buyers: `ebay_send_message.py`, `ebay_variations.py`, `ebay_shipping_dims.py` and `ebay_promote.py`
- XML requests built from command-line input, such as the item ID, subject and body in `ebay_send_message.py`
