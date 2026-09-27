import uuid
class Paper:
 def __init__(self):self.position=0
 def order(self,side,qty,price):self.position+=qty if side=='buy' else -qty;return {'accepted':True,'order_id':str(uuid.uuid4()),'side':side,'quantity':qty,'price':price,'mode':'paper'}
class Coinbase:
 def __init__(self,key,secret,product):
  from coinbase.rest import RESTClient;self.c=RESTClient(api_key=key,api_secret=secret);self.product=product
 def order(self,side,qty,price):
  cid=str(uuid.uuid4())
  r=self.c.market_order_buy(client_order_id=cid,product_id=self.product,base_size=f'{qty:.8f}') if side=='buy' else self.c.market_order_sell(client_order_id=cid,product_id=self.product,base_size=f'{qty:.8f}')
  d=r.to_dict() if hasattr(r,'to_dict') else dict(r);oid=str(d.get('success_response',{}).get('order_id',cid));return {'accepted':True,'order_id':oid,'side':side,'quantity':qty,'price':price,'mode':'live'}
