# Contributing

Thanks for taking a look. These scripts run a real store through eBay's APIs, and eBay's APIs have
plenty of quiet failure modes, so a report of a call that "succeeded" but did nothing is very useful.

## Reporting a problem

Open an [issue](https://github.com/nicedreamzapp/ebay-tools/issues/new/choose). The things that
make it quick to fix:

- which script and the exact command you ran (with item and order IDs changed if you prefer)
- your Python version and OS
- the full output, including the `Ack` value and any eBay error code
- what you expected eBay to show afterward (in Seller Hub, the Sent folder, the listing)

Never paste your `.env`, `ebay_oauth.env` or any token into an issue.

## Running it locally

```bash
pip install python-dotenv requests
cp .env.example .env                    # fill in your keys
cp ebay_oauth.env.example ebay_oauth.env
python ebay_recent_orders.py
```

Get keys at developer.ebay.com. Needs Python 3.7 or newer.

## Tests

There are no automated tests. The scripts call the live eBay APIs, so check changes by hand
against your own store. Start with read-only scripts like `ebay_recent_orders.py` and
`ebay_item_api.py <ItemID>`, and only run scripts that change listings, stock, ads or messages
on items you are happy to change.

## Pull requests

Small and focused is easiest to review. For big changes, open an issue first so we can talk it
through. Say which eBay call you tested and what eBay returned. If you found another call that
replies `Ack=Success` without doing anything, a note in the README is the most helpful part.

Please follow the [code of conduct](CODE_OF_CONDUCT.md).
