from entropy import perm_entropy, sample_entropy
import pandas as pd

class RiskModels:
    
    def __init__(self, dictionary):
        self.dictionary=dictionary
        
    def RiskCalculations(self,wl,tradepair):
        # initialize dataframe
        risks=pd.DataFrame()
        risks['CoefVar']=0
        risks['PE']=0
        risks['SaE']=0
        risks['VAR']=0
        # calculate Coefficient of Variations
        desv=self.dictionary[tradepair].close.rolling(window=wl, min_periods=1, center=False).std()
        mean=self.dictionary[tradepair].close.rolling(window=wl, min_periods=1, center=False).mean()
        risks['CoefVar']=desv/mean
        
        # calculate Value At Risk
        risks['VAR']=self.dictionary[tradepair].close.rolling(window=wl, min_periods=1, center=False).min()
        
        # calculate Entropy (Permutation Entropy)
        risks['PE']=perm_entropy(self.dictionary[tradepair].close, order=3, normalize=True)
        risks['SaE']=sample_entropy(self.dictionary[tradepair].close, order=2, metric='chebyshev')
    
        return risks

