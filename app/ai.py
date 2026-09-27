import json,logging
from .models import AIAnalysis
log=logging.getLogger(__name__)
class Analyst:
 def __init__(self,key,model):
  self.enabled=bool(key);self.model=model;self.client=None
  if self.enabled:
   from openai import OpenAI;self.client=OpenAI(api_key=key)
 def analyze(self,sig,f):
  if not self.enabled:return AIAnalysis(thesis='AI disabled')
  try:
   r=self.client.responses.create(model=self.model,input=[{'role':'system','content':'Act as a risk-aware second opinion. Do not invent data. You may veto a proposed quantitative trade but cannot create a trade. Return only the requested schema.'},{'role':'user','content':json.dumps({'signal':sig,'features':f})}],text={'format':{'type':'json_schema','name':'trade_analysis','strict':True,'schema':{'type':'object','properties':{'side':{'type':'string','enum':['buy','sell','flat']},'confidence':{'type':'number'},'risk_flags':{'type':'array','items':{'type':'string'}},'thesis':{'type':'string'}},'required':['side','confidence','risk_flags','thesis'],'additionalProperties':False}}})
   d=json.loads(r.output_text);return AIAnalysis(d['side'],max(0,min(1,float(d['confidence']))),d['risk_flags'],d['thesis'])
  except Exception as e:log.exception('AI failed');return AIAnalysis(risk_flags=['AI unavailable'],thesis=str(e))
