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
2. Nuovo cron: ogni **10 minuti**. Non ogni ora: a 60 minuti il servizio ha
   gia' dormito per 45.
3. URL: `https://IL-TUO-SERVIZIO.onrender.com/health` ← **non `/`**
4. Salva.

Quel ping tiene acceso il processo.

**Perche' `/health` e non `/`.** Il server HTTP gira in un thread daemon, il
polling Telegram sul thread principale: sono indipendenti. Se il polling muore
— 409 Conflict, rete, eccezione non ripresa — il thread HTTP continua a
rispondere `ok`. Una sonda puntata su `/` direbbe «vivo» proprio nel caso in
cui il bot e' sordo, e il keep-alive terrebbe sveglio un processo che non
riceve niente.

`/health` guarda lo stato reale dell'updater e risponde **503** quando il
polling non gira (con una finestra di grazia all'avvio, `GRAZIA_AVVIO`, 90s di
default). E' la sonda da puntare anche nell'Health Check Path di Render: cosi'
il riavvio parte da solo, senza aspettare che qualcuno se ne accorga.

## 3. Prova

https://t.me/ProtocolloRossoBot → `/ping`

Se risponde «Qui», è vivo anche a Grok chiuso.
