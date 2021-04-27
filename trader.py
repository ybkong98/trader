import time
import pyupbit
import datetime

access = "ShkhhIzBOStvE1htVAWxXxX1mxOo69u5JpZ38OH1"
secret = "Sn23wuVplOd82za6GALKxfovqYYI5qa2Lebnro1at"

def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTT",count=24,interval="minute60")
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0005
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror


def get_k():
    result=0.5
    M=0
    for k in np.arange(0.1, 1.0, 0.1):
     ror = get_ror(k)
     if ror>M:
         M=ror
         result=k
    return result

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=72)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15시간 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
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
        start_time = get_start_time("KRW-BTT")
        end_time = start_time + datetime.timedelta(hours=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTT", get_k())
            ma15 = get_ma15("KRW-BTT")
            current_price = get_current_price("KRW-BTT")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTT", krw*0.9995)
        else:
            BTT = get_current_price("KRW-BTT")*get_balance("KRW-BTT")
            if btc > 5000:
                upbit.sell_market_order("KRW-BTT", BTT*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
