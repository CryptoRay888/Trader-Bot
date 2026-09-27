import asyncio,logging,time
from fastapi import FastAPI
import uvicorn
from coinbase.rest import RESTClient
from .config import Settings
from .models import MarketState
from .market import CoinbaseStream,BinanceDerivatives,open_interest
from .strategy import features,signal
from .ai import Analyst
from .risk import Risk
from .execution import Paper,Coinbase
s=Settings();logging.basicConfig(level=getattr(logging,s.log_level.upper(),20),format='%(asctime)s %(levelname)s %(message)s');log=logging.getLogger('alpha')
state=MarketState(s.symbol);ai=Analyst(s.openai_api_key,s.openai_model);risk=Risk(s);paper=Paper();executor=Coinbase(s.coinbase_api_key,s.coinbase_api_secret,s.symbol) if s.live_enabled else paper
app=FastAPI(title='Alpha Trader');latest={'status':'starting','signal':None,'ai':None,'risk':None,'execution':None};last_ai=0;last_ai_result=None
@app.get('/health')
def health():return {'status':latest['status'],'mode':'live' if s.live_enabled else 'paper','symbol':s.symbol,'price':state.price,'fresh':state.fresh()}
@app.get('/state')
def state_api():return {'latest':latest,'market':state.__dict__,'paper_position':paper.position}
async def candles():
 c=RESTClient()
 while True:
  try:
   e=int(time.time());r=c.get_candles(product_id=s.symbol,start=str(e-3600),end=str(e),granularity='ONE_MINUTE',limit=300);rows=getattr(r,'candles',[]);state.candles=sorted([[int(x.start),float(x.open),float(x.high),float(x.low),float(x.close),float(x.volume)] for x in rows])[-300:]
  except Exception as ex:log.warning('candles: %s',ex)
  await asyncio.sleep(30)
async def oi():
 while True:
  try:await open_interest(state,s.binance_symbol)
  except Exception as ex:log.warning('OI: %s',ex)
  await asyncio.sleep(10)
async def decisions():
 global last_ai,last_ai_result
 while True:
  try:
   if not state.fresh() or len(state.candles)<40:latest['status']='warming_or_stale';await asyncio.sleep(s.loop_seconds);continue
   f=features(state);sig=signal(f)
   if time.time()-last_ai>=s.ai_min_interval_seconds:last_ai_result=ai.analyze(sig,f);last_ai=time.time()
   ok,reason,qty=risk.check(sig,last_ai_result,f);latest['signal']=sig;latest['ai']=last_ai_result.__dict__ if last_ai_result else None;latest['risk']={'approved':ok,'reason':reason,'quantity':qty}
   if ok:
    current=paper.position
    same=(sig['side']=='buy' and current>0) or (sig['side']=='sell' and current<0)
    if not same:latest['execution']=executor.order(sig['side'],qty,sig['entry']);latest['status']='trade_executed'
    else:latest['status']='position_held'
   else:latest['status']='monitoring'
  except Exception:log.exception('decision failure');latest['status']='error'
  await asyncio.sleep(s.loop_seconds)
@app.on_event('startup')
async def startup():
 for worker in (CoinbaseStream(state).run(),BinanceDerivatives(state,s.binance_symbol).run(),candles(),oi(),decisions()):asyncio.create_task(worker)
if __name__=='__main__':uvicorn.run(app,host=s.host,port=s.port)
