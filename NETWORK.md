# Network Event v1 — Protocollo Rosso twin

Same contract as Supereroe `NETWORK.md`. Peer base URL (Render):
`https://protocollo-rosso-bot-2e9v.onrender.com` (no trailing slash in `NETWORK_PEERS`).

## Endpoints (this bot)

| Method | Path | Response |
|--------|------|----------|
| `GET` | `/health` or `/` | `200` plain `ok — protocollo-rosso-bot` |
| `GET` | `/network/v1/nodes` | `200` JSON `{ nodeId, peers, recent }` |
| `POST` | `/network/v1/event` | `204` (auth via `X-Network-Secret` if set) |

Also kept: `GET /sdq1/health`, `POST /ask` (local SDQ nucleo).

## Env

| Var | Meaning |
|-----|--------|
| `NODE_ID` | default `protocollo-rosso` |
| `NETWORK_SECRET` | shared with Supereroe; empty = open ingest (MVP) |
| `NETWORK_PEERS` | comma-separated peer bases (e.g. Supereroe Render URL) |

## Hard rules (locked)

- Network ingest **never** auto-alerts institutions.
- Anti-×3 / crisis-access / no-ID stay on Telegram paths only.
- Failed peer = `UNKNOWN` house, not silence — no invented certainty.
