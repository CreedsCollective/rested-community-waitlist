// Cloudflare Pages Function: POST /api/waitlist
// Checks the signup again, then forwards it to the GoHighLevel inbound webhook
// stored in the GHL_WEBHOOK_URL environment variable (Pages > Settings > Variables).
// The URL is never in this repo.

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

const FRIENDLY_ERROR = 'Sorry, we couldn’t save your spot just now. Please try again in a minute.';

export async function onRequestPost({ request, env }) {
  let d;
  try { d = await request.json(); } catch { return json({ ok: false, error: 'Please try again.' }, 400); }
  if (!d || typeof d !== 'object') return json({ ok: false, error: 'Please try again.' }, 400);

  // Honeypot: a hidden field people never see. Bots fill it in; pretend it worked and drop it.
  if (typeof d.website === 'string' && d.website.trim() !== '') return json({ ok: true });

  const str = (v, max = 200) => (typeof v === 'string' ? v.trim().slice(0, max) : '');
  const first = str(d.first_name, 80);
  const last = str(d.last_name, 80);
  const email = str(d.email, 254).toLowerCase();
  const sms = d.sms_consent === true;
  const digits = String(d.phone || '').replace(/\D/g, '');

  if (!first || !last) return json({ ok: false, error: 'Please add your first and last name.' }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ ok: false, error: 'Please enter a valid email address.' }, 400);

  // Phone is only sent with SMS consent: 10 digits, or 11 starting with the US country code 1.
  let phone = null;
  if (sms) {
    if (digits.length === 10) phone = '+1' + digits;
    else if (digits.length === 11 && digits[0] === '1') phone = '+' + digits;
    else return json({ ok: false, error: 'Please enter a valid 10-digit mobile number, or uncheck the text box.' }, 400);
  }

  if (!env.GHL_WEBHOOK_URL) return json({ ok: false, error: FRIENDLY_ERROR }, 503);

  // Exactly the keys the GoHighLevel workflow is mapped to.
  const payload = {
    first_name: first,
    last_name: last,
    email,
    phone,
    email_permission: true,
    sms_consent: sms,
    submitted_at: new Date().toISOString(),
    source_page: str(d.source_page, 500),
    form_version: str(d.form_version, 60),
    sms_disclosure: sms ? str(d.sms_disclosure, 1000) || null : null,
    email_disclosure: str(d.email_disclosure, 1000) || null,
  };

  try {
    const r = await fetch(env.GHL_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!r.ok) return json({ ok: false, error: FRIENDLY_ERROR }, 502);
  } catch {
    return json({ ok: false, error: FRIENDLY_ERROR }, 502);
  }
  return json({ ok: true });
}

export const onRequest = () => json({ ok: false, error: 'method not allowed' }, 405);
