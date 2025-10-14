let i18n = { en: {}, ar: {}, tr: {} };

const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

const themeToggle = document.getElementById('themeToggle');
const langEn = document.getElementById('langEn');
const langAr = document.getElementById('langAr');
const langTr = document.getElementById('langTr');
const linkInput = document.getElementById('linkInput');
const grabForm = document.getElementById('grabForm');
const results = document.getElementById('results');
const titleEl = document.getElementById('title');
const platformEl = document.getElementById('platform');
const thumbEl = document.getElementById('thumb');
const formatsEl = document.getElementById('formats');
const loader = document.getElementById('loader');
const qualitySelect = document.getElementById('qualitySelect');
const mp3Toggle = document.getElementById('mp3Toggle');
const downloadBtn = document.getElementById('downloadBtn');
const toast = document.getElementById('toast');

// Theme
const savedTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', savedTheme);
themeToggle?.addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
});

// Language
const savedLang = localStorage.getItem('lang') || 'en';
loadLang(savedLang).then(() => setLang(savedLang));
langEn?.addEventListener('click', () => loadLang('en').then(() => setLang('en')));
langAr?.addEventListener('click', () => loadLang('ar').then(() => setLang('ar')));
langTr?.addEventListener('click', () => loadLang('tr').then(() => setLang('tr')));

async function loadLang(lang){
  try{
    const res = await fetch(`/i18n/${lang}.json`);
    const data = await res.json();
    i18n[lang] = data;
  }catch(e){
    console.warn('Failed to load lang', lang, e);
  }
}

function setLang(lang){
  localStorage.setItem('lang', lang);
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = i18n[lang][key];
  });
  document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
  langEn?.classList.toggle('active', lang === 'en');
  langAr?.classList.toggle('active', lang === 'ar');
  langTr?.classList.toggle('active', lang === 'tr');
}

// Micro animation on submit button
function pulse(el){
  el.animate([
    { transform: 'scale(1)' },
    { transform: 'scale(1.03)' },
    { transform: 'scale(1)' }
  ], { duration: 180, easing: 'ease-out' });
}

// Fetch inspect
grabForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = grabForm.querySelector('button');
  pulse(btn);
  const url = linkInput.value.trim();
  if (!url) return;
  if (!navigator.onLine) { showToast('You are offline'); return; }

  btn.disabled = true; btn.textContent = savedLang === 'ar' ? 'جاري الجلب...' : 'Fetching...';
  if (loader) loader.hidden = false;
  try{
    const res = await fetch('/api/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    renderResults(data);
  }catch(err){
    showToast(savedLang === 'ar' ? ('فشل الجلب: ' + err) : ('Fetch failed: ' + err));
  }finally{
    btn.disabled = false; btn.textContent = i18n[savedLang].downloadBtn;
    if (loader) loader.hidden = true;
  }
});

function renderResults(data){
  results.hidden = false;
  titleEl.textContent = data.title || '';
  platformEl.textContent = data.platform || '';
  thumbEl.src = data.thumbnail || '';
  formatsEl.innerHTML = '';
  if (qualitySelect) qualitySelect.innerHTML = '';

  const byQuality = (a,b) => (b.height||0) - (a.height||0);
  let formats = (data.formats||[]).sort(byQuality);
  formats = formats.filter(f => !String(f.id||'').startsWith('sb'));
  if (qualitySelect){
    const seen = new Set();
    for (const f of formats){
      const key = `${f.id}`;
      if (seen.has(key)) continue; seen.add(key);
      const opt = document.createElement('option');
      const label = `${f.height ? f.height+'p' : (f.ext||'file')} • ${f.ext||''} ${f.vcodec||''}/${f.acodec||''}`;
      opt.value = f.id; opt.textContent = label;
      qualitySelect.append(opt);
    }
    if (!qualitySelect.options.length){
      const opt = document.createElement('option'); opt.textContent = 'No formats found'; qualitySelect.append(opt);
    }
  }
  for (const f of formats){
    const div = document.createElement('div');
    div.className = 'format-item';
    const head = document.createElement('div'); head.className = 'format-head';
    const name = document.createElement('div');
    name.textContent = `${f.height ? f.height+'p' : (f.ext||'file')} · ${f.ext||''}`;
    const badges = document.createElement('div'); badges.className = 'badges';
    const b1 = document.createElement('span'); b1.className = 'badge'; b1.textContent = f.format_note || '';
    const b2 = document.createElement('span'); b2.className = 'badge'; b2.textContent = f.vcodec || '';
    const b3 = document.createElement('span'); b3.className = 'badge'; b3.textContent = f.acodec || '';
    badges.append(b1,b2,b3);
    head.append(name, badges);

    const actions = document.createElement('div'); actions.className = 'actions-row';
    const a1 = document.createElement('a');
    a1.className = 'btn small ghost';
    a1.textContent = savedLang === 'ar' ? 'رابط مباشر' : 'Direct Link';
    a1.href = f.url; a1.target = '_blank'; a1.rel = 'noopener';

    const a2 = document.createElement('button');
    a2.className = 'btn small primary';
    a2.textContent = savedLang === 'ar' ? 'تحميل عبر الخادم' : 'Download via server';
    a2.addEventListener('click', () => downloadViaServer(data.webpage_url, f.id));

    const a3 = document.createElement('button');
    a3.className = 'btn small ghost';
    a3.textContent = savedLang === 'ar' ? 'تحويل إلى MP3' : 'Convert to MP3';
    a3.addEventListener('click', () => downloadViaServer(data.webpage_url, f.id, true));

    actions.append(a1, a2, a3);
    div.append(head, actions);
    formatsEl.append(div);
  }
}

async function downloadViaServer(url, format_id, to_mp3=false){
  try{
    const res = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, format_id, to_mp3 })
    });
    if (!res.ok) throw new Error(await res.text());
    // Stream back as a blob then trigger download
    const blob = await res.blob();
    const dlUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = dlUrl;
    const cd = res.headers.get('Content-Disposition') || '';
    const match = cd.match(/filename="?([^";]+)"?/i);
    a.download = match ? match[1] : 'download';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(dlUrl), 5000);
  }catch(err){
    showToast(savedLang === 'ar' ? ('فشل التحميل: ' + err) : ('Download failed: ' + err));
  }
}

downloadBtn?.addEventListener('click', () => {
  const url = linkInput.value.trim();
  const fid = qualitySelect?.value;
  const toMp3 = !!mp3Toggle?.checked;
  if (!url) { showToast(savedLang === 'ar' ? 'الرجاء إدخال الرابط' : 'Please enter a URL'); return; }
  if (!fid && !toMp3) { showToast(savedLang === 'ar' ? 'اختر الجودة أو MP3' : 'Choose quality or MP3'); return; }
  downloadViaServer(url, fid, toMp3);
});
function showToast(text){
  if (!toast) return;
  toast.textContent = text;
  toast.hidden = false;
  setTimeout(() => { toast.hidden = true; }, 2500);
}
/* FAB: added floating info button + dialog — 2025-10-14 */
(function(){
  const fab = document.getElementById('fabInfo');
  const backdrop = document.getElementById('infoDialog');
  const panel = backdrop?.querySelector('.info-panel');
  const closeBtn = document.getElementById('infoClose');
  const contactBtn = document.getElementById('contactBtn');
  const toastEl = document.getElementById('toast');
  let lastFocus = null;
  let startY = 0;

  function showToast(text){
    if (!toastEl) return; 
    toastEl.textContent = text; 
    toastEl.hidden = false; 
    clearTimeout(window.__fab_toast_timer);
    window.__fab_toast_timer = setTimeout(()=>{toastEl.hidden = true;}, 2200);
  }

  function trapFocus(e){
    if (!backdrop || backdrop.hidden) return;
    const focusables = panel.querySelectorAll('button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.key === 'Tab'){
      if (e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
    } else if (e.key === 'Escape'){
      closeDialog();
    }
  }

  function openDialog(){
    if (!backdrop) return;
    lastFocus = document.activeElement;
    backdrop.hidden = false;
    backdrop.classList.add('open');
    fab?.setAttribute('aria-expanded','true');
    // RTL support: align row reverse when dir=rtl
    if (document.documentElement.dir === 'rtl') panel?.classList.add('rtl'); else panel?.classList.remove('rtl');
    // Focus inside
    setTimeout(()=>{ (panel.querySelector('#contactBtn') || panel)?.focus(); }, 10);
    document.addEventListener('keydown', trapFocus);
  }

  function closeDialog(){
    if (!backdrop) return;
    backdrop.classList.remove('open');
    backdrop.hidden = true;
    fab?.setAttribute('aria-expanded','false');
    document.removeEventListener('keydown', trapFocus);
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  fab?.addEventListener('click', () => {
    if (backdrop.hidden) openDialog(); else closeDialog();
  });
  closeBtn?.addEventListener('click', closeDialog);
  backdrop?.addEventListener('click', (e) => { if (e.target === backdrop) closeDialog(); });

  // Mobile swipe-down to close
  panel?.addEventListener('touchstart', (e)=>{ startY = e.touches[0].clientY; });
  panel?.addEventListener('touchmove', (e)=>{ const dy = e.touches[0].clientY - startY; if (dy > 50) closeDialog(); });

  contactBtn?.addEventListener('click', async ()=>{
    try{
      await navigator.clipboard.writeText('contact@example.com');
      showToast(document.documentElement.lang === 'ar' ? 'تم النسخ' : 'Copied');
    }catch{
      window.open('/pages/contact.html','_blank','noopener');
    }
  });
})();