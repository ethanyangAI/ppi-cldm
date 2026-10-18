import numpy as np
def confusion(y,p):
 y=np.asarray(y,bool);p=np.asarray(p,bool)
 tp=int((y&p).sum());fp=int((~y&p).sum());tn=int((~y&~p).sum());fn=int((y&~p).sum())
 return dict(TP=tp,FP=fp,TN=tn,FN=fn,TPR=tp/(tp+fn) if tp+fn else None,FPR=fp/(fp+tn) if fp+tn else None,precision=tp/(tp+fp) if tp+fp else None)
def choose_threshold(y,s,max_fpr=.2):
 y=np.asarray(y,bool);s=np.asarray(s,float)
 if len(set(y.tolist()))<2:return float(np.max(s)+1),dict(reason="training has one class; reject all")
 choices=[]
 for t in sorted(set(s.tolist())|{float(np.max(s)+1)}):
  c=confusion(y,s>=t)
  if c["FPR"]<=max_fpr:choices.append((c["TPR"],-c["FPR"],t,c))
 best=max(choices,key=lambda x:x[:3]);return best[2],best[3]
def transform(train,test):
 train=np.asarray(train,float);test=np.asarray(test,float)
 return np.array([[(np.sum(train[:,j]<v)+.5*np.sum(train[:,j]==v))/len(train) for j,v in enumerate(row)] for row in test])
def auc(y,s):
 a=np.asarray(s)[np.asarray(y,bool)];b=np.asarray(s)[~np.asarray(y,bool)]
 return float(np.mean((a[:,None]>b[None,:])+.5*(a[:,None]==b[None,:]))) if len(a) and len(b) else None

