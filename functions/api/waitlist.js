// Cloudflare Pages Function: POST /api/waitlist
// Checks the signup again, then forwards it to the GoHighLevel inbound webhook
// stored in the GHL_WEBHOOK_URL environment variable (Pages > Settings > Variables).

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

export async function onRequestPost({ request, env }) {
  let d;
  try { d = await request.json(); } catch { return json({ ok: false, error: 'bad json' }, 400); }

  const str = (v, max = 200) => (typeof v === 'string' ? v.trim().slice(0, max) : '');
  const first = str(d.first_name, 80);
  const last = str(d.last_name, 80);
  const email = str(d.email, 254).toLowerCase();
  const sms = d.sms_consent === true;
  const digits = String(d.phone || '').replace(/\D/g, '');

  if (!first || !last) return json({ ok: false, error: 'name required' }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ ok: false, error: 'bad email' }, 400);
  let phone = '';
  if (sms) {
    if (digits.length === 10) phone = '+1' + digits;
    else if (digits.length === 11 && digits[0] === '1') phone = '+' + digits;
    else return json({ ok: false, error: 'bad phone' }, 400);
  }

  if (!env.GHL_WEBHOOK_URL) return json({ ok: false, error: 'not configured' }, 503);

  const payload = {
    first_name: first,
    last_name: last,
    email,
    phone,
    sms_consent: sms,
    email_permission: true,
    tags: sms ? 'rested-waitlist, sms-optin' : 'rested-waitlist',
    source: 'waitlist.eviephillips.com',
    source_page: str(d.source_page, 500),
    submitted_at: new Date().toISOString(),
    form_version: str(d.form_version, 60),
    sms_disclosure_shown: sms ? str(d.sms_disclosure_shown, 1000) : '',
    email_disclosure_shown: str(d.email_disclosure_shown, 1000),
    ip: request.headers.get('cf-connecting-ip') || '',
    user_agent: str(request.headers.get('user-agent') || '', 300),
  };

  const r = await fetch(env.GHL_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!r.ok) return json({ ok: false, error: 'crm error' }, 502);
  return json({ ok: true });
}

export const onRequest = () => json({ ok: false, error: 'method not allowed' }, 405);
