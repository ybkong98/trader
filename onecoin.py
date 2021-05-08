import time
import pyupbit
import datetime
import numpy as np

access = "3lRyWFJGeaWrinlGBpNDNrTbfKtIyaDo9ivqDSBZ"
secret = "Yo4CmD2i1ULxfete4adBRKqxcc7JmwgNioW8GAHb"

ticker="KRW-DOGE"
def get_ror(ticker="KRW-DOGE",k=0.5):
    #백테스팅으로 k값에 따른 수익률 산출
    df = pyupbit.get_ohlcv(ticker, count=7,interval="minute60")
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_ma15(ticker):
    #15시간 평균
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_k(ticker="KRW-DOGE"):
    #백테스팅 기반, 최선의 변동성 계수 산출
    finalK,maxRor=0,0
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(ticker,k)
        if maxRor<ror:
            finalK,maxRor=k,ror
    return finalK


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
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-DOGE")
        end_time = start_time + datetime.timedelta(hours=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-DOGE", get_k())
            current_price = get_current_price("KRW-DOGE")
            print(target_price,current_price)
            if target_price < 1.01*current_price and get_ma15(ticker="KRW-DOGE")<current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-DOGE", krw*0.9995)
        else:
            DOGE = get_balance("DOGE")*get_current_price("KRW-DOGE")
            if DOGE > 5000:
                upbit.sell_market_order("KRW-DOGE", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
