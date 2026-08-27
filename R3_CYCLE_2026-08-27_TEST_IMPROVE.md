# Ciclo test + miglioramento — 2026-08-27

Oggetto: https://t.me/Rossoroseorossobot (repo Hub: raffaellocantatelli/protocollo-rosso-bot)
Strato: FATTO dove c'è test locale. Bot live: NON VERIFICATO (nessun token in questo ambiente).

## Test eseguiti (locale, sandbox)

- pytest prima: 8 passed, 1 failed (`test_handlers_export` per dipendenza telegram assente nell'ambiente nudo).
- pytest dopo: 14 passed.

## Miglioramenti (v1.1.0) — testi del Protocollo non sostituiti

- P6 dopo `/tieni_aperto` (o `/salta`).
- Tastiere per Santuario e veli.
- `/annulla` corretto fuori dal Santuario.
- `/stato`, `/registro`, `/ping` allineati.
- Escape Markdown sul testo utente.
- `/strati` senza tabella Markdown.

Questo ciclo non conferma la tesi del «già».
