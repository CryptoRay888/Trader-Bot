from .indicators import atr_pct,ema,rsi,zscore
def features(s):
 c=s.candles;cl=[x[4] for x in c];hi=[x[2] for x in c];lo=[x[3] for x in c];vo=[x[5] for x in c];ef=ema(cl,12);es=ema(cl,26);rs=rsi(cl);ap=atr_pct(hi,lo,cl);vz=zscore(vo);trend=1 if ef>es else -1 if ef<es else 0;mom=max(min((rs-50)/20,1),-1) if rs>55 or rs<45 else 0;liq=s.liquidation_buy+s.liquidation_sell;lb=(s.liquidation_buy-s.liquidation_sell)/liq if liq else 0
 return dict(price=s.price,ema_fast=ef,ema_slow=es,rsi=rs,atr_pct=ap,volume_z=vz,orderbook_imbalance=s.orderbook_imbalance,trade_imbalance=s.trade_imbalance,funding_rate=s.funding_rate,oi_change_pct=s.oi_change_pct,liquidation_bias=lb,spread_bps=s.spread_bps,trend=trend,momentum=mom)
def signal(f):
 L=S=0;lr=[];sr=[]
 def add(v,side,txt):
  nonlocal L,S
  if side=='L':L+=v;lr.append(txt)
  else:S+=v;sr.append(txt)
 if f['trend']>0:add(18,'L','EMA trend bullish')
 elif f['trend']<0:add(18,'S','EMA trend bearish')
 if f['momentum']>.15:add(14,'L','momentum positive')
 elif f['momentum']<-.15:add(14,'S','momentum negative')
 if f['orderbook_imbalance']>.1:add(14,'L','bid imbalance')
 elif f['orderbook_imbalance']<-.1:add(14,'S','ask imbalance')
 if f['trade_imbalance']>.1:add(14,'L','aggressive buy flow')
 elif f['trade_imbalance']<-.1:add(14,'S','aggressive sell flow')
 if f['volume_z']>.75:add(10,'L' if f['momentum']>0 else 'S','volume expansion') if f['momentum'] else None
 if f['funding_rate']>.0003:add(5,'S','crowded positive funding')
 elif f['funding_rate']<-.0003:add(5,'L','negative funding')
 if f['oi_change_pct']>1 and f['momentum']>0:add(8,'L','OI rising with momentum')
 elif f['oi_change_pct']>1 and f['momentum']<0:add(8,'S','OI rising with momentum')
 if f['liquidation_bias']>.15:add(4,'L','buy liquidation pressure')
 elif f['liquidation_bias']<-.15:add(4,'S','sell liquidation pressure')
 side='buy' if L>S else 'sell' if S>L else 'flat';score=max(L,S);reasons=lr if side=='buy' else sr;v=max(f['atr_pct']/100,.001)
 stop=f['price']*(1-1.5*v) if side=='buy' else f['price']*(1+1.5*v) if side=='sell' else f['price'];target=f['price']*(1+3*v) if side=='buy' else f['price']*(1-3*v) if side=='sell' else f['price'];rr=abs(target-f['price'])/abs(f['price']-stop) if stop!=f['price'] else 0
 return {'side':side,'score':score,'entry':f['price'],'stop':stop,'target':target,'reward_risk':rr,'reasons':reasons}
