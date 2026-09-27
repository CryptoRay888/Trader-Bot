from dataclasses import dataclass,field
from datetime import datetime,timezone

def now(): return datetime.now(timezone.utc)
@dataclass
class MarketState:
    symbol:str; price:float=0; bid:float=0; ask:float=0; spread_bps:float=9999; orderbook_imbalance:float=0; trade_imbalance:float=0; funding_rate:float=0; open_interest:float=0; oi_change_pct:float=0; liquidation_buy:float=0; liquidation_sell:float=0; last_exchange_update:datetime=field(default_factory=now); last_derivatives_update:datetime=field(default_factory=now); candles:list=field(default_factory=list)
    def fresh(self,max_age=5): return (now()-self.last_exchange_update).total_seconds()<=max_age
@dataclass
class Features:
    price:float; ema_fast:float; ema_slow:float; rsi:float; atr_pct:float; volume_z:float; orderbook_imbalance:float; trade_imbalance:float; funding_rate:float; oi_change_pct:float; liquidation_bias:float; spread_bps:float; trend:float; momentum:float
@dataclass
class Signal:
    side:str; score:float; entry:float; stop:float; target:float; reward_risk:float; reasons:list
@dataclass
class AIAnalysis:
    side:str='flat'; confidence:float=0; risk_flags:list=field(default_factory=list); thesis:str=''
