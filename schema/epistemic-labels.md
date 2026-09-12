# Epistemic labels — Protocollo Rosso P5/P6

Every answer, artifact, first-aid URL, and CASE house carries **one** of:

| Label | Meaning | Default use |
|-------|---------|-------------|
| `VERIFICATO` | Independently checked against a trusted source | Verified Brussels numbers; locked YouTube ids; sealed facts |
| `IPOTESI` | Open hypothesis — keep possibilities open | Raw drops; working drafts; parallel glosses |
| `UNKNOWN` | Missing evidence, unclear provenance, or open edge | Failed sync; no verified URL; CASE default house |

## House rule (locked)

**UNKNOWN is a house, not silence** / **UNKNOWN è una casa, non silenzio.**

- Hold both poles; do not force false certainty.
- UNKNOWN must **never** hide crisis buttons (SOS / `112` / `101`) or gate help behind ID/card.
- Prefer an explicit UNKNOWN + next safe step over inventing content (no fake URLs, no invented emergency numbers).

## Locale from body (locked — Claudio 2026-09-12)

Language is read from the **Telegram message body** (`from.language_code`) plus picker override — not only baked into a release build. If chrome stays EN while the body says `it` (or any other EU locale), that is a **runtime gap**, not a deploy footnote.

## Product copy — EU 24

Machine table: [`eu24-unknown-house.json`](./eu24-unknown-house.json).

| Tier | Locales |
|------|---------|
| `VERIFICATO` (core) | `en` `it` `fr` `de` `nl` `es` `pt` |
| `IPOTESI` (peer review welcome) | remaining EU official: `pl` `ro` `sv` `da` `fi` `el` `cs` `sk` `sl` `hr` `hu` `bg` `lt` `lv` `et` `mt` `ga` |

Missing or unreviewed locale → fall back to **EN** and treat UI chrome as **UNKNOWN**, never invent false certainty.

## Anti-regression

- Labels do not change anti-×3 (`ambulanza`\|`arma` ×3 same sentence → auto-alert only).
- Labels do not add ID/payment gates before help.
