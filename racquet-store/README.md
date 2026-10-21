# Rally Racquets

A responsive badminton racquet storefront with 28 supplier listings: 5 Yonex and 23 Li-Ning. Each product has its own static URL, an image gallery, an original description and sourced specifications.

The store includes brand and playing-style filters, model search, price sorting, image zoom, and a persistent shopping bag. Customers can select string tension on every product page, with optional stringing at A$10 per racquet. Different tensions remain separate bag items, and saved/copied enquiries include each tension and the stringing fee. Customers can save or copy an availability enquiry. Payments and order transmission are not connected; the site does not claim to accept paid orders.

## Pricing

The **dealer/seller column** in the supplied screenshots is the cost basis. Shoes, bags, shuttles and grips are excluded because this project is a racquet store.

- Reference rate: **1 AUD = 18,162.4 VND**.
- Rate snapshot: **21 October 2026, 06:51 UTC**, retrieved from [XE](https://www.xe.com/en-au/currencyconverter/convert/?Amount=1&From=AUD&To=VND).
- Selling price: `round(dealerVnd / 18162.4, 2) + 60 AUD`.
- The A$60 is a markup before shipping, foreign exchange costs, import costs, payment fees and taxes. It is not an assertion of net profit.
- Original retail and dealer values are preserved in `data/supplier.json`. Internal supplier pricing is excluded from the served catalogue.

## Edit and regenerate

```bash
python scripts/build.py
```

Serve `dist/` with any static web server. Every asset is local; there are no runtime third-party asset requests or package dependencies. All links are relative, so the site also works below a GitHub Pages subdirectory.

Edit `data/supplier.json` for prices, product names, descriptions, and the reference rate. Image manifests are `data/lining-assets.json`, `data/yonex-assets.json` and `data/yonex-two-assets.json`. Source URLs for each downloaded image are retained there. The finished catalogue and pricing audit is `data/catalogue.json`.

## Seller setup before taking orders

Confirm the exact supplier stock, weight and grip variants, stringing, colour, delivery charges and business contact details. Add your payment and order processing provider when ready to accept purchases. The current bag deliberately saves an enquiry rather than claiming that a customer has placed an order.

Photographs are genuine product images downloaded from the linked manufacturer and retailer pages. Some include the original retailer watermark, which has been preserved. Confirm commercial reuse permission with the relevant image owner before launching commercial advertising.

Rally Racquets is a working project name. The store is independent of the existing Cairns Badminton Club website concept in the parent repository.
