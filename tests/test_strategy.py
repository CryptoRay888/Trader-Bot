from app.strategy import signal
def test_bullish():
 f={'price':100,'ema_fast':105,'ema_slow':100,'rsi':65,'atr_pct':1,'volume_z':1.5,'orderbook_imbalance':.25,'trade_imbalance':.25,'funding_rate':0,'oi_change_pct':2,'liquidation_bias':.2,'spread_bps':2,'trend':1,'momentum':.75}
 x=signal(f);assert x['side']=='buy';assert x['score']>=72;assert x['reward_risk']>=2
