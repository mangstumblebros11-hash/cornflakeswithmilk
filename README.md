# Skibiditopia Poller

Der Dienst erzeugt dauerhaft Fake-Drops für **OG**, **Highlights** und
**Peaklights** und sendet sie als Discord-Embeds an Webhooks.

## Lokal starten

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DISCORD_WEBHOOK_URL="deine-webhook-url"
python app.py
```

Der Health-Check ist unter `/healthz` erreichbar.

## Railway einrichten

1. Dieses Verzeichnis als GitHub-Repository anlegen.
2. In Railway ein neues Projekt aus dem GitHub-Repository erstellen.
3. Als Variable `DISCORD_WEBHOOK_URL` die Discord-Webhook-URL hinterlegen.
4. Railway erkennt das `Dockerfile` automatisch und startet den Dienst.
5. Optional können `DISCORD_WEBHOOK_OG`, `DISCORD_WEBHOOK_HIGHLIGHT` und
   `DISCORD_WEBHOOK_PEAKLIGHT` gesetzt werden, wenn jede Kategorie in einen
   anderen Discord-Kanal soll.

Die Webhook-URL gehört ausschließlich in Railway Variables oder eine lokale
`.env`-Datei und niemals in GitHub.

## Verhalten

- OG: alle 20–60 Minuten
- Highlights: alle 3–8 Sekunden
- Peaklights: alle 30–90 Sekunden
- OG-Drops erwähnen standardmäßig `@everyone`; mit
  `DISCORD_OG_MENTION=` kann die Erwähnung abgeschaltet werden.

Der Dienst ist ein Generator wie die bereitgestellte Vorlage. Er ruft keine
Live-Spiel-API ab.