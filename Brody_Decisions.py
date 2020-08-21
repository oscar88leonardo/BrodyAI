import pandas as pd
import numpy as np
import copy


class TradeDecisions:
    
    ################# Initialize object ##################################
    def __init__(self, Alpha_dic, AT_risks, Fees_dict,tp):
        self.Alpha_dic=Alpha_dic
        self.AT_risks=AT_risks
        self.Fees_dict=Fees_dict
        self.tp=tp
    
    ######################### filter by risks    
    def filter_by_risks(self):
        #Alpha_filt=self.Alpha_dic
        Alpha_filt=copy.deepcopy(self.Alpha_dic)
        for risk_type in self.AT_risks.columns:
           logic_condition=(self.AT_risks[risk_type]) > (self.AT_risks[risk_type].mean())
           for alpha_keys in self.Alpha_dic.keys():
               Alpha_filt[alpha_keys][risk_type]=np.multiply(self.Alpha_dic[alpha_keys][self.tp], np.where(logic_condition, 1.0, 0.0).astype(float))
               Alpha_filt[alpha_keys]['p'+risk_type]=Alpha_filt[alpha_keys][risk_type].diff() 

        return Alpha_filt
    
    
    ####################### get trading dictionary
    def get_trading_dic(self,Alpha_filt, tradePair_dic, risk_type,alpha_keys):
        # trade directory for specific risk_type
        Trade_dic={
                    'buy':[],'buy_time':[],'bix_time':[],
                    'sell':[],'sell_time':[],'six_time':[],
                    }

        close_prices=tradePair_dic[self.tp].close
        dates_tp=tradePair_dic[self.tp].datetime
        pos=Alpha_filt[alpha_keys].index
        
        lsell_condition = Alpha_filt[alpha_keys]['p'+risk_type] == 1.0
        Trade_dic['sell']=close_prices[lsell_condition].values
        Trade_dic['sell_time']=dates_tp[lsell_condition].values
        Trade_dic['six_time']=pos[lsell_condition].values
    
        lbuy_condition = Alpha_filt[alpha_keys]['p'+risk_type] == -1.0  
        Trade_dic['buy']=close_prices[lbuy_condition].values
        Trade_dic['buy_time']=dates_tp[lbuy_condition].values
        Trade_dic['bix_time']=pos[lbuy_condition].values
                        
        
        return Trade_dic
    
    ###################### get trading cycles
    def get_trading_cycles(self,Trade_dic,alpha_keys,investment):
        #Trade_dic : trade directory for specific risky_type
        # alpha_keys : string with the name of a single alpha model in Alpha_dic
        # initialize Cycles DataFrame
        cycles_data={
            'type':[],'buy':[],'buy_time':[],'bix_time':[],
            'sell':[],'sell_time':[],'six_time':[],
            'total_buy':[],'total_sell':[],'profit':[]
        }
        cycles_df=pd.DataFrame(cycles_data)
        pending_df=copy.deepcopy(cycles_df)
        
        #alpha_keys='SMA_'+self.tp
        LT= np.min([len(Trade_dic['buy']), len(Trade_dic['sell'])])
        if LT <= 2:
            normal_case=False
        else:
            normal_case=True
            LT=LT-1
        
        
        for i in range(LT):
            # determine  position
            cycle_temp={
                'type':[ '' ],
                'buy':[ Trade_dic['buy'][i] ],'buy_time':[ Trade_dic['buy_time'][i] ],
                'bix_time':[ Trade_dic['bix_time'][i] ],
                'sell':[ Trade_dic['sell'][i] ],'sell_time':[ Trade_dic['sell_time'][i] ],
                'six_time':[ Trade_dic['six_time'][i] ],
                'total_buy':[0.0000],'total_sell':[0.0000],'profit':[0.0000]
            }
            
            if normal_case:
                second_cycle_short={
                                'type':[ 'short' ],
                                'buy':[ Trade_dic['buy'][i+1] ],'buy_time':[ Trade_dic['buy_time'][i+1] ],
                                'bix_time':[ Trade_dic['bix_time'][i+1] ],
                                'sell':[ Trade_dic['sell'][i] ],'sell_time':[ Trade_dic['sell_time'][i] ],
                                'six_time':[ Trade_dic['six_time'][i] ],
                                'total_buy':[0.0000],'total_sell':[0.0000],'profit':[0.0000]
                             }
                second_cycle_sdf=pd.DataFrame(second_cycle_short)
            
                second_cycle_long={
                                'type':[ 'long' ],
                                'buy':[ Trade_dic['buy'][i] ],'buy_time':[ Trade_dic['buy_time'][i] ],
                                'bix_time':[ Trade_dic['bix_time'][i] ],
                                'sell':[ Trade_dic['sell'][i+1] ],'sell_time':[ Trade_dic['sell_time'][i+1] ],
                                'six_time':[ Trade_dic['six_time'][i+1] ],
                                'total_buy':[0.0000],'total_sell':[0.0000],'profit':[0.0000]
                             }
                second_cycle_ldf=pd.DataFrame(second_cycle_long)
        
            # Determine profits
            #taker_fee=0.001 # market orders
            maker_fee=0.001 # limit orders
            
            # Define type of 1st trade (short or long)
            if cycle_temp['bix_time'][0] < cycle_temp['six_time'][0]:                
                cycle_temp['type'][0]='long'
                #####################################################
                cycle_temp_df=pd.DataFrame(cycle_temp)
                if normal_case:
                    cycle_temp_df=cycle_temp_df.append(second_cycle_sdf, ignore_index=True) 
                    # pending_df.loc['sell']=cycle_temp['sell'][0]
                    # check profitable trades in penidng dataframe
                    #pending_entry=pending_df.loc[((cycle_temp['sell']-pending_df['buy']>0) and (cycle_temp['six_time'] < pending_df['bix_time']))] 
            else:
                cycle_temp['type'][0]='short'
                cycle_temp_df=pd.DataFrame(cycle_temp)
                if normal_case:
                    cycle_temp_df=cycle_temp_df.append(second_cycle_ldf, ignore_index=True) 
                    # replace buy/sell value to test profit against the newly reported values
                    # long , replace sell value and test if a profitable trade can be closed
                    # short, replace buy 
                    # pending_df.loc['buy']=cycle_temp['buy'][0]
                    # check profitable trades in pending dataframe
                    #pending_entry=pending_df.loc[((pending_df['sell']-cycle_temp['buy']>0) and (pending_df['six_time'] < cycle_temp['bix_time']))]             
            
            cycle_temp_df.loc[0,'total_buy']=investment/cycle_temp_df.loc[0,'buy']-(investment/cycle_temp_df.loc[0,'buy'])*maker_fee
            cycle_temp_df.loc[0,'total_sell']=cycle_temp_df.loc[0,'total_buy']*cycle_temp_df.loc[0,'sell']-(cycle_temp_df.loc[0,'total_buy']*cycle_temp_df.loc[0,'sell'])*maker_fee
            cycle_temp_df.loc[0,'profit']=cycle_temp_df.loc[0,'total_sell']-investment
                
            
            
            # if it is a profitable trade, add temporal dataframe to cycles dataframe, otherwise add to pending book dataframe
            if  cycle_temp_df.loc[0,'profit'] > 0:
                #profitable trade, append main dataframe
                cycles_df=cycles_df.append(cycle_temp_df, ignore_index=True)
            else:
                # Not profitable trade, add to pending dataframe
                pending_df=pending_df.append(cycle_temp_df.iloc[[0]], ignore_index=True)
            
            # compute pending profits
            #pending_df.loc[:,'total_buy']=investment/pending_df.loc[:,'buy']-(investment/pending_df.loc[:,'buy'])*maker_fee
            #pending_df.loc[:,'total_sell']=pending_df.loc[:,'total_buy']*pending_df.loc[:,'sell']-(pending_df.loc[:,'total_buy']*pending_df.loc[:,'sell'])*maker_fee
            #pending_df.loc[:,'profit']=pending_df.loc[:,'total_sell']-investment   
            #cycles_df.append( pending_df.loc[pending_df['profit'] > 0], ignore_index=True)
            
            
        return cycles_df, pending_df
