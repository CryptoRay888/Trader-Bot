import asyncio,json,logging,time
from collections import deque
from datetime import datetime,timezone
import httpx,websockets
log=logging.getLogger(__name__)
class CoinbaseStream:
 def __init__(self,state):self.s=state;self.trades=deque(maxlen=5000);self.bids={};self.asks={}
 async def run(self):
  while True:
   try:
    async with websockets.connect('wss://advanced-trade-ws.coinbase.com',ping_interval=20,ping_timeout=10,max_size=8000000) as ws:
     for ch in ('ticker','level2','market_trades'):
      await ws.send(json.dumps({'type':'subscribe','product_ids':[self.s.symbol],'channel':ch}))
     async for raw in ws: await self.handle(raw)
   except Exception as e:log.warning('Coinbase reconnect: %s',e);await asyncio.sleep(2)
 async def handle(self,raw):
  m=json.loads(raw);ch=m.get('channel')
  for e in m.get('events',[]):
   if ch=='ticker':
    for t in e.get('tickers',[]):
     self.s.price=float(t.get('price',self.s.price));self.s.bid=float(t.get('best_bid',self.s.bid));self.s.ask=float(t.get('best_ask',self.s.ask))
     if self.s.bid and self.s.ask:self.s.spread_bps=(self.s.ask-self.s.bid)/((self.s.ask+self.s.bid)/2)*10000
   elif ch=='market_trades':
    for t in e.get('trades',[]):
     q=float(t.get('size',0));self.trades.append((time.time(),q if str(t.get('side','')).lower()=='buy' else -q))
    x=[q for ts,q in self.trades if time.time()-ts<=30];d=sum(abs(q) for q in x);self.s.trade_imbalance=sum(x)/d if d else 0
   elif ch=='l2_data':
    for u in e.get('updates',[]):
     b=self.bids if u.get('side')=='bid' else self.asks;p=float(u.get('price_level',0));q=float(u.get('new_quantity',0))
     if q:b[p]=q
     else:b.pop(p,None)
    bs=sum(q for _,q in sorted(self.bids.items(),reverse=True)[:20]);ask=sum(q for _,q in sorted(self.asks.items())[:20]);tot=bs+ask;self.s.orderbook_imbalance=(bs-ask)/tot if tot else 0
  self.s.last_exchange_update=datetime.now(timezone.utc)
class BinanceDerivatives:
 def __init__(self,state,symbol):self.s=state;self.symbol=symbol.lower()
 async def run(self):
  url='wss://fstream.binance.com/stream?streams='+f'{self.symbol}@markPrice/{self.symbol}@forceOrder'
  while True:
   try:
    async with websockets.connect(url,ping_interval=20,ping_timeout=10) as ws:
     async for raw in ws:
      d=json.loads(raw).get('data',{});e=d.get('e')
      if e=='markPriceUpdate':self.s.funding_rate=float(d.get('r',0))
      elif e=='forceOrder':
       o=d.get('o',{});q=float(o.get('q',0));self.s.liquidation_buy+=q if o.get('S')=='BUY' else 0;self.s.liquidation_sell+=q if o.get('S')=='SELL' else 0
      self.s.last_derivatives_update=datetime.now(timezone.utc)
   except Exception as e:log.warning('Binance reconnect: %s',e);await asyncio.sleep(2)
async def open_interest(state,symbol):
 async with httpx.AsyncClient(timeout=5) as c:r=await c.get('https://fapi.binance.com/fapi/v1/openInterest',params={'symbol':symbol});r.raise_for_status();n=float(r.json()['openInterest'])
 state.oi_change_pct=((n-state.open_interest)/state.open_interest*100) if state.open_interest else 0;state.open_interest=n
