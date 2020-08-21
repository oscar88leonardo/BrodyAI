# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from finta import TA 
import pandas as pd
import numpy as np

# +
# Signal generators-Technical indicator:

class AlphaModels:
    
    def __init__(self, dictionary):
        self.dictionary=dictionary

    ################## Plot signals in the object
    def PlotSignals(self,exchange,tradepair,alpha_str,signals,risk):
        # for no risk -> risk=tradepair
        # Show Graph:
        # Signals and cryptocoin closing
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax2 = ax1.twinx()
        rspine = ax2.spines['right']
        rspine.set_position(('axes', 1.15))
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)

        fig.subplots_adjust(right=0.7)
        self.dictionary[tradepair].close.plot(ax=ax1, style='b-',title='{}:Data from {}. risk:{}'.format(alpha_str,exchange,risk))
        signals[risk].plot(ax=ax1, style='r*', secondary_y=True)  
        # plot position according to risk
        if risk == tradepair:
            signals['position'].plot(ax=ax2, style='g--')
        elif risk == 'CoefVar':
            signals['pCoefVar'].plot(ax=ax2, style='g--')
        elif risk == 'PE':
            signals['pPE'].plot(ax=ax2, style='g--')
        elif risk == 'SaE':
            signals['pSaE'].plot(ax=ax2, style='g--')
        elif risk == 'VAR':
            signals['pVAR'].plot(ax=ax2, style='g--')
            
        # legend
        ax2.legend([ax1.get_lines()[0],
                    ax1.right_ax.get_lines()[0],
                    ax2.get_lines()[0]],
                   [tradepair, 'signal', 'position'])
    
    def PlotBBZ(self,exchange,tradepair,alpha_str,signals,risk):
        # risk = tradepair means no risk measure considered.
        # Show Graph:
        # Signals and cryptocoin closing
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax2 = ax1.twinx()
        rspine = ax2.spines['right']
        rspine.set_position(('axes', 1.15))
        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        fig.subplots_adjust(right=0.7)
    
        # Get index values for the X axis 
        x_axis = signals.index.get_level_values(0)
        # Plot shaded Bollinger Band 
        ax1.fill_between(x_axis, signals['Upper_Band'], signals['Lower_Band'], color='DarkSeaGreen')
        # Plot Adjust Closing Price and Moving Averages
        ax1.plot(x_axis, signals['Close'], color='blue', lw=2)
        ax1.plot(x_axis, signals['wl_MAV'], color='Teal', lw=2)
        signals[risk].plot(ax=ax1, style='r*', secondary_y=True)
        signals['position'].plot(ax=ax2, style='g--')
        
        # Set Title & Show the Image
        ax1.set_title('{}:{} from {} exchange'.format(alpha_str,tradepair,exchange))
        ax1.set_xlabel('Time units')
        ax1.set_ylabel(risk) 
        #legend
        ax2.legend([ax1.get_lines()[0],
                    ax1.right_ax.get_lines()[0],
                    ax2.get_lines()[0]],
                   [risk, 'signal', 'position'])
        plt.show()

    ############################################################################
    # Buy and Hold: Buy cryptocurrency and holds it for a long period, regardless of fluctuations in the market
    
    def BuyAndHold(self,exchange,tradepair,x_ref,goal,N):
        print('Entry point {}={} in {} Exchange'.format(tradepair, x_ref, exchange))
        df_return = self.dictionary[tradepair].close.apply(lambda x: x/x_ref)
        plt.figure(figsize=(8, 4))
        df_return.plot(grid=True,title='B&H:{} from {} exchange'.format(tradepair,exchange)).axhline(y = goal, color = "green", lw = 2)
        
        last_return=df_return.iloc[-1]
    
        if last_return < goal:
            print('Hold, No goal reached. Last return:{}'.format(last_return))
        else:
            print('GOAL ! ! !, goal reached. Last return:{}'.format(last_return))
        
        return df_return, last_return

    ############################################################################
    # Simple N-Moving Average (SMA)
    # The most common applications of moving averages are to identify trend direction
    # and to determine support and resistance levels.  
    # When asset prices cross over their moving averages, it may generate a trading 
    # signal for technical traders.      
    def SimpleMovingAverage(self,exchange, tradepair, wl):   
        # initialize signals
        alpha_str='SMA'
        signals=pd.DataFrame()
        signals[tradepair]=0
        
        # Calculate simple moving average
        signals['SMA'] = self.dictionary[tradepair].close.rolling(window=wl, min_periods=1, center=False).mean()
        # Create signals
        signals.loc[wl:,tradepair] = np.where(self.dictionary[tradepair][wl:].close 
                                                     > signals['SMA'][wl:], 1.0, 0.0)
        # detect transitions
        signals['position'] = signals[tradepair].diff()    
        # Show Graph:
        #self.PlotSignals(exchange,tradepair,alpha_str,signals,tradepair)
        return signals

    ############################################################################
    # n- and N Movinge Averages Crossover (MAC n,N)
    # A moving average crossover occurs when two different moving average lines 
    # cross over one another.
    # Because moving averages are a lagging indicator, the crossover technique 
    # may not capture exact tops and bottoms. But it can help you identify the 
    # bulk of a trend.
    # If the moving averages cross over one another, it could signal that the 
    # trend is about to change soon, thereby giving you the chance to get a better entry.       
    def MovingAverageCrossover(self, exchange, tradepair, short_window, long_window):
        # initialize signals
        alpha_str='MAC'
        signals=pd.DataFrame()
        signals[tradepair]=0
    
        # Calculate long and short moving averages:
        signals['short_MAC'] = self.dictionary[tradepair].close.rolling(window=short_window, min_periods=1, center=False).mean()
        signals['long_MAC'] = self.dictionary[tradepair].close.rolling(window=long_window, min_periods=1, center=False).mean()
        # create signals
        signals.loc[short_window:,tradepair] = np.where(signals['short_MAC'][short_window:] 
                                                     > signals['long_MAC'][short_window:], 1.0, 0.0)   
    
        # detect transitions
        signals['position'] = signals[tradepair].diff()
    
        # Show Graph:
        #self.PlotSignals(exchange,tradepair,alpha_str,signals,tradepair)
        return signals

    ############################################################################
    # Kaufman Adaptative Moving Average (AMA)
    # Developed by Perry Kaufman, Kaufman's Adaptive Moving Average (KAMA) is a moving 
    # average designed to account for market noise or volatility. KAMA will closely 
    # follow prices when the price swings are relatively small and the noise is low. 
    # KAMA will adjust when the price swings widen and follow prices from a greater distance.
    #
    # First, a cross above or below KAMA indicates directional changes in prices.
    # As with any moving average, a simple crossover system will generate lots of signals and 
    # lots of whipsaws. Chartists can reduce whipsaws by applying a price or time filter to the crossovers. 
    # One might require price to hold the cross for a set number of days or require the cross 
    # to exceed KAMA by a set percentage.    
    def kAdaptativeMovingAverage(self, exchange, tradepair, fast_win, slow_win,T):
        # create signal dataframe
        alpha_str='KAMA'
        signals=pd.DataFrame()
        # get KAMA 
        KAMA=TA.KAMA(self.dictionary[tradepair], ema_fast=fast_win, ema_slow=slow_win, period=T)
        # generate base signal
        signals[tradepair]= np.where(self.dictionary[tradepair].close > KAMA, 1.0, 0.0)
        # detect transitions
        signals['position'] = signals[tradepair].diff()
    
        # Show Graph:
        #self.PlotSignals(exchange,tradepair,alpha_str,signals,tradepair)
        return signals

    ############################################################################
    # Volume Adjusted Moving Average (VAMA)
    # there is a theory behind trading, that if you have got the possibility to Buy an asset 
    # for a price lower than the VAMA is, then you can make a profitable trade.
    # The indicator signalizes that going long is just more advantageous than it was
    # withn the las x time units (window length)
    def VolumeAdjustedMAV(self,exchange, tradepair,wl):
        # create signal dataframe
        alpha_str='VAMA'
        signals=pd.DataFrame()
        # get VAMA 
        VAMA=TA.VAMA(self.dictionary[tradepair],wl,'close')
        # generate base signal
        signals[tradepair]= np.where(self.dictionary[tradepair].close > VAMA, 1.0, 0.0)
        # detect transitions
        signals['position'] = signals[tradepair].diff()
    
        # Show Graph:
        # self.PlotSignals(exchange,tradepair,alpha_str,signals,tradepair)
        return signals


    ############################################################################
    # Standard Deviation Breakout Bollinger Bands
    # According to John Bollinger’s official website, this tool primarily answers 
    # the question:
    # Are prices high or low on a relative basis? By definition price is high at the 
    # upper band and price is low at the lower band. That bit of information is incredibly
    # valuable. It is even more powerful if combined with other tools such as other 
    # indicators for confirmation
    #
    # *spot trading opportunities through looking out for the contraction or expansion of these bands
    def BollingerBandsBreakout(self,exchange, tradepair,wl):
        # initialize signals
        alpha_str='BBZ'
        signals=pd.DataFrame()
        signals[tradepair]=0
        # Calculate simple moving average
        signals['wl_MAV'] = self.dictionary[tradepair].close.rolling(window=wl, min_periods=1, center=False).mean()
        signals['wl_STD']=  self.dictionary[tradepair].close.rolling(window=wl, min_periods=1, center=False).std()
        signals['Upper_Band'] = signals['wl_MAV'] + (signals['wl_STD']*2)
        signals['Lower_Band'] = signals['wl_MAV'] - (signals['wl_STD']*2)
        signals['Close'] = self.dictionary[tradepair].close
    
        # Create signals
        signals.loc[wl:,tradepair] = np.where(self.dictionary[tradepair][wl:].close > signals['Upper_Band'][wl:], 1.0,
                                     (np.where(self.dictionary[tradepair][wl:].close < signals['Lower_Band'][wl:], -1.0, 0.0)))
    
    
        # detect transitions
        signals['position'] = signals[tradepair].diff()
    
        # Show graph
        #self.PlotBBZ(exchange,tradepair,alpha_str,signals,tradepair)
    
        return signals

