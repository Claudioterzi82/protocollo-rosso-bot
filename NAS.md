# NAS vault — Claudionas / Synology (phase 2)

Offline vault for Protocollo Rosso (and later Supereroe sealed artifacts).
Crisis path on Telegram/Render must work with the NAS **offline**.

## Role

- Backup / evidence vault / reflection exports — **not** proof by itself.
- Bridge pattern MVP: agent on the LAN PC uploads via DSM File Station API.
- Credentials live in DSM + secure agent store only — never in this repo, never in channel chat.

## Epistemic labels (locked)

Every artifact (or sidecar `*.label.json`) carries one of:

| Label | Meaning |
|-------|--------|
| `VERIFICATO` | Independently checked |
| `IPOTESI` | Working hypothesis / raw drop default |
| `UNKNOWN` | Missing sync, unclear provenance, or open edge |

A backup is **not** proof. Failed sync = `UNKNOWN`, never invented silence.

## Hard rules (locked with Supereroe)

1. **Labels required** — `VERIFICATO` / `IPOTESI` / `UNKNOWN` on every artifact.
2. **NAS offline ≠ gate crisis** — SOS / `112` / `101` / no-ID help stay on the bot, independent of storage.
3. **No auto-alert from storage/sync** — anti-×3 remains only on user text (`ambulanza`\|`arma` ×3 in the same sentence).

## Suggested share layout

Under share `Backup_Raffello` (or equivalent):

```
protocollo-rosso/
  README.md
  inbox/             # raw drops — default IPOTESI
  sealed/            # report-sealed copies
  network-events/    # optional Network Event v1 JSON archives
  scacchiera/        # CASE / reflect exports
  labels/            # optional sidecars
  tmp/               # wipeable staging
```

## Network Event v1 (optional)

Peers may emit `vault.stored` / `vault.failed` with `caseId`, path hash, and label only — **no PII**, and **never** trigger institutional alert.

See also Supereroe `NETWORK.md` when present.

## Out of scope (MVP)

- Continuous camera / Blink ingest (phase 2+, explicit BE/EU opt-in only).
- Putting NAS passwords in Render env for public bots.
