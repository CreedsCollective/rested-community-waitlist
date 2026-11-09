# the rested — waitlist homepage

Live at https://waitlist.eviephillips.com (Cloudflare Pages, auto-deploys from `main`).

- `index.html` + `assets/` — the page, exported from the Claude design canvas "the rested | home launch".
- `functions/api/waitlist.js` — the form handler. It re-checks each signup and forwards it to GoHighLevel
  through the inbound-webhook URL in the Pages environment variable `GHL_WEBHOOK_URL`.

To change the page: edit the design in Claude, re-export, push to `main`.

## How edits go live

This folder (`~/Projects/rested-community-waitlist`) is a clone of
github.com/CreedsCollective/rested-community-waitlist.

1. In a Claude session in this folder, say what to change ("change X on my waitlist").
2. Claude edits the files and shows Evie the change. Nothing is published yet.
3. Only after Evie says yes, Claude commits and pushes to `main`.
4. Cloudflare Pages sees the push and publishes it to https://waitlist.eviephillips.com, usually within a minute or two.

Rules: run `git pull` before editing. Never push without Evie's yes. Never print or change `GHL_WEBHOOK_URL`.
Signups live in GoHighLevel, not here. Keep this project separate from Evie's other projects and from the Viralish-Team organization.

## Re-exporting from the design canvas

`tools/export.py <Main.dc.html> <folder with the canvas's /_blob images> <this repo>` turns the canvas file into
`index.html` + `assets/`. The hand-drawn icons live in `assets/icons/` (taken from the canvas's HTML export).
