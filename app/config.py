from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    trading_mode:str='paper'; live_trading_confirm:str=''; coinbase_api_key:str=''; coinbase_api_secret:str=''
    openai_api_key:str=''; openai_model:str='gpt-5.1'; symbol:str='BTC-USD'; binance_symbol:str='BTCUSDT'
    equity_usd:float=10000; risk_per_trade:float=.0025; max_daily_loss:float=.01; max_position_notional:float=.10
    max_spread_bps:float=20; min_signal_score:float=72; min_reward_risk:float=2; cooldown_seconds:int=300
    loop_seconds:int=5; ai_min_interval_seconds:int=30; database_path:str='alpha_trader.db'; host:str='127.0.0.1'; port:int=8000; log_level:str='INFO'
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
    @property
    def live_enabled(self): return self.trading_mode.lower()=='live' and self.live_trading_confirm=='YES_I_UNDERSTAND'
