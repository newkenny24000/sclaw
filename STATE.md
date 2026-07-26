# Super Claw Bros marketing site — STATE

_Updated: 2026-07-26_

Durable "what's hot" for the SCB web surfaces. Sub-effort of the SCB venture (`../super-claw-bros/`); it carries no metric of its own. Venture status, ICP, and blockers live up the parent, not here.

## Status
**REBRAND IN PROGRESS (2026-07-25/26): Super Claw Bros → Buffalo Claw Co.** New site built at `bcc-site/` from Ken's Claude Design project and **deployed to the DO droplet** (68.183.19.160, CloudPanel static site `buffaloclawmachines.com`, site user `bccsite`, pw in droplet `/root/.bccsite_pw`). Serving 200 with real images; awaiting DNS to go public. The old `superclawbros.com` pages (repo root) stay live for now; retire after the new brand fully lands.

## What's hot
- **`bcc-site/`** — Buffalo Claw Co one-pager: hosting pitch + event rentals + contact form. Verified via `bcc-site/verify_site.py` (Playwright, desktop+mobile). Brand facts: phone 716-325-0758, email **contact@bfloclaw.com** (bfloclaw.com Workspace NOT yet set up), footer carries "Formerly Super Claw Bros."
- Old-brand pages still in repo root: `index.html`, `play.html`, `thanks.html`, `card.html`, `print.html`.

## Blockers / open decisions (all Ken)
1. **DNS:** point `buffaloclawmachines.com` A → 68.183.19.160 (direct or Cloudflare-proxied). Then issue LE cert on droplet: `clpctl lets-encrypt:install:certificate --domainName=buffaloclawmachines.com`.
2. **bfloclaw.com**: register/confirm + Workspace secondary domain + SPF/DKIM/DMARC so contact@bfloclaw.com receives. Site references it in 3 places.
3. **Form backend:** currently mailto-fallback to contact@bfloclaw.com; drop a Formspree ID into `FORMSPREE_ID` in `bcc-site/index.html` for in-page submit.
4. DBA filing "Buffalo Claw Co." under WNY Tech LLC (NY DOS assumed name) before contracts/cards print.

## Next action
- After DNS lands: LE cert, then live-domain Playwright pass + Lighthouse check. Then update outreach templates/one-pagers to the new brand (coordinate up through SCB parent).

## Recently done
- Added `/play` mobile HTML5 mini claw game (touch-drag aim, DROP, local best score), brand-matched, self-contained, no backend.
- Added phone + email to contact section and footer.
- Added pizzeria photo of kids at the machine below the hero.

## Housekeeping
- Stray `nul` file in repo root (Windows artifact) — safe to delete; do not commit.
- Brand facts flow DOWN from `../super-claw-bros/`. If they change at the source, update here; never invent new ones. Do not touch sibling dirs.
