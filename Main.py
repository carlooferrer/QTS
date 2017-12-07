# Quantitative Trading Simulator built December 2017
# Made by Carlo Ferrer, Aldwin Uy and with the help of Dr. Kardi Teknomo
# Ateneo de Manila University
# Department of Information Systems and Computer Science
# CS195.6 - A
# SY 2017-2018

# MIT License
#
# Copyright (c) 2017 StoxTek: Carlo Ferrer and Aldwin Uy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import random
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pylab import *
import matplotlib.dates as mdates
from matplotlib import style

style.use('ggplot')

#Start
#Change "_.csv" to the filename of the stock you want to simulate
dataset = pd.read_csv("TM.csv", index_col=0)

def simulatemacd(dataset,strategy):
    #http://www.andrewshamlet.net/2017/01/19/python-tutorial-macd-moving-average-convergencedivergence/
    #Input for Starting Capital and Stock Volume
    capital = int(input('Enter your starting captial: '))
    margin = float(input('Enter number of stocks per trade: '))

    #Compute for MACD (26DayEMA-12DayEMA = MACD)
    pc = pd.DataFrame([])
    pc['Close'] = dataset["Close"]
    time = pd.DataFrame([])
    day = dataset["Day"]
    time = time.append(day)

    ema26 = pd.ewma(pc['Close'],span=26)
    ema12 = pd.ewma(pc['Close'], span=12)
    pc['MACD'] = (ema12 - ema26)
    macd = pc['MACD']
    y = macd
    x = day


    #Compute for MovingAverage
    pc['MA']= pc['MACD'].rolling(8).mean()
    ma = pc['MA']
    z = ma

    #Compute for Histogram
    histogram = macd - ma
    pc['Histogram'] = histogram

    #Trading Signals
    tradesignals = []
    h = pc['Histogram']
    c = pc["Close"]

    balance = []
    startcapital = capital
    inventory = 0
    maxdrawdown = 0
    sellcapital = []
    risk = []

    for i in range(0,len(pc)):
        if h[i] > 0 and h[i-1] < 0:
            tradesignals.append('BUY')
            if capital - (c[i] * margin) < 0:
                balance.append(capital)
            else:
                capital = capital - (c[i] * margin)
                balance.append(capital)
                inventory += margin
        elif h[i] < 0 and h[i-1] > 0:
            if strategy == 1:
                tradesignals.append('SELL')
                capital = capital + (c[i] * inventory)
                balance.append(capital)
                sellcapital.append(capital)
                inventory = 0
            else:
                tradesignals.append('SELL')
                capital = capital + (c[i] * (inventory/2))
                balance.append(capital)
                sellcapital.append(capital)
                inventory = inventory/2
        elif i == (len(pc) - 1):
            tradesignals.append('SELL')
            capital = capital + (c[i] * inventory)
            balance.append(capital)
            sellcapital.append(capital)
        else:
            tradesignals.append('')
            capital = capital
            balance.append(capital)

    for i in range(0,len(sellcapital)):
        if i == len(sellcapital)-1:
            maxdrawdown = maxdrawdown
        elif ((sellcapital[i]-sellcapital[i+1])/sellcapital[i+1]) < maxdrawdown:
            maxdrawdown = ((sellcapital[i]-sellcapital[i+1])/sellcapital[i+1])
        else:
            maxdrawdown = maxdrawdown
    for i in range(0,len(sellcapital)-1):
        risk.append((sellcapital[i + 1] / sellcapital[i]))

    arisk = average(risk) / len(pc) * 254
    riskstd = std(risk)
    sratio = abs((arisk - 0) / riskstd)

    pc['Signals'] = tradesignals
    s = pc['Signals']
    pc['Balance'] = balance
    profit = capital - startcapital
    print(pc)
    print('STARTING CAPITAL: $', startcapital)
    print('ENDING CAPITAL: $', capital)
    print('PROFIT: $', profit)
    print('NUMBER OF STOCKS PER TRADE: ', margin)
    print('NUMBER OF TRADES: ', (pc['Signals'] == 'SELL').sum())
    print('MAXIMUM PROFIT IS AT:')
    print(pc.loc[pc['Balance'].idxmax()])
    print('MAXIMUM DRAWDOWN:', maxdrawdown)
    print('SHARPE RATIO:', sratio)

    #Plotting MACD and MA
    plt.xlabel('Day Number')
    plt.title('MACD and Moving Average')
    grid(True)
    plt.plot(x, y, x ,z)
    plt.show()

    #Plotting Balance of MACD
    plt.plot(balance)
    plt.xlabel('Day Number')
    plt.ylabel('Balance')
    plt.title('MACD Balance')
    plt.show()

    show_menu()

