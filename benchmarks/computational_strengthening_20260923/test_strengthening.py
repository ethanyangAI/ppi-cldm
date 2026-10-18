import numpy as np
from calibration_math import *
def test_threshold_excludes_test_labels():
 t,c=choose_threshold([0,0,1,1],[.1,.4,.5,.9]);assert t==.5 and c["FPR"]==0
def test_reject_all_is_available():
 t,c=choose_threshold([0,1],[.9,.1],0);assert t>.9 and c["TPR"]==0
def test_ties_not_broken_using_labels():
 assert auc([1,0],[.5,.5])==.5
def test_train_only_percentile():
 tr=np.array([[0,1],[1,2]]);te=np.array([[100,-10]])
 assert transform(tr,te).tolist()==[[1,0]]
def test_missing_positive_denominator():
 assert confusion([0,0],[0,1])["TPR"] is None
def test_zero_predictions_precision_missing():
 assert confusion([1,0],[0,0])["precision"] is None

