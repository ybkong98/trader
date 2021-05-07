import time
import pyupbit
import datetime
import numpy as np
import pandas

access = "key"
secret = "key"

tickers=pyupbit.get_tickers(fiat="KRW")

def get_ror(ticker="KRW-BTC",k=0.5):
    #백테스팅으로 k값에 따른 수익률 산출
    df = pyupbit.get_ohlcv(ticker, count=7,interval="minute60")
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_k(ticker="KRW-BTC"):
    #백테스팅 기반, 최선의 변동성 계수 산출
    finalK,maxRor=0,0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(ticker,k)
        if maxRor<ror:
            finalK,maxRor=k,ror
    return finalK,maxRor
    
def get_best_coin(coins=tickers):
    resultCoin,resultK=None,0
    maxror=0
    for coin in coins:
        k,ror=get_k(ticker=coin)
        target_price=get_target_price(ticker=coin, k=k)
        current_price=get_current_price(ticker=coin)
        ma15=get_ma15(ticker=coin)
        if target_price<current_price or ma15<=current_price:
            continue
        if target_price/current_price>maxror:
            maxror,resultCoin,resultK=target_price/current_price,coin,k
        time.sleep(0.4)
    return resultCoin,resultK

def get_target_price(ticker, k):
    #변동성 돌파 전략으로 매수 목표가 조회
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    #시작 시간 조회
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    #15시간 평균
    df = pyupbit.get_ohlcv(ticker, interval="minute240", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    #잔고 조회
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("Login done")


ticker=None

# 자동매매 시작
while True:
    try:
        tickers=pyupbit.get_tickers(fiat="KRW")
        #코인, 변동성 상수 탐색
        if ticker is None:
            ticker,k=get_best_coin(coins=tickers)
        
        #거래시간설정
        now = datetime.datetime.now()
        start_time = get_start_time(ticker)
        end_time = start_time + datetime.timedelta(hours=1)
        
        print("coin=",ticker,"k=",k)
        if start_time < now < end_time - datetime.timedelta(seconds=300):
            target_price = get_target_price(ticker, k)
            ma15 = get_ma15(ticker)
            current_price = get_current_price(ticker)
            print(target_price/current_price,ma15,current_price)
            if target_price > 1.011*current_price and ma15 < current_price:
                if start_time==get_start_time(ticker=ticker):
                    krw = get_balance("KRW")
                    if krw > 5000:
                        print("Buy Order ",ticker)
                        upbit.buy_market_order(ticker, krw*0.9995)
                        buy=ticker
                else:
                    coin = get_balance(buy[4:])*get_current_price(buy)
                    if coin > 5000:
                        print("Sell Order ",ticker)
                        upbit.sell_market_order(buy, coin*0.9995)
            ticker=None

        else:
            coin = get_balance(buy[4:])*get_current_price(buy)
            if coin > 5000:
                print("Sell Order ",ticker)
                upbit.sell_market_order(buy, coin*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