#AROON BY ALDWIN
def simulatearoon(dataset,strategy):

    pc = pd.DataFrame([])
    pc['Open'] = dataset["Open"]
    pc['High'] = dataset["High"]
    pc['Low'] = dataset["Low"]
    pc['Close'] = dataset["Close"]
    pc['Adj Close'] = dataset["Adj Close"]
    pc['Volume'] = dataset["Volume"]

    o = pc['Open']
    h = pc['High']
    l = pc['Low']
    c = pc['Close']
    ac = pc['Adj Close']
    v= pc['Volume']
    time = pd.DataFrame([])
    day = dataset["Day"]
    time = time.append(day)

    i = int(input("Input the value of window : "))
    y = int(input("Input initial balance : "))
    z = int(input("Input number of volume per trade : "))

    AroonUp = []
    AroonDown = []
    AroonDate = []
    AroonOscillator = []
    TradeSignal = []
    onGoingVolume = 0
    onGoingBalance = y
    volumePerTrade = z
    BalanceHistory = []
    counter = 0
    x = i
    maxdrawdown = 0
    sellcapital = []
    risk = []

    # Add buffer for first x days
    for j in range(0, i):
        BalanceHistory.append(onGoingBalance)
        AroonUp.append(0)
        AroonDown.append(0)
        AroonOscillator.append(0)
        TradeSignal.append('')

    while x < len(day):

        # Get Aroon Oscillator

        Aroon_Up = ((h[x - i:x].tolist().index(max(h[x - i:x]))) / float(i)) * 100

        Aroon_Down = ((l[x - i:x].tolist().index(min(l[x - i:x]))) / float(i)) * 100

        AroonUp.append(Aroon_Up)
        AroonDown.append(Aroon_Down)
        AroonDate.append(day[x])
        AroonOscillator.append(int(Aroon_Up - Aroon_Down))

        # Trading Signals
        if counter > 0:
            if x == int(len(day) - 1):  # if last day
                onGoingBalance = onGoingBalance + (onGoingVolume * c[x])
                onGoingVolume = 0
                BalanceHistory.append(onGoingBalance)
                TradeSignal.append("Sell")
            #if AroonOscillator[x - 1] > 90 and AroonOscillator[x] < 0:
            if AroonOscillator[x-1] < -90:
                TradeSignal.append("Sell")
            #elif AroonOscillator[x - 1] < 0 and AroonOscillator[x] > 0:
            elif AroonOscillator[x - 1] > 90:
                TradeSignal.append("Buy")
            else:
                TradeSignal.append("")

            # Balance Changing
            if TradeSignal[x - 1] == "Buy":
                if onGoingBalance - (volumePerTrade * c[x]) < 0:
                    BalanceHistory.append(onGoingBalance)
                else:
                    onGoingBalance = onGoingBalance - (volumePerTrade * c[x])
                    onGoingVolume += volumePerTrade
                    BalanceHistory.append(onGoingBalance)
            elif TradeSignal[x - 1] == "Sell":
                if strategy == 1:
                    onGoingBalance = onGoingBalance + (onGoingVolume * c[x])
                    onGoingVolume = 0
                    BalanceHistory.append(onGoingBalance)
                    sellcapital.append(onGoingBalance)
                else:
                    onGoingBalance = onGoingBalance + ((onGoingVolume/2) * c[x])
                    onGoingVolume = onGoingVolume/2
                    BalanceHistory.append(onGoingBalance)
                    sellcapital.append(onGoingBalance)
            else:
                BalanceHistory.append(onGoingBalance)
            counter += 1
        else:
            counter += 1
        x += 1

    for i in range(0,len(sellcapital)):
        if i == len(sellcapital)-1:
            maxdrawdown = maxdrawdown
        elif ((sellcapital[i]-sellcapital[i+1])/sellcapital[i+1]) < maxdrawdown:
            maxdrawdown = ((sellcapital[i]-sellcapital[i+1])/sellcapital[i+1])
        else:
            maxdrawdown = maxdrawdown

    for i in range(0,len(sellcapital)-1):
        risk.append((sellcapital[i + 1] / sellcapital[i]))

    arisk = average(risk) / len(pc) * 254
    riskstd = std(risk)
    sratio = abs((arisk - 0) / riskstd)

    pc['Aroon Up'] = AroonUp
    pc['Aroon Down'] = AroonDown
    pc['Aroon Oscillator'] = AroonOscillator
    pc['Balance'] = BalanceHistory
    profit = onGoingBalance - y
    print(pc)

    print('STARTING CAPITAL: $', y)
    print('ENDING CAPITAL: $', onGoingBalance)
    print('PROFIT: $', profit)
    print('NUMBER OF STOCKS PER TRADE: ', z)
    print('NUMBER OF TRADES: ', TradeSignal.count('Sell'))
    print('MAXIMUM PROFIT IS AT:')
    print(pc.loc[pc['Balance'].idxmax()])
    print('MAXIMUM DRAWDOWN:', maxdrawdown)
    print('SHARPE RATIO:', sratio)

    plt.plot(BalanceHistory)
    plt.xlabel('Day Number')
    plt.ylabel('Balance')
    plt.title('Aroon Oscillator Balance')
    plt.show()

    show_menu()

