import os
import requests as rq
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA, ARMA
from statsmodels.tsa.seasonal import seasonal_decompose

from matplotlib import font_manager, rc
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
import time

rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

CODE = {
  "NAVER": "035420",
  "카카오": "035720",
  "삼성전자": "005930",
  "안랩": "053800",
  "엔씨소프트": "036570",
  "유바이오로직스": "206650",
  "디피씨": "026890"
}

URL = 'https://m.stock.naver.com/api/item/getPriceDayList.nhn?code={code}&pageSize=10000&page=1'

def getTodayDatetime():
  return str(datetime.now()).split(' ')[0]

def makePath(code):
  return 'data/{date}/{code}.csv'.format(date=getTodayDatetime(), code=code)

def _isData(code):
  path=makePath(code)
  return os.path.exists(path)

def save(code, data):
  df = pd.DataFrame(data)
  dt = pd.to_datetime(df['dt'], format='%Y-%m-%d')
  ncv = df['ncv']
  
  pd.concat([dt, ncv], axis=1).iloc[::-1].to_csv(makePath(code), index=False)
  
def getFund(code):
  isData = _isData(code)

  if not isData:
    res = rq.get(URL.format(code=CODE[code]))
    data = res.json()
    save(code, data['result']['list'])
    print('success created data file : {code} '.format(code=makePath(code)))
  else :
    print('success loaded data file : {code} '.format(code=makePath(code)))

  return pd.read_csv(makePath(code), header=0, index_col=['dt'])

def getLastDate(data):
  lastDate = fundData.tail(1).index[0]
  return _dt(lastDate)

def _dt(dtStr):
  s = dtStr.split(' ')[0]
  splited = s.split('-')
  return datetime(int(splited[0]), int(splited[1]), int(splited[2]), 0, 0, 0)

if __name__ == "__main__":
  save_dir = 'data/{date}'.format(date=getTodayDatetime())
  
  if not os.path.exists(save_dir):
    os.mkdir(save_dir)

  names = [
    "카카오",
    "NAVER",
    "엔씨소프트",
  ]

  for nameIdx, name in enumerate(names):
    predictCnt = 200
    fundData = getFund(name)

    lastDate = getLastDate(fundData)
    model = ARIMA(fundData, order=(2,1,2))
    model_fit = model.fit(trend='c', full_output=False, disp=1, freq='D') # trend: c, nc
    print(model_fit.summary())

    fore = model_fit.forecast(steps=predictCnt)
    prev_d = {
      'dt': [_dt(i) for i in fundData.tail(10).index],
      'ncv': [i for i in fundData.tail(10)['ncv']]
    }
    next_d = {
      'dt': [_dt(i) for i in fundData.tail(1).index],
      'ncv': [i for i in fundData.tail(1)['ncv']]
    }

    for idx, val in enumerate(fore[0]):
      dt = lastDate + timedelta(days=idx + 1)
      next_d['dt'].append(dt)
      next_d['ncv'].append(val)
      # print(lastDate + timedelta(days=idx + 1), val)

    df = pd.DataFrame(next_d)
    
    if (len(names) != 1):
      plt.subplot(len(names)+1, 1, nameIdx+1) 

    plt.plot(prev_d['dt'], prev_d['ncv'], label="실츨값", marker='x')
    plt.plot(df['dt'], df['ncv'], label="예측값",)

    if len(names) - 1 != nameIdx: 
      ax = plt.gca()
      ax.axes.xaxis.set_visible(False)
    plt.xlabel('time(day)')
    plt.xticks(rotation=45)
    plt.ylabel('price')
    
    plt.grid()
    plt.legend()
    title = '{name}({lastDate})'.format(name=name, lastDate=str(lastDate).split(' ')[0])
    plt.title(title)
    print(title)
    # time.sleep(3)

    # plt.savefig('{title}.png'.format(title=title), bbox_inches='tight')
  plt.show()