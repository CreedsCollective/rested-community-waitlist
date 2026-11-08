# the rested — waitlist homepage

Live at https://waitlist.eviephillips.com (Cloudflare Pages, auto-deploys from `main`).

- `index.html` + `assets/` — the page, exported from the Claude design canvas "the rested | home launch".
- `functions/api/waitlist.js` — the form handler. It re-checks each signup and forwards it to GoHighLevel
  through the inbound-webhook URL in the Pages environment variable `GHL_WEBHOOK_URL`.

To change the page: edit the design in Claude, re-export, push to `main`.
