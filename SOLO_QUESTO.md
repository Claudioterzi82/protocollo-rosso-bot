# Hosting gratis — perché Grok si spegne

Grok non può tenere il bot acceso. Serve un sito gratis che ascolti Telegram.

Il piano **Render Free** è un servizio *web*. Il `Procfile` deve essere `web:`, non `worker:` (i worker su Render si pagano e sul free non partono).

## 1. Render (gratis)

1. Apri https://render.com e entra con GitHub (`raffaellocantatelli`).
2. **New + → Web Service** (non Background Worker).
3. Collega il repo `protocollo-rosso-bot`.
4. Impostazioni:
   - Build: `pip install -r requirements.txt`
   - Start: `python -m bot.main`
   - Instance: **Free**
5. Environment:
   - `TELEGRAM_BOT_TOKEN` = il token di BotFather (solo lì, non in chat)
   - `PYTHONUNBUFFERED` = `1`
6. Deploy. Copia l’URL tipo `https://protocollo-rosso-bot.onrender.com`.
   Nel browser deve comparire `ok`.

## 2. Non farlo addormentare (gratis)

Render free si spegne dopo ~15 minuti senza visite.

1. Apri https://cron-job.org (account gratis).
2. Nuovo cron: ogni **10 minuti**.
3. URL: `https://IL-TUO-SERVIZIO.onrender.com/`
4. Salva.

Quel ping tiene acceso il processo. Telegram vede il bot sempre.

## 3. Prova

https://t.me/ProtocolloRossoBot → `/ping`

Se risponde «Qui», è vivo anche a Grok chiuso.
