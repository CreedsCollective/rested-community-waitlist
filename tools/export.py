#!/usr/bin/env python3
"""Export the rested homepage canvas (Main.dc.html) to a plain static site.

usage: export.py <Main.dc.html> <assets-src-dir> <out-dir>
"""
import os, re, shutil, sys, glob, urllib.parse

src, asset_dir, out = sys.argv[1:4]
html = open(src, encoding="utf-8").read()

# --- split helmet / body / script ---------------------------------------
helmet = re.search(r"<helmet>(.*?)</helmet>", html, re.S).group(1)
body = re.search(r"</helmet>(.*?)</x-dc>", html, re.S).group(1)
script = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', html, re.S).group(1)
title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)

def const(name):
    m = re.search(r"const %s = (\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*');" % name, script)
    return m.group(1) if m else "''"

# --- images ---------------------------------------------------------------
os.makedirs(os.path.join(out, "assets"), exist_ok=True)
def blob(m):
    bid = m.group(1)
    files = glob.glob(os.path.join(asset_dir, bid + ".*"))
    if not files:
        sys.exit("missing asset " + bid)
    name = os.path.basename(files[0])
    shutil.copyfile(files[0], os.path.join(out, "assets", name))
    return "assets/" + name
body = re.sub(r"/_blob/([0-9a-f]{32})", blob, body)
helmet = re.sub(r"/_blob/([0-9a-f]{32})", blob, helmet)

# --- template holes -> static markup -------------------------------------
reps = [
    ('onClick="{{toggleMenu}}"', 'id="menu-btn"'),
    ('aria-label="{{menuLabel}}"', 'aria-label="Open menu"'),
    ('aria-expanded="{{menuOpenStr}}"', 'aria-expanded="false" aria-controls="mobile-menu"'),
    ('onClick="{{closeMenu}}"', 'data-close-menu=""'),
    ('class="{{proofClass}} ', 'class="'),
    ('ref="{{proofRef}}"', 'data-proof=""'),
    ('onSubmit="{{wlSubmit}}"', 'novalidate=""'),
    ('color:{{wlMsgColor}};', ''),
    ('>{{wlMsg}}<', ' id="wl-msg"><'),
]
for a, b in reps:
    body = body.replace(a, b)
body = re.sub(r'\s(onInput|onChange)="\{\{\w+\}\}"', "", body)
body = re.sub(r'<sc-if value="\{\{menuOpen\}\}"[^>]*>', '<div id="mobile-menu" hidden="">', body)
body = body.replace("</sc-if>", "</div>")
# every waitlist button goes to the one signup form
body = body.replace('href="#v4-join"', 'href="#v4-signup"')
left = re.findall(r"\{\{[^}]*\}\}|<sc-|<dc-", body)
if left:
    sys.exit("unconverted template syntax: %s" % left[:5])

# --- icons (the editor's icon set isn't exportable; drawn here) ----------
ICONS = {
 "heart": '<path d="M12 21s-7.5-4.6-9.6-9.3C.9 8.3 3 4.5 6.6 4.5c2.2 0 3.7 1.3 5.4 3.4 1.7-2.1 3.2-3.4 5.4-3.4 3.6 0 5.7 3.8 4.2 7.2C19.5 16.4 12 21 12 21z"/>',
 "star": '<path d="M12 1.8l2.9 6.6 7.2.7-5.4 4.8 1.6 7.1L12 17.3 5.7 21l1.6-7.1L1.9 9.1l7.2-.7z"/>',
 "sparkle": '<path d="M12 1c.8 5.6 2.6 8.9 10 11-7.4 2.1-9.2 5.4-10 11-.8-5.6-2.6-8.9-10-11 7.4-2.1 9.2-5.4 10-11z"/>',
 "smiley": '<path fill-rule="evenodd" d="M12 1a11 11 0 110 22 11 11 0 010-22zm0 2.2a8.8 8.8 0 100 17.6 8.8 8.8 0 000-17.6zM8.6 8.2a1.5 1.5 0 110 3 1.5 1.5 0 010-3zm6.8 0a1.5 1.5 0 110 3 1.5 1.5 0 010-3zM6.9 13.6h2.3a3 3 0 005.6 0h2.3a5.2 5.2 0 01-10.2 0z"/>',
 "coffee": '<path fill-rule="evenodd" d="M3 8h14v6a6 6 0 01-6 6H9a6 6 0 01-6-6V8zm14 1.5h1.5a3 3 0 010 6H17v-2h1.5a1 1 0 000-2H17zM7 2.5c.8 1 .8 2 0 3M10.5 2.5c.8 1 .8 2 0 3M14 2.5c.8 1 .8 2 0 3M2 21.5h17v1.5H2z"/><path d="M6.2 1.8l1.2.9c-.9 1.2-.9 2.4 0 3.6l-1.2.9c-1.3-1.7-1.3-3.7 0-5.4zm3.5 0l1.2.9c-.9 1.2-.9 2.4 0 3.6l-1.2.9c-1.3-1.7-1.3-3.7 0-5.4zm3.5 0l1.2.9c-.9 1.2-.9 2.4 0 3.6l-1.2.9c-1.3-1.7-1.3-3.7 0-5.4z"/>',
 "crown": '<path d="M2 7l5 4.5L12 4l5 7.5L22 7l-2 11H4L2 7zm2 13h16v2H4z"/>',
 "envelope": '<path fill-rule="evenodd" d="M2 5h20v14H2V5zm2.4 2L12 12.6 19.6 7H4.4zM4 8.6V17h16V8.6l-8 5.9-8-5.9z"/>',
 "laptop": '<path fill-rule="evenodd" d="M4 4h16v11H4V4zm2 2v7h12V6H6zM1 17h22l-1.5 3h-19z"/>',
}
icon_css = [".ic{-webkit-mask-position:center;mask-position:center;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-size:contain;mask-size:contain}"]
# the editor's hand-drawn icon set, extracted from the canvas's HTML export into assets/icons/
icon_dir = os.path.join(out, "assets", "icons")
have = {os.path.splitext(f)[0] for f in os.listdir(icon_dir)} if os.path.isdir(icon_dir) else set()
for name in sorted(have):
    uri = "assets/icons/%s.png" % name
    icon_css.append('.ic-%s{-webkit-mask-image:url("%s");mask-image:url("%s")}' % (name, uri, uri))
used = set(re.findall(r'class="ic ic-([a-z-]+)', body))
missing = used - have
if missing:
    sys.exit("no icon drawn for: %s" % missing)

# --- behaviour (replaces the editor runtime) -----------------------------
js = """
(function () {
  var WL_ENDPOINT = '/api/waitlist';
  var WL_FORM_VERSION = %(ver)s;
  var WL_SMS_DISCLOSURE = %(sms)s;
  var WL_EMAIL_DISCLOSURE = %(email)s;

  // mobile menu
  var btn = document.getElementById('menu-btn');
  var menu = document.getElementById('mobile-menu');
  function setMenu(open) {
    if (!btn || !menu) return;
    menu.hidden = !open;
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  if (btn) btn.addEventListener('click', function () { setMenu(menu.hidden); });
  document.querySelectorAll('[data-close-menu]').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });

  // count-up stats
  var proof = document.querySelector('[data-proof]');
  function proofOn() { if (proof) proof.classList.add('v112-proof-on'); }
  if (!proof || !('IntersectionObserver' in window)) { proofOn(); }
  else {
    var io = new IntersectionObserver(function (es) {
      if (es.some(function (e) { return e.isIntersecting; })) { proofOn(); io.disconnect(); }
    }, { threshold: 0.35 });
    io.observe(proof);
  }

  // highlighter marks
  var marks = Array.prototype.slice.call(document.querySelectorAll('.v112-mk'));
  if (!('IntersectionObserver' in window)) { marks.forEach(function (m) { m.classList.add('v112-on'); }); }
  else {
    var mk = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { var m = e.target.querySelector('.v112-mk'); if (m) m.classList.add('v112-on'); mk.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    marks.forEach(function (m) { if (m.parentElement) mk.observe(m.parentElement); });
  }

  // waitlist buttons: scroll to the form and put the cursor in it
  document.querySelectorAll('a[href="#v4-signup"]').forEach(function (a) {
    a.addEventListener('click', function () {
      setTimeout(function () { var f = document.getElementById('wl-first'); if (f) f.focus({ preventScroll: true }); }, 450);
    });
  });

  // signup form -> /api/waitlist -> GoHighLevel
  var form = document.getElementById('v4-signup');
  var msg = document.getElementById('wl-msg');
  function say(text, isError) { if (!msg) return; msg.textContent = text; msg.style.color = isError ? '#9E1F4F' : '#1A1D24'; }
  function val(id) { var el = document.getElementById(id); return el ? el.value : ''; }
  var busy = false;
  if (form) form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (busy) return;
    var firstName = val('wl-first').trim();
    var lastName = val('wl-last').trim();
    var email = val('wl-email').trim();
    var digits = val('wl-phone').replace(/\\D/g, '');
    var smsBox = document.getElementById('wl-sms');
    var sms = !!(smsBox && smsBox.checked);
    var phoneOk = digits.length === 10 || (digits.length === 11 && digits.charAt(0) === '1');
    if (!firstName || !lastName) return say('Please add your first and last name.', true);
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) return say('Please enter a valid email address to join the waitlist.', true);
    if (sms && !phoneOk) return say('To get texts, enter a valid mobile number, or uncheck the text box to join by email only.', true);
    var payload = {
      first_name: firstName, last_name: lastName, email: email,
      email_permission: true, sms_consent: sms,
      phone: sms ? digits : null,
      submitted_at: new Date().toISOString(), source_page: location.href,
      form_version: WL_FORM_VERSION,
      sms_disclosure_shown: WL_SMS_DISCLOSURE, email_disclosure_shown: WL_EMAIL_DISCLOSURE
    };
    busy = true; say('Saving\\u2026', false);
    fetch(WL_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      .then(function (r) { if (!r.ok) throw new Error('save failed'); say('You\\u2019re on the list! Watch your inbox for what\\u2019s next.', false); form.reset(); })
      .catch(function () { say('Something went wrong saving your signup. Your details are still here, so please try again.', true); })
      .then(function () { busy = false; });
  });
})();
""" % {"ver": const("WL_FORM_VERSION"), "sms": const("WL_SMS_DISCLOSURE"), "email": const("WL_EMAIL_DISCLOSURE")}

page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="The rested is a faith-forward lifestyle and coaching community for women who refuse to put their lives on hold while they wait on God. Join the waitlist.">
<meta property="og:title" content="the rested">
<meta property="og:description" content="For women in the waiting. Join the waitlist.">
%(helmet)s
<style>%(icons)s
html{scroll-behavior:smooth}#v4-signup{scroll-margin-top:110px}
#mobile-menu[hidden]{display:none}
</style>
</head>
<body>
%(body)s
<script>%(js)s</script>
</body>
</html>
""" % {"title": title, "helmet": helmet.strip(), "icons": "\n".join(icon_css), "body": body.strip(), "js": js}

with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
    f.write(page)
print("wrote", os.path.join(out, "index.html"), len(page), "bytes;", len(os.listdir(os.path.join(out, "assets"))), "assets; icons:", sorted(used))
