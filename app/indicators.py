import numpy as np
def ema(v,p):
 a=np.asarray(v,float)
 if len(a)<p:return float(a[-1]) if len(a) else 0
 x=a[0]; al=2/(p+1)
 for z in a[1:]:x=al*z+(1-al)*x
 return float(x)
def rsi(v,p=14):
 a=np.asarray(v,float)
 if len(a)<p+1:return 50
 d=np.diff(a);g=np.maximum(d,0);l=np.maximum(-d,0);ag=g[:p].mean();al=l[:p].mean()
 for x,y in zip(g[p:],l[p:]):ag=(ag*(p-1)+x)/p;al=(al*(p-1)+y)/p
 return 100. if al==0 else float(100-100/(1+ag/al))
def atr_pct(h,l,c,p=14):
 h,l,c=map(lambda x:np.asarray(x,float),(h,l,c))
 if len(c)<p+1:return 0
 tr=np.maximum(h[1:]-l[1:],np.maximum(abs(h[1:]-c[:-1]),abs(l[1:]-c[:-1])))
 return float(100*tr[-p:].mean()/c[-1]) if c[-1] else 0
def zscore(v,w=30):
 a=np.asarray(v,float)
 if len(a)<5:return 0
 x=a[-min(w,len(a)):];s=x.std();return float((x[-1]-x.mean())/s) if s>1e-12 else 0
