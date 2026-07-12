# momenta-webhook-bot
Trading bot from TradingView to Delta Exchange

## Webhook authentication

The `/webhook` endpoint requires a shared secret. Requests without it are
rejected with `401` and never reach the trading logic.

Setup (both steps required — the bot refuses to start without step 1):

1. Set the `WEBHOOK_SECRET` environment variable on the server, e.g. a value
   from `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`.
2. Add the same value to every TradingView alert's JSON message:

   ```json
   {
     "signal": "LONG",
     "secret": "<your WEBHOOK_SECRET value>"
   }
   ```

TradingView cannot send custom HTTP headers, which is why the secret travels
in the payload. The bot strips it before logging, so it never appears in logs.
If you rotate the secret, update the environment variable and all TradingView
alerts together.
