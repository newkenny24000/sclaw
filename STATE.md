# Super Claw Bros marketing site — STATE

_Updated: 2026-09-15_

Durable "what's hot" for the SCB web surfaces. Sub-effort of the SCB venture (`../super-claw-bros/`); it carries no metric of its own. Venture status, ICP, and blockers live up the parent, not here.

## Status
**REBRAND SHIPPED (2026-07-26): Super Claw Bros → Buffalo Claw Co.** **https://buffaloclawmachines.com is LIVE** — built at `bcc-site/` from Ken's Claude Design project, deployed to the DO droplet (68.183.19.160, CloudPanel static site, site user `bccsite`, pw in droplet `/root/.bccsite_pw`), Cloudflare-proxied DNS, LE cert on origin. Contact form live via **Formspree `mpqjlpwb`** (verified end-to-end from the live domain). **bfloclaw.com** = short/email domain: Google Workspace verified (Gmail live), web 301-redirects every path to buffaloclawmachines.com (droplet vhost, own LE cert, site user `bfloclaw`). The old `superclawbros.com` pages (repo root) stay live for now; retire after the brand fully lands.

## What's hot
- **`bcc-site/`** — Buffalo Claw Co one-pager: hosting pitch + event rentals + contact form (name/business/email/phone + contact-method/time pills + free-text **Details**). Verify anytime: `python bcc-site/verify_site.py` (Playwright, desktop+mobile).
- **Lead notifier (2026-09-04)** -- `bcc-site/lead_notify/`: form submissions POST to `/api/lead` on the droplet (stdlib service, loopback 8580, systemd `bcc_lead`, nginx location in the vhost) which pushes name/phone/details to Ken's ntfy topic as a high-priority tap-to-call alert. Why: Formspree mail sat in Gmail's Updates tab; two leads in two weeks with zero marketing. Deploy/redeploy: `powershell -File bcc-site\lead_notify\deploy_lead.ps1` (Ken runs it; the orchestrator session cannot write to the droplet). Test submissions (email @example.com) log but never push. Log: `/home/bccsite/logs/lead.log`. CloudPanel vhost saves from the UI can drop the nginx location; rerun the deploy script to restore it.
- Brand facts: **Buffalo Claw Co.**, phone **716-472-1689** (changed from 716-325-0758 on 2026-09-15; site, signature, templates, old-brand pages all swept), email contact@bfloclaw.com. Site: SEO meta + OG + LocalBusiness schema (GBP-ready).
- Old-brand pages still in repo root: `index.html`, `play.html`, `thanks.html`, `card.html`, `print.html`.

## Blockers / open decisions (all Ken)
1. **DBA filing** "Buffalo Claw Co." under WNY Tech LLC (NY DOS assumed name) before contracts/cards print.
2. **contact@bfloclaw.com alias** in Google Admin + flip Formspree recipient to it (until then Formspree delivers to the account email).
3. **DKIM/DMARC** on bfloclaw.com if not done in the Workspace wizard; 2-week warm-up before outreach volume.
4. Decide retirement plan for superclawbros.com (redirect to the new brand once outreach materials are swapped).

## Next action
- ~~Update outreach templates~~ — DONE 2026-08-19 by the SCB parent (templates.py + templates.md + staged batches now Buffalo Claw Co. / contact@bfloclaw.com / buffaloclawmachines.com). One-pagers/cards still pending the DBA filing before print.
- GBP for Buffalo Claw Co once DBA is filed (zero inbound surface today; the rental searches are uncontested locally).

## Recently done
- 2026-08-24: dropped the "Formerly Super Claw Bros." footer line (rebrand has landed) and added a **Details** textarea to the contact form (posts as `details` to Formspree; also in the mailto fallback). Deployed to the droplet, verified live. Backup of the previous live file at `root@68.183.19.160:/root/index.html.bak-20260824`. Also fixed a flaky fixed-400ms wait in `verify_site.py` (now waits on the success card; the Formspree round-trip is slower than that).
- Added `/play` mobile HTML5 mini claw game (touch-drag aim, DROP, local best score), brand-matched, self-contained, no backend.
- Added phone + email to contact section and footer.
- Added pizzeria photo of kids at the machine below the hero.

## Housekeeping
- Stray `nul` file in repo root (Windows artifact) — safe to delete; do not commit.
- Brand facts flow DOWN from `../super-claw-bros/`. If they change at the source, update here; never invent new ones. Do not touch sibling dirs.
