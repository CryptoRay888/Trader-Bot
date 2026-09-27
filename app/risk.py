import time
class Risk:
 def __init__(self,c):self.c=c;self.daily_pnl=0;self.cooldown=0
 def check(self,sig,ai,f):
  if sig['side']=='flat':return False,'flat',0
  if sig['score']<self.c.min_signal_score:return False,'score',0
  if sig['reward_risk']<self.c.min_reward_risk:return False,'reward/risk',0
  if f['spread_bps']>self.c.max_spread_bps:return False,'spread',0
  if self.daily_pnl<=-(self.c.equity_usd*self.c.max_daily_loss):return False,'daily loss',0
  if time.time()<self.cooldown:return False,'cooldown',0
  if ai.side not in ('flat',sig['side']):return False,'AI veto',0
  if ai.confidence and ai.confidence<.55:return False,'AI confidence',0
  stop=abs(sig['entry']-sig['stop']);qty=min((self.c.equity_usd*self.c.risk_per_trade)/stop,(self.c.equity_usd*self.c.max_position_notional)/sig['entry']) if stop else 0
  return (True,'approved',qty) if qty>0 else (False,'size',0)
