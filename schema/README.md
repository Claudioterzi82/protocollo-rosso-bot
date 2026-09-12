# Protocollo Rosso schema — P5/P6 + CASE v1

Canonical epistemic labels and the 15 CASE houses (scacchiera) for Supereroe import **after** this lands on `main`.

## Files

| File | Role |
|------|------|
| `epistemic-labels.md` | P5/P6 contract + body-locale rule |
| `eu24-unknown-house.json` | «UNKNOWN is a house» for 24 EU official languages |
| `case.schema.json` | JSON Schema for CASE houses |
| `case.v1.json` | Canonical 15 houses (IT poles + IT/EN notes) |

## Import rule (locked)

- **Do not** import into Supereroe until this schema is on `protocollo-rosso-bot` `main`.
- Supereroe should stop duplicating CASE in `scacchiera.ts` only after a deliberate import PR.
- Aligns with `NAS.md` vault labels (same three strings).
- Locale from Telegram **body** + picker; EU24 phrases from `eu24-unknown-house.json`.

## Crisis / anti-×3 (locked)

- Schema is **documentation + data** only — no Telegram escalation changes.
- `UNKNOWN` is a house, not silence; it must **not** hide SOS / `112` / no-ID help.
- No auto-alert from schema or NAS sync; anti-×3 stays user-text only (`ambulanza`\|`arma` ×3 same sentence).

## Provenance

CASE poles + English glosses: `VERIFICATO` against Supereroe `src/lib/core/scacchiera.ts` (canonical order). Italian notes: `IPOTESI` parallel glosses (same meaning as EN). Direction cycle matches Supereroe `DIRECTIONS`. EU24 house phrases: core 7 `VERIFICATO`, others `IPOTESI` pending peer review.
