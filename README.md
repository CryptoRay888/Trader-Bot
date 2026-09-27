# Alpha Trader

Multi-source live crypto trading system. Paper trading is the default.

## Stack
- Coinbase Advanced Trade: execution + real-time ticker/Level 2/trades
- Binance Futures: funding/mark price, open interest, liquidations
- Python async event loop
- deterministic multi-signal engine
- OpenAI Responses API structured-output second opinion
- hard risk gate
- SQLite audit log
- FastAPI health/state API

## Run
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main

Test: `pytest -q`

Live execution requires `TRADING_MODE=live`, `LIVE_TRADING_CONFIRM=YES_I_UNDERSTAND`, and Coinbase credentials. Never commit `.env`.

The AI cannot execute orders. It can only confirm/veto the deterministic signal. Risk code remains the final gate.

Official docs:
- https://docs.cdp.coinbase.com/advanced-trade/docs/ws-overview/
- https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams
- https://platform.openai.com/docs/quickstart