def simulateturtle(dataset,strategy):
    # Input for Starting Capital and Stock Volume
    capital = int(input('Enter your starting captial: '))
    margin = float(input('Enter number of stocks per trade: '))

    #Start
    pc = pd.DataFrame([])
    pc['Close'] = dataset["Close"]

    time = pd.DataFrame([])
    day = dataset["Day"]
    time = time.append(day)

    #Calculate Days of Breakouts
    #20, 20, 10 combination works best for IBM
    pc['90Highs'] = pc['Close'].rolling(window=90).max()
    pc['90Lows'] = pc['Close'].rolling(window=90).min()
    pc['45Lows'] = pc['Close'].rolling(window=45).min()


    # Trading Signals
    # You can use 20Lows or 10Lows for Sell signal but 20Lows works better
    tradesignals = []
    c = pc["Close"]
    h = pc['90Highs']
    l = pc['90Lows']
    hl = pc['45Lows']

    balance = []
    inventory = 0
    startcapital = capital
    maxdrawdown = 0
    sellcapital = []
    risk = []

    for i in range(0,len(pc)):
        if c[i] >= h[i] and capital > (c[i] * margin):
            tradesignals.append('BUY')
            capital = capital - ((c[i] * margin))
            balance.append(capital)
            inventory += margin
        elif c[i] <= l[i] and inventory > 0:
            if strategy == 1:
                tradesignals.append('SELL')
                capital = capital + ((c[i] * inventory))
                balance.append(capital)
                sellcapital.append(capital)
                inventory = 0
            else:
                tradesignals.append('SELL')
                capital = capital + ((c[i] * inventory/2))
                balance.append(capital)
                sellcapital.append(capital)
                inventory = inventory/2
        elif i == (len(pc)-1):
            tradesignals.append('SELL')
            capital = capital + (c[i] * inventory)
            balance.append(capital)
            sellcapital.append(capital)
        else:
            tradesignals.append('')
            capital = capital
            balance.append(capital)

    for i in range(0,len(sellcapital)):
        if i == len(sellcapital)-1:
            maxdrawdown = maxdrawdown
        elif ((sellcapital[i]-sellcapital[i+1])/sellcapital[i+1]) < maxdrawdown:
            maxdrawdown = ((sellcapital[i]-sellcapital[i+1])/sellcapital[i+1])
        else:
            maxdrawdown = maxdrawdown

    for i in range(0,len(sellcapital)-1):
        risk.append((sellcapital[i + 1] / sellcapital[i]))

    arisk = average(risk)/len(pc)*254
    riskstd = std(risk)
    sratio = abs((arisk-0)/riskstd)

    pc['Signals'] = tradesignals
    s = pc['Signals']
    pc['Balance'] = balance
    pc['Inventory'] = inventory
    profit = capital - startcapital
    print(pc)
    print('STARTING CAPITAL: $', startcapital)
    print('ENDING CAPITAL: $', capital)
    print('PROFIT: $', profit)
    print('NUMBER OF STOCKS PER TRADE: ', margin)
    print('NUMBER OF TRADES: ', (pc['Signals'] == 'SELL').sum())
    print('MAXIMUM PROFIT IS AT:')
    print(pc.loc[pc['Balance'].idxmax()])
    print('MAXIMUM DRAWDOWN:', maxdrawdown)
    print('SHARPE RATIO:', sratio)


    # Plotting Balance of Turtle
    plt.plot(balance)
    plt.xlabel('Day Number')
    plt.ylabel('Balance')
    plt.title('Turtle Trading Balance')
    plt.show()

    show_menu()

