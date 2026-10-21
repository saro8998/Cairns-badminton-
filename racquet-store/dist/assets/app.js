(() => {
  'use strict';
  const products = window.RALLY_PRODUCTS;
  const bySlug = new Map(products.map(p => [p.slug, p]));
  const base = document.body.dataset.base;
  const money = cents => new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD' }).format(cents / 100);
  const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
  const bagDialog = document.querySelector('.bag-dialog');
  const stringingFee = 1000;
  const validTension = (slug, value) => Number.isInteger(value) && value >= 20 && value <= (slug === 'yonex-arcsaber-11-tour' ? 27 : 28);
  const lineKey = item => `${item.slug}:${item.tension || 'unstrung'}`;
  const unitPrice = item => bySlug.get(item.slug).priceCents + (item.tension ? stringingFee : 0);
  const stringingLabel = item => item.tension ? `Strung at ${item.tension} lbs (+A$10.00 per racquet)` : 'No stringing service';
  let bag = [];
  try {
    const saved = JSON.parse(localStorage.getItem('rally-bag-v1') || '[]');
    if (Array.isArray(saved)) bag = saved.filter(i => bySlug.has(i.slug) && Number.isInteger(i.qty) && i.qty > 0).map(i => ({ slug:i.slug, qty:Math.min(i.qty, 99), tension:validTension(i.slug, i.tension) ? i.tension : null }));
  } catch { /* An empty bag remains usable when storage is unavailable. */ }
  let toastTimer;
  function toast(message) {
    const element = document.querySelector('.toast');
    element.textContent = message;
    element.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => element.classList.remove('visible'), 2800);
  }
  function saveBag() {
    try { localStorage.setItem('rally-bag-v1', JSON.stringify(bag)); } catch { /* Bag still works for this visit. */ }
    renderBag();
  }
  function renderBag() {
    const count = bag.reduce((sum, i) => sum + i.qty, 0);
    document.querySelectorAll('.bag-count').forEach(n => { n.textContent = count; });
    const items = document.querySelector('#bag-items');
    const summary = document.querySelector('#bag-summary');
    if (!bag.length) {
      items.innerHTML = '<div class="empty-bag"><span>READY WHEN YOU ARE</span><h3>Your next racquet<br>is out there.</h3><p>Explore the collection and find your fit.</p><a class="button button-dark" href="'+base+'#shop">Explore racquets <span>→</span></a></div>';
      summary.innerHTML = '';
      return;
    }
    items.innerHTML = bag.map(i => {
      const p = bySlug.get(i.slug);
      const key = lineKey(i);
      return `<article class="bag-item"><a href="${base}products/${p.slug}/"><img src="${base}${escape(p.images[0])}" alt="${escape(p.name)}" width="96" height="110"></a><div><span class="brand-label">${escape(p.brand)}</span><h3><a href="${base}products/${p.slug}/">${escape(p.name)}</a></h3><p class="bag-stringing">${stringingLabel(i)}</p><strong>${money(unitPrice(i))} each</strong><div class="bag-quantity"><button data-change="${key}" data-delta="-1" aria-label="Decrease ${escape(p.name)} ${i.tension || 'unstrung'} quantity">−</button><span>${i.qty}</span><button data-change="${key}" data-delta="1" aria-label="Increase ${escape(p.name)} ${i.tension || 'unstrung'} quantity">+</button><button class="remove-item" data-remove="${key}" aria-label="Remove ${escape(p.name)} ${i.tension || 'unstrung'}">Remove</button></div></div></article>`;
    }).join('');
    const total = bag.reduce((sum, i) => sum + i.qty * unitPrice(i), 0);
    const fees = bag.reduce((sum, i) => sum + (i.tension ? i.qty * stringingFee : 0), 0);
    summary.innerHTML = `<div class="bag-subtotal"><span>Subtotal</span><strong>${money(total)} <small>AUD</small></strong></div>${fees ? `<p class="bag-stringing">Includes ${money(fees)} stringing</p>` : ''}<p class="bag-disclaimer">Availability and delivery are confirmed before payment. Saving an enquiry does not place an order.</p><button class="button button-dark" data-save-enquiry>Save enquiry <span>↓</span></button><button class="copy-enquiry" data-copy-enquiry>Copy enquiry</button>`;
  }
  function enquiryText() {
    const total = bag.reduce((sum, i) => sum + i.qty * unitPrice(i), 0);
    return 'RALLY RACQUETS — AVAILABILITY ENQUIRY\n\n'+bag.map(i => {
      const p = bySlug.get(i.slug);
      return `${i.qty} × ${p.brand} ${p.name} — ${money(unitPrice(i))} each\nRacquet: ${money(p.priceCents)} each\nStringing: ${stringingLabel(i)}\nColour: ${p.colour}\nWeight/grip: ${p.weight}`;
    }).join('\n\n')+`\n\nSubtotal including selected stringing: ${money(total)} AUD\n\nPlease confirm stock, weight/grip, stringing, delivery costs and payment arrangements.\nThis is an enquiry, not a placed or paid order.\n\nMy name:\nMy contact details:\nDelivery postcode:\n`;
  }
  document.querySelectorAll('.bag-toggle').forEach(b => b.addEventListener('click', () => { renderBag(); bagDialog.showModal(); }));
  document.querySelector('[data-close-bag]').addEventListener('click', () => bagDialog.close());
  bagDialog.addEventListener('click', async event => {
    if (event.target === bagDialog) bagDialog.close();
    const change = event.target.closest('[data-change]');
    if (change) {
      const item = bag.find(i => lineKey(i) === change.dataset.change);
      item.qty = Math.max(0, Math.min(99, item.qty + Number(change.dataset.delta)));
      bag = bag.filter(i => i.qty > 0);
      saveBag();
    }
    const remove = event.target.closest('[data-remove]');
    if (remove) { bag = bag.filter(i => lineKey(i) !== remove.dataset.remove); saveBag(); }
    if (event.target.closest('[data-save-enquiry]')) {
      const url = URL.createObjectURL(new Blob([enquiryText()], { type:'text/plain;charset=utf-8' }));
      const a = document.createElement('a'); a.href = url; a.download = 'rally-racquets-enquiry.txt'; a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      toast('Enquiry saved. Share it with the seller to confirm your selection.');
    }
    if (event.target.closest('[data-copy-enquiry]')) {
      try { await navigator.clipboard.writeText(enquiryText()); toast('Enquiry copied.'); }
      catch { toast('Use “Save enquiry” to download your selection.'); }
    }
  });
  const info = document.querySelector('.info-dialog');
  document.querySelectorAll('[data-info]').forEach(b => b.addEventListener('click', () => info.showModal()));
  document.querySelector('.close-info').addEventListener('click', () => info.close());
  info.addEventListener('click', e => { if (e.target === info) info.close(); });

  const currentSlug = document.querySelector('[data-current-product]')?.dataset.currentProduct;
  if (currentSlug) {
    const quantity = document.querySelector('#product-quantity');
    const tensionSelect = document.querySelector('#string-tension');
    const selectedTension = () => validTension(currentSlug, Number(tensionSelect.value)) ? Number(tensionSelect.value) : null;
    tensionSelect.addEventListener('change', () => {
      const tension = selectedTension();
      document.querySelector('#selected-price').textContent = `A${money(bySlug.get(currentSlug).priceCents + (tension ? stringingFee : 0))}`;
      document.querySelector('#stringing-price-note').textContent = tension ? `Includes A$10.00 stringing at ${tension} lbs, per racquet.` : 'Stringing is optional: A$10.00 per racquet.';
    });
    const clamp = () => { quantity.value = Math.min(99, Math.max(1, parseInt(quantity.value, 10) || 1)); return Number(quantity.value); };
    quantity.addEventListener('change', clamp);
    document.querySelector('[data-product-minus]').addEventListener('click', () => { quantity.value = clamp() - 1; clamp(); });
    document.querySelector('[data-product-plus]').addEventListener('click', () => { quantity.value = clamp() + 1; clamp(); });
    document.querySelector('[data-add]').addEventListener('click', () => {
      const tension = selectedTension();
      const existing = bag.find(i => i.slug === currentSlug && i.tension === tension);
      if (existing) existing.qty = Math.min(99, existing.qty + clamp());
      else bag.push({ slug:currentSlug, qty:clamp(), tension });
      saveBag(); bagDialog.showModal();
    });
    const mainPhoto = document.querySelector('#main-product-photo');
    document.querySelectorAll('[data-gallery-src]').forEach(button => button.addEventListener('click', () => {
      mainPhoto.src = button.dataset.gallerySrc;
      document.querySelectorAll('[data-gallery-src]').forEach(b => { b.classList.toggle('active', b === button); b.setAttribute('aria-pressed', String(b === button)); });
    }));
    const zoom = document.querySelector('.zoom-dialog');
    document.querySelector('.main-photo').addEventListener('click', () => { const img = zoom.querySelector('img'); img.src = mainPhoto.src; img.alt = mainPhoto.alt; zoom.showModal(); });
    document.querySelector('.close-zoom').addEventListener('click', () => zoom.close());
    zoom.addEventListener('click', e => { if (e.target === zoom) zoom.close(); });
  }

  const grid = document.querySelector('#product-grid');
  if (grid) {
    const params = new URLSearchParams(location.search);
    const state = { brand:['Yonex','Li-Ning'].includes(params.get('brand')) ? params.get('brand') : 'all', style:['Power','Control','Speed','All-round'].includes(params.get('style')) ? params.get('style') : 'all', query:params.get('q') || '', sort:params.get('sort') || 'featured' };
    const cards = new Map([...grid.children].map(card => [card.dataset.product, card]));
    const search = document.querySelector('#search');
    const sort = document.querySelector('#sort');
    search.value = state.query;
    if ([...sort.options].some(o => o.value === state.sort)) sort.value = state.sort;
    function filter() {
      const query = state.query.toLocaleLowerCase().trim();
      let matches = products.filter(p => (state.brand === 'all' || p.brand === state.brand) && (state.style === 'all' || p.style === state.style) && `${p.brand} ${p.name} ${p.series} ${p.colour}`.toLocaleLowerCase().includes(query));
      if (state.sort === 'price-low') matches.sort((a,b) => a.priceCents - b.priceCents);
      if (state.sort === 'price-high') matches.sort((a,b) => b.priceCents - a.priceCents);
      if (state.sort === 'name') matches.sort((a,b) => a.name.localeCompare(b.name));
      const visible = new Set(matches.map(p => p.slug));
      cards.forEach((card,slug) => { card.hidden = !visible.has(slug); });
      matches.forEach(p => grid.append(cards.get(p.slug)));
      document.querySelectorAll('[data-brand]').forEach(b => { b.classList.toggle('active', b.dataset.brand === state.brand); b.setAttribute('aria-pressed', String(b.dataset.brand === state.brand)); });
      document.querySelectorAll('[data-style]').forEach(b => { b.classList.toggle('active', b.dataset.style === state.style); b.setAttribute('aria-pressed', String(b.dataset.style === state.style)); });
      document.querySelector('#result-count').textContent = `${matches.length} racquet${matches.length === 1 ? '' : 's'}`;
      document.querySelector('#empty-results').hidden = matches.length > 0;
      const next = new URL(location.href);
      next.search = '';
      if (state.brand !== 'all') next.searchParams.set('brand', state.brand);
      if (state.style !== 'all') next.searchParams.set('style', state.style);
      if (state.query) next.searchParams.set('q', state.query);
      if (state.sort !== 'featured') next.searchParams.set('sort', state.sort);
      history.replaceState(null, '', next);
    }
    document.querySelectorAll('[data-brand]').forEach(b => b.addEventListener('click', () => { state.brand = b.dataset.brand; filter(); }));
    document.querySelectorAll('[data-style]').forEach(b => b.addEventListener('click', () => { state.style = b.dataset.style; filter(); }));
    search.addEventListener('input', () => { state.query = search.value; filter(); });
    sort.addEventListener('change', () => { state.sort = sort.value; filter(); });
    document.querySelector('#reset-filters').addEventListener('click', () => { state.brand = state.style = 'all'; state.query = ''; search.value = ''; filter(); });
    filter();
    if (params.has('search')) search.focus({ preventScroll:true });
  }
  renderBag();
})();
