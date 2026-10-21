"""Generate a portable static store with a real URL for every product."""
import json, pathlib, html, shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
supplier = json.loads((ROOT/'data/supplier.json').read_text())
products = supplier['products']

def e(value):
    return html.escape(str(value), quote=True)

for filename in ['lining-assets.json', 'yonex-assets.json', 'yonex-two-assets.json']:
    path = ROOT/'data'/filename
    if not path.exists():
        continue
    mapping = json.loads(path.read_text())
    if isinstance(mapping,list):
        mapping = {p['slug']:p for p in mapping}
    for p in products:
        asset = mapping.get(p['slug'])
        if not asset:
            continue
        if asset.get('productSource'):
            p.setdefault('imageProductSource',asset['productSource'])
            p.setdefault('source',asset['productSource'])
        for k in ['images','imageSources','source','sources','description','summary','specs','flex']:
            if asset.get(k) and (k not in p or k in ['images','imageSources']):
                p[k] = asset[k]
        if not p.get('colour') and (asset.get('colour') or asset.get('color')):
            p['colour'] = asset.get('colour',asset.get('color'))
        if asset.get('description') and not p.get('summary'):
            p['summary'] = asset['description'].split('. ')[0].rstrip('.')+'.'
        p['imageNote'] = asset.get('imageNote','')

for p in products:
    p['priceCents'] = int(p['dealerVnd']/supplier['pricing']['vndPerAud']*100+0.5)+int(supplier['pricing']['markupAud']*100)
    p.setdefault('weight','Confirm weight and grip on enquiry')
    p.setdefault('colour','Confirm colour on enquiry')
    p.setdefault('summary',f"Discover the {p['name']} from Li-Ning’s {p['series']} collection.")
    p.setdefault('description',p['summary'])
    p.setdefault('specs',{})
    p.setdefault('images',[])
    p.setdefault('flex','Confirm on enquiry')

def money(p):
    return f"A${p['priceCents']/100:,.2f}"

def icon(name):
    paths = {
        'arrow':'<path d="M5 12h14M13 6l6 6-6 6"/>',
        'bag':'<path d="M5 7h14l1 14H4L5 7Z"/><path d="M8 8V6a4 4 0 0 1 8 0v2"/>',
        'search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
        'close':'<path d="m6 6 12 12M18 6 6 18"/>',
        'plus':'<path d="M12 5v14M5 12h14"/>',
        'check':'<path d="m5 12 4 4L19 6"/>',
    }
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{paths[name]}</svg>'

def header(base):
    return f'''<a class="skip-link" href="#main">Skip to content</a>
    <div class="announcement">GOOD GAMES START WITH THE RIGHT GEAR <span>YONEX + LI-NING · ALL PRICES IN AUD</span></div>
    <header class="site-header"><div class="header-inner">
    <a class="logo" href="{base}" aria-label="Rally Racquets home"><span class="logo-mark">R<span>.</span></span><span>RALLY<small>RACQUETS</small></span></a>
    <nav aria-label="Main navigation"><a href="{base}#shop">All racquets</a><a href="{base}?brand=Yonex#shop">Yonex</a><a href="{base}?brand=Li-Ning#shop">Li-Ning</a><a href="{base}#your-game">Find your fit</a></nav>
    <div class="header-actions"><a class="icon-button search-link" href="{base}?search=1#shop" aria-label="Search racquets">{icon('search')}</a><button class="bag-toggle" type="button" aria-label="Open shopping bag">{icon('bag')}<span class="bag-label">Bag</span><span class="bag-count">0</span></button></div>
    </div></header>'''

def footer(base):
    return f'''<footer class="site-footer"><div class="footer-top"><a class="logo" href="{base}"><span class="logo-mark">R<span>.</span></span><span>RALLY<small>RACQUETS</small></span></a><p>For the love of the next rally.</p><a href="{base}#shop">Find your next racquet {icon('arrow')}</a></div><div class="footer-bottom"><span>© 2026 Rally Racquets</span><span>Yonex & Li-Ning · Priced in Australian dollars</span><button type="button" data-info>Orders & delivery</button></div></footer>'''

def overlays():
    return f'''<dialog class="bag-dialog" aria-labelledby="bag-title"><div class="bag-shell"><div class="drawer-heading"><div><span class="eyebrow">YOUR NEXT GAME</span><h2 id="bag-title">Your bag <span class="bag-count">0</span></h2></div><button class="icon-button" data-close-bag aria-label="Close bag">{icon('close')}</button></div><div id="bag-items"></div><div id="bag-summary"></div></div></dialog>
    <dialog class="info-dialog" aria-labelledby="info-title"><button class="icon-button close-info" aria-label="Close information">{icon('close')}</button><span class="eyebrow">A LITTLE MORE DETAIL</span><h2 id="info-title">Before your next rally.</h2><h3>Availability & ordering</h3><p>Choose your racquets and add them to your bag. Save or copy your enquiry to share with the seller. Stock, weight, grip size and stringing are confirmed before an order is placed.</p><h3>Delivery & payment</h3><p>Delivery costs and payment arrangements are confirmed by the seller before you pay. Online payments are not available yet.</p><h3>Product photographs</h3><p>Photos show the model and colour shown in the listing. Where the supplier has not specified a colour or weight, confirm the exact version when enquiring.</p></dialog>
    <dialog class="zoom-dialog" aria-label="Enlarged product photo"><button class="icon-button close-zoom" aria-label="Close enlarged photo">{icon('close')}</button><img alt=""></dialog>
    <div class="toast" role="status" aria-live="polite"></div>'''

def card(p,base):
    image = p['images'][0] if p['images'] else ''
    return f'''<article class="product-card" data-product="{e(p['slug'])}"><a class="card-photo" href="{base}products/{p['slug']}/"><span class="card-tag">{e(p['style'])}</span><img src="{base}{e(image)}" alt="{e(p['brand']+' '+p['name'])}" loading="lazy" width="600" height="600"><span class="card-view">Explore racquet {icon('arrow')}</span></a><div class="card-meta"><span class="brand-label">{e(p['brand'])}</span><span>{e(p.get('weight','')) if len(p.get('weight',''))<7 else e(p['series'])}</span></div><h3><a href="{base}products/{p['slug']}/">{e(p['name'])}</a></h3><p class="card-summary">{e(p['summary'])}</p><div class="card-bottom"><span class="price">{money(p)}</span><a class="card-arrow" href="{base}products/{p['slug']}/" aria-label="View {e(p['name'])}">{icon('arrow')}</a></div></article>'''

def shell(title,description,body,base='./',extra=''):
    return f'''<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#173d31"><title>{e(title)}</title><meta name="description" content="{e(description)}"><link rel="icon" type="image/svg+xml" href="{base}assets/favicon.svg"><link rel="stylesheet" href="{base}assets/styles.css">{extra}</head><body data-base="{base}">{header(base)}{body}{footer(base)}{overlays()}<script src="{base}assets/catalog.js"></script><script src="{base}assets/app.js" defer></script></body></html>'''

def home():
    hero1=next(p for p in products if p['slug']=='yonex-astrox-77-tour')
    hero2=next(p for p in products if p['slug']=='lining-halbertec-9000-power')
    im1=hero1['images'][0] if hero1['images'] else ''
    im2=hero2['images'][0] if hero2['images'] else ''
    low=min(p['priceCents'] for p in products)/100
    body=f'''<main id="main"><section class="hero"><div class="hero-copy"><span class="eyebrow"><span class="little-line"></span> MADE FOR YOUR NEXT LEVEL</span><h1>YOUR GAME.<br>YOUR <em>RACQUET.</em></h1><p>From the first serve to match point.<br>Find the Yonex or Li-Ning that feels like you.</p><a class="button button-dark" href="#shop">Shop the collection {icon('arrow')}</a><div class="hero-foot"><span class="hero-dot"></span>28 racquets. Two great brands. Your next move.</div></div><div class="hero-art"><span class="court-line line-one"></span><span class="court-line line-two"></span><span class="hero-watermark">RALLY</span><a href="products/{hero1['slug']}/" class="hero-racquet one"><img src="{im1}" alt="{e(hero1['brand']+' '+hero1['name'])}" width="600" height="600"><span>01 / YONEX<small>{e(hero1['name'])}</small></span></a><a href="products/{hero2['slug']}/" class="hero-racquet two"><img src="{im2}" alt="Li-Ning Halbertec 9000 Power" width="600" height="600"><span>02 / LI-NING<small>Halbertec 9000 Power</small></span></a><div class="hero-roundel">FIND YOUR<br><strong>SWEET<br>SPOT.</strong><span>↗</span></div><span class="art-caption">PRECISION. POWER. PLAY.</span></div></section>
    <div class="brand-strip"><span>THE RIGHT GEAR.<br><b>THE BETTER GAME.</b></span><span class="brand-yonex">YONEX</span><span class="brand-lining">LI-NING</span><div>Racquets from <strong>A${low:.2f}</strong><small>Find your next favourite.</small></div></div>
    <section class="shop-section section-wrap" id="shop"><div class="section-heading"><div><span class="eyebrow">THE RACQUET COLLECTION</span><h2>Find your advantage.</h2></div><p>Quick hands. Big smashes. Pinpoint control.<br>There’s a racquet for your kind of game.</p></div><div class="shop-toolbar"><div class="brand-filters" role="group" aria-label="Filter by brand"><button class="active" data-brand="all" aria-pressed="true">All racquets <span>28</span></button><button data-brand="Yonex" aria-pressed="false">Yonex <span>5</span></button><button data-brand="Li-Ning" aria-pressed="false">Li-Ning <span>23</span></button></div><div class="shop-tools"><label class="search-field">{icon('search')}<input id="search" type="search" placeholder="Find a racquet…" aria-label="Search racquets"></label><select id="sort" aria-label="Sort racquets"><option value="featured">Featured</option><option value="price-low">Price: low to high</option><option value="price-high">Price: high to low</option><option value="name">Name: A–Z</option></select></div></div><div class="filter-line"><div class="style-filters" role="group" aria-label="Filter by playing style"><button data-style="all" aria-pressed="true" class="active">Every game</button><button data-style="Power" aria-pressed="false">Power</button><button data-style="Control" aria-pressed="false">Control</button><button data-style="Speed" aria-pressed="false">Speed</button><button data-style="All-round" aria-pressed="false">All-round</button></div><span id="result-count" aria-live="polite">28 racquets</span></div><div class="product-grid" id="product-grid">{''.join(card(p,'./') for p in products)}</div><div class="empty-results" id="empty-results" hidden><h3>No racquets found.</h3><p>Try another model, brand or playing style.</p><button class="button button-dark" id="reset-filters">Clear filters {icon('arrow')}</button></div></section>
    <section class="game-guide section-wrap" id="your-game"><div class="guide-intro"><span class="eyebrow">PLAY YOUR WAY</span><h2>Different games.<br>Same obsession.</h2><p>A little direction for your next racquet.</p></div><a href="?style=Power#shop" class="guide-card"><span>01 / POWER</span><h3>Own the<br>back court.</h3><p>For players who love a deep clear and a committed attack.</p>{icon('arrow')}</a><a href="?style=Control#shop" class="guide-card"><span>02 / CONTROL</span><h3>Place it.<br>Don’t chase it.</h3><p>For thoughtful placement, net play and shaping the rally.</p>{icon('arrow')}</a><a href="?style=Speed#shop" class="guide-card"><span>03 / SPEED</span><h3>Be there.<br>Before the shuttle.</h3><p>For quick exchanges, lively drives and reactive defence.</p>{icon('arrow')}</a></section>
    <section class="closing-banner section-wrap"><div><span class="eyebrow">SEE YOU ON COURT</span><h2>Make the next rally yours.</h2></div><a class="button button-cream" href="#shop">Find my racquet {icon('arrow')}</a></section></main>'''
    (OUT/'index.html').write_text(shell('Rally Racquets | Yonex & Li-Ning Badminton Racquets', 'Find your next badminton racquet. Shop 28 Yonex and Li-Ning racquets with AUD prices, detailed descriptions and product photo galleries.',body))

def product_page(p):
    base='../../'
    images=p['images']
    gallery=''.join(f'<button class="gallery-thumb {"active" if i==0 else ""}" data-gallery-src="{base}{e(image)}" aria-label="View photo {i+1} of {e(p["name"])}" aria-pressed="{"true" if i==0 else "false"}"><img src="{base}{e(image)}" alt="{e(p["name"])} — photo {i+1}" width="100" height="100"></button>' for i,image in enumerate(images))
    specs={'Brand':p['brand'],'Series':p['series'],'Colour':p['colour'],'Weight / grip':p['weight'],**p['specs']}
    related=[x for x in products if x['brand']==p['brand'] and x['slug']!=p['slug']]
    related.sort(key=lambda x:(x['style']!=p['style'],abs(x['priceCents']-p['priceCents'])))
    img=images[0] if images else ''
    note=f'<p class="image-note">{e(p["imageNote"])}</p>' if p.get('imageNote') else ''
    body=f'''<main id="main" data-current-product="{p['slug']}"><div class="breadcrumb section-wrap"><a href="{base}">Home</a><span>/</span><a href="{base}?brand={e(p['brand'])}#shop">{e(p['brand'])}</a><span>/</span><span>{e(p['name'])}</span></div><section class="product-layout section-wrap"><div class="gallery"><div class="main-photo-wrap"><span class="product-style">{e(p['style'])} / {e(p['series'])}</span><button class="main-photo" aria-label="Enlarge {e(p['name'])} photo"><img id="main-product-photo" src="{base}{e(img)}" alt="{e(p['brand']+' '+p['name'])}" width="900" height="900"></button><span class="zoom-hint">Click image to explore</span></div><div class="gallery-thumbs">{gallery}</div>{note}</div><div class="product-detail"><span class="eyebrow">{e(p['brand'])} / {e(p['series'])}</span><h1>{e(p['name'])}</h1><p class="product-lead">{e(p['summary'])}</p><div class="product-price">{money(p)} <small>AUD</small></div><span class="availability"><span></span>Availability on enquiry</span><div class="product-options"><div><span>COLOUR</span><strong>{e(p['colour'])}</strong></div><div><span>WEIGHT / GRIP</span><strong>{e(p['weight'])}</strong></div></div><div class="product-purchase"><label class="quantity-picker"><span class="sr-only">Quantity</span><button type="button" data-product-minus aria-label="Decrease quantity">−</button><input id="product-quantity" type="number" min="1" max="99" value="1" inputmode="numeric" aria-label="Quantity"><button type="button" data-product-plus aria-label="Increase quantity">+</button></label><button class="button button-dark add-to-bag" data-add="{p['slug']}">Add to bag {icon('plus')}</button></div><p class="order-note">Confirm availability, exact specification and delivery before payment. <button data-info>How ordering works</button></p><div class="product-description"><h2>Meet your next racquet.</h2><p>{e(p['description'])}</p></div><details class="product-accordion" open><summary>Racquet specifications <span>+</span></summary><dl>{''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in specs.items())}</dl></details><details class="product-accordion"><summary>Ordering & delivery <span>+</span></summary><p>Add your selection to the bag and save or copy your enquiry. The seller will confirm stock, the exact weight and grip, stringing, delivery costs and payment arrangements before you place an order. Online payments are not available yet.</p></details></div></section><section class="related-section section-wrap"><div class="section-heading"><div><span class="eyebrow">KEEP YOUR OPTIONS OPEN</span><h2>Also in your corner.</h2></div><a class="text-link" href="{base}?brand={e(p['brand'])}#shop">Explore {e(p['brand'])} {icon('arrow')}</a></div><div class="product-grid">{''.join(card(x,base) for x in related[:4])}</div></section></main>'''
    path=OUT/'products'/p['slug'];path.mkdir(parents=True,exist_ok=True)
    structured={'@context':'https://schema.org','@type':'Product','name':p['brand']+' '+p['name'],'description':p['description'],'brand':{'@type':'Brand','name':p['brand']},'sku':p['slug']}
    extra='<script type="application/ld+json">'+json.dumps(structured).replace('</','<\\/')+'</script>'
    (path/'index.html').write_text(shell(p['brand']+' '+p['name']+' | '+money(p)+' | Rally Racquets',p['summary'],body,base,extra))

if __name__=='__main__':
    public_keys=['slug','brand','name','series','style','colour','weight','summary','description','specs','priceCents','images','imageNote']
    public=[{k:p[k] for k in public_keys if k in p} for p in products]
    (OUT/'assets/catalog.js').write_text('window.RALLY_PRODUCTS = '+json.dumps(public,ensure_ascii=False)+';\n')
    home()
    for p in products:
        product_page(p)
    (ROOT/'data/catalogue.json').write_text(json.dumps({'pricing':supplier['pricing'],'products':products},indent=2,ensure_ascii=False))
    print(f'Generated storefront + {len(products)} product pages; '+str(sum(len(p['images']) for p in products))+' product images')