def doubletop(dataset):
    pc = pd.DataFrame([])
    df = pd.DataFrame([])

    ohlc = (dataset['Open'] + dataset['High'] + dataset['Low'] + dataset['Close'])/4
    df['OHLC'] = ohlc
    maxpeak3 = []
    t = []
    chartpattern = []
    slope = []
    for i in range(0,len(df)):
        if i == 0 or i == 1 or i == 2 or i == 3 or i == len(df)-1 or i == len(df)-2 or i == len(df)-3:
            pass
        else:
            if ohlc[i]>ohlc[i-1] and ohlc[i]>ohlc[i-2] and ohlc[i]>ohlc[i-3] and ohlc[i]>ohlc[i+1] and ohlc[i]>ohlc[i+2] and ohlc[i]>ohlc[i+3]:
                maxpeak3.append(ohlc[i])
                t.append(i)
    for i in range(0,len(maxpeak3)):
        if i == 0 or i == 1 or i == len(maxpeak3)-1 or i == len(maxpeak3) -2:
            chartpattern.append('')
            slope.append(0)
        else:
            if 0 < abs(((maxpeak3[i]-maxpeak3[i-1])/(t[i] - t[i-1])) - ((maxpeak3[i+1]-maxpeak3[i])/(t[i+1] - t[i]))) < 0.01:
                chartpattern.append('Has Double Top')
                slope.append(abs(((maxpeak3[i]-maxpeak3[i-1])/(t[i] - t[i-1])) - ((maxpeak3[i+1]-maxpeak3[i])/(t[i+1] - t[i]))))
            else:
                chartpattern.append('')
                slope.append(abs(((maxpeak3[i] - maxpeak3[i - 1]) / (t[i] - t[i - 1])) - ((maxpeak3[i + 1] - maxpeak3[i]) / (t[i + 1] - t[i]))))
    pc['Day'] = t
    pc['Max Peak 3'] = maxpeak3
    pc['Difference of Slopes'] = slope
    pc['Chart Pattern'] = chartpattern
    doubletop = pc['Chart Pattern'] == 'Has Double Top'
    print(pc[doubletop])
    print(len(pc[doubletop]), "instances has Double Top out of", len(pc), "max peaks.")
    show_menu()

def doublebottom(dataset):
    pc = pd.DataFrame([])
    df = pd.DataFrame([])

    ohlc = (dataset['Open'] + dataset['High'] + dataset['Low'] + dataset['Close']) / 4
    df['OHLC'] = ohlc
    minpeak3 = []
    t = []
    chartpattern = []
    slope = []
    for i in range(0, len(df)):
        if i == 0 or i == 1 or i == 2 or i == 3 or i == len(df) - 1 or i == len(df) - 2 or i == len(df) - 3:
            pass
        else:
            if ohlc[i] < ohlc[i - 1] and ohlc[i] < ohlc[i - 2] and ohlc[i] < ohlc[i - 3] and ohlc[i] < ohlc[i + 1] and ohlc[i] < ohlc[i + 2] and ohlc[i] < ohlc[i + 3]:
                minpeak3.append(ohlc[i])
                t.append(i)
    for i in range(0, len(minpeak3)):
        if i == 0 or i == 1 or i == len(minpeak3) - 1 or i == len(minpeak3) - 2:
            chartpattern.append('')
            slope.append(0)
        else:
            if 0 < abs(((minpeak3[i] - minpeak3[i - 1]) / (t[i] - t[i - 1])) - ((minpeak3[i + 1] - minpeak3[i]) / (t[i + 1] - t[i]))) < 0.01:
                slope.append(abs(((minpeak3[i] - minpeak3[i - 1]) / (t[i] - t[i - 1])) - ((minpeak3[i + 1] - minpeak3[i]) / (t[i + 1] - t[i]))))
                chartpattern.append('Has Double Bottom')
            else:
                slope.append(abs(((minpeak3[i] - minpeak3[i - 1]) / (t[i] - t[i - 1])) - ((minpeak3[i + 1] - minpeak3[i]) / (t[i + 1] - t[i]))))
                chartpattern.append('')

    pc['Day'] = t
    pc['Minimum Peak 3'] = minpeak3
    pc['Difference of Slopes'] = slope
    pc['Chart Pattern'] = chartpattern
    doublebottom = pc['Chart Pattern'] == 'Has Double Bottom'
    print(pc[doublebottom])
    print(len(pc[doublebottom]), "instances has Double Bottom out of", len(pc), "minimum peaks.")
    show_menu()

def graphClosingPrice(dataset):
    priceclose = pd.DataFrame([])
    closingprice = dataset["Close"]
    priceclose = priceclose.append(closingprice)
    priceclose = pd.concat([priceclose.T[x] for x in priceclose.T], ignore_index =True)
    y = closingprice
    x = dataset["Day"]
    plt.xlabel('Day Number')
    plt.ylabel('Closing Price')
    plt.title('Closing Price Graph')
    grid(True)
    plot(x,y)
    plt.show()
    show_menu()

# Choices for menu
def show_menu():
    print("MENU")
    print("1. Simulate MACD")
    print("2. Simulate Aroon Oscillator")
    print("3. Simulate Turtle Trading")
    print("4. Graph Closing Price")
    print("5. Look for Pattern")
    print("6. Exit")
    choice = int(input('Enter the number of you choice: '))
    if choice == 1:
        strategy = int(input('If you want simple trading, enter 1. If you want cumulative trading enter 2: '))
        if strategy == 1:
            simulatemacd(dataset,1)
        elif strategy == 2:
            simulatemacd(dataset, 2)
        else:
            print("Try again")
            show_menu()
    elif choice == 2:
        strategy = int(input('If you want simple trading, enter 1. If you want cumulative trading enter 2: '))
        if strategy == 1:
            simulatearoon(dataset, 1)
        elif strategy == 2:
            simulatearoon(dataset, 2)
        else:
            print("Try again")
            show_menu()
    elif choice == 3:
        strategy = int(input('If you want simple trading, enter 1. If you want cumulative trading enter 2: '))
        if strategy == 1:
            simulateturtle(dataset, 1)
        elif strategy == 2:
            simulateturtle(dataset, 2)
        else:
            print("Try again")
            show_menu()
    elif choice == 4:
        graphClosingPrice(dataset)
    elif choice == 5:
        print('1. Look for Double Top')
        print('2. Look for Double Bottom')
        pattern = int(input('Enter the number of the pattern you want: '))
        if pattern == 1:
            doubletop(dataset)
        elif pattern == 2:
            doublebottom(dataset)
        else:
            print('Try again')
            show_menu()
    elif choice == 6:
        pass
    else:
        print("Try again")
        show_menu()

title = "Quantitative Trading Simulation"
print(title)
print("Data Set:", "\n", dataset)
show_menu()