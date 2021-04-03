import requests as rq
import json

res = rq.get('https://m.stock.naver.com/api/json/sise/siseListJson.nhn?menu=market_sum&sosok=0&pageSize=20000&page=1')
data = res.json()["result"]['itemList']

with open("code.json", "w", encoding='utf-8') as json_file:
  d = [] 
  for dd in data:
    d.append({
      'name': str(dd['nm']),
      'code': dd['cd'],
    })
  json.dump(d, json_file)


with open("code.json", "r", encoding='utf-8') as json_file:
  data = json.load(json_file)
  print(data)


