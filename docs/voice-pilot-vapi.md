# Voice pilot: Vapi + Twilio setup

This guide wires **one pilot tenant** so missed phone calls become inquiries in the same dashboard inbox as website chat.

## What you need

- Vapi account with API access
- Twilio account with a German (or local) phone number
- Deployed backend with public HTTPS URL (e.g. `https://api.your-domain.com`)
- Pilot company slug from dashboard **Settings** (Chat-Referenz / slug)

## Architecture

```
Caller → Twilio number → Vapi (STT/TTS/LLM) → POST /api/v1/public/voice/webhook
                                                      ↓
                                              LeadCaptureService (channel=voice)
                                                      ↓
                                              Same inbox + email notifications
```

- **Deepgram Nova-3 Multilingual** — configured in Vapi dashboard (transcriber)
- **ElevenLabs Flash** — configured in Vapi dashboard (voice)
- **GPT-4o mini** — configured in Vapi for short spoken dialog; business logic runs on our backend

## 1. Twilio phone number

1. In Twilio Console, buy or port a number with voice capability.
2. In **Vapi → Phone Numbers → Import**, connect the Twilio number (Vapi guides you through credentials).
3. Note the E.164 number (e.g. `+493012345678`).

## 2. Vapi assistant (German, max ~3 minutes)

Create an assistant with:

| Setting | Value |
|---------|--------|
| **Language** | German (`de`) |
| **Max duration** | 3 minutes |
| **Transcriber** | Deepgram, model `nova-3`, multilingual |
| **Voice** | ElevenLabs Flash (German-friendly voice) |
| **Model** | OpenAI `gpt-4o-mini` |

### System prompt (example)

```
Du bist der telefonische Anfragen-Assistent für [Firmenname].
Sprich kurz und klar. Maximal 2 Sätze pro Antwort.

Ziele in dieser Reihenfolge:
1. Problem / gewünschte Leistung
2. Ort oder Postleitzahl
3. Dringlichkeit
4. Rückrufnummer bestätigen (falls abweichend von Anrufer-ID)

Am Anfang: Kurzer DSGVO-Hinweis, dass das Gespräch zur Bearbeitung der Anfrage verarbeitet wird.
Wenn alle Infos da sind: Bestätige Empfang und erwarteten Rückruf.

Rufe bei jeder Kundenaussage das Tool capture_inquiry auf — antworte dem Kunden nur mit dem Tool-Ergebnis.
```

### First message (DSGVO + Begrüßung)

```
Guten Tag. Dieses Gespräch wird zur Bearbeitung Ihrer Anfrage verarbeitet.
Wie kann ich Ihnen helfen?
```

### Metadata (required)

In assistant metadata (or phone-number metadata):

```json
{
  "company_slug": "YOUR-PILOT-SLUG"
}
```

Replace `YOUR-PILOT-SLUG` with the slug from dashboard settings.

## 3. Server URL (webhook)

Set the assistant **Server URL** to:

```
https://YOUR-API-HOST/api/v1/public/voice/webhook
```

Local dev (via ngrok or Vapi CLI forwarder):

```bash
ngrok http 8000
# Use https://xxxx.ngrok.io/api/v1/public/voice/webhook
```

Optional direct message endpoint (testing without tool-calls):

```
POST https://YOUR-API-HOST/api/v1/public/voice/message
```

```json
{
  "company_slug": "YOUR-PILOT-SLUG",
  "conversation_id": "test-call-1",
  "message": "Wasserrohrbruch in 10115 Berlin, dringend",
  "caller_phone": "+491701234567"
}
```

Response:

```json
{
  "reply": "Danke, wir haben Ihre Anfrage aufgenommen."
}
```

## 4. Tool: `capture_inquiry`

Add a **server** function tool on the assistant:

| Field | Value |
|-------|--------|
| **Name** | `capture_inquiry` |
| **Description** | Send the customer's latest spoken message to the business inbox backend |
| **Parameters** | `message` (string, required) — transcribed user utterance |
| **Server URL** | Same as assistant Server URL, or rely on `tool-calls` events to the Server URL |

When the user speaks, Vapi sends a `tool-calls` webhook. Our backend:

1. Resolves tenant from `call.metadata.company_slug`
2. Uses `call.id` as `conversation_id`
3. Seeds `call.customer.number` as caller phone when valid
4. Runs existing lead capture + notifications
5. Returns `{ "results": [{ "toolCallId": "...", "result": "<reply to speak>" }] }`

## 5. Assign phone number to assistant

In Vapi, link the Twilio number to this assistant. Place a test call.

## 6. Verify in dashboard

1. Log in as the pilot company.
2. Place a test call with problem + location + urgency.
3. Open **Anfragen** — inquiry should show source badge **Telefon** / **Phone**.
4. Confirm email notification respects **Benachrichtigen ab Dringlichkeit** settings.

## Troubleshooting

| Symptom | Check |
|---------|--------|
| 404 Company not found | `company_slug` in Vapi metadata matches dashboard slug |
| 422 on webhook | Tool name must be `capture_inquiry` (or `handle_user_message`) with `message` in arguments |
| No notification | Urgency below company minimum, or lead not yet contactable |
| Empty reply | Backend logs; OpenAI key on server for extraction |

## Security notes (pilot)

- Webhook is public (like widget). Rate-limited per IP.
- Do not put secrets in Vapi metadata.
- **Production:** set `VAPI_WEBHOOK_SECRET` on the backend and configure the same value in Vapi as a Custom Credential with header `X-Vapi-Secret` (Bearer prefix off). Requests with a wrong or missing secret receive HTTP 401.
- Leave `VAPI_WEBHOOK_SECRET` empty in local development to skip header verification.

## Pilot checklist

- [ ] Twilio number purchased and imported to Vapi
- [ ] Assistant: German prompt, 3 min max, DSGVO first message
- [ ] Deepgram Nova-3 + ElevenLabs Flash + gpt-4o-mini configured in Vapi
- [ ] `company_slug` in assistant metadata
- [ ] Server URL → `/api/v1/public/voice/webhook`
- [ ] `capture_inquiry` tool defined
- [ ] `VAPI_WEBHOOK_SECRET` set on server + matching `X-Vapi-Secret` in Vapi (production)
- [ ] Test call → inquiry in inbox with **Telefon** badge
- [ ] Notification email received (if urgency threshold met)
