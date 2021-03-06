# -*- coding: utf-8 -*-

# sys
import datetime
import re
import traceback

# thirdpart
import pandas as pd
import pymongo
from pymongo import MongoClient
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, DateFormatter
from pymongo import MongoClient
from pymongo import errors

#this project
import util
import const

def getWeekofYear():
  iso = datetime.datetime.now().isocalendar()
  return int(iso[0]) * 100 + int(iso[1])


def String2Number(s):
  out = np.nan
  try:
    out = float(re.findall('([-+]?\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?', s)[0][0])
  except Exception as e:
    pass

  return out


def SaveMongoDB(data, dbName, collectionName):
  client = MongoClient()
  db = client[dbName]
  collection = db[collectionName]
  result = data
  
  try:
    update_result = collection.update_one({'_id': result['_id']},
                                          {'$set': result})  # , upsert=True)
    
    if update_result.matched_count > 0:
      print('upate to Mongo: %s : %s' % (dbName, collectionName))
      if update_result.modified_count > 0:
        # detail[k] = result
        pass
    
    if update_result.matched_count == 0:
      try:
        if collection.insert_one(result):
          print('insert to Mongo: %s : %s' % (dbName, collectionName))
          # detail[k] = result
      except errors.DuplicateKeyError as e:
        print('faild to Mongo!!!!: %s : %s' % (dbName, collectionName))
        pass
  
  except Exception as e:
    print(e)
    



def SaveMongoDB_DF(data: pd.DataFrame, dbName, collectionName, insert=True):
  print('enter SaveMongoDBDF')
  client = MongoClient()
  db = client[dbName]
  collection = db[collectionName]


  for k, v in data.iterrows():
    result = v.to_dict()

    try:
      update_result = collection.update_one({'_id': result['_id']},
                                          {'$set': result}, upsert=insert)

      if update_result.matched_count > 0 and update_result.modified_count > 0:
        print('update to Mongo: %s : %s'%(dbName, collectionName))
      elif update_result.upserted_id is not None:
        print('insert to Mongo: %s : %s : %s' % (dbName, collectionName, update_result.upserted_id))

    except errors.DuplicateKeyError as e:
      print('DuplicateKeyError to Mongo!!!: %s : %s : %s' % (dbName, collectionName, result['_id']))
    except Exception as e:
      print(e)

  print('leave SaveMongoDBDF')



def SaveMongoDBDict(data: dict, dbName, collectionName, insert=True):
  print('enter SaveMongoDBDict')
  client = MongoClient()
  db = client[dbName]
  collection = db[collectionName]


  for k, v in data.items():
    try:
      update_result = collection.update_one({'_id': k},
                                          {'$set': v}, upsert=insert)

      if update_result.matched_count > 0 and update_result.modified_count > 0:
        print('update to Mongo: %s : %s'%(dbName, collectionName))
      elif update_result.upserted_id is not None:
        print('insert to Mongo: %s : %s : %s' % (dbName, collectionName, update_result.upserted_id))

    except errors.DuplicateKeyError as e:
      print('DuplicateKeyError to Mongo!!!: %s : %s : %s' % (dbName, collectionName, k))
    except Exception as e:
      print(e)

  print('leave SaveMongoDBDict')

  
def QueryHS300All():
  client = MongoClient()
  db = client['stock']
  collection = db['hs300_stock_list']

  out = []

  cursor = collection.find()
  for c in cursor:
    out.append(c)

  if len(out):
    df = pd.DataFrame(out)
    df.set_index(const.HS300.KEY_NAME['code'], inplace=True)
    return df
  else:
    return None
  
  

def QueryCodeList():
  client = MongoClient()
  db = client['stock']
  collection = db['hs300_stock_list']

  out = []

  cursor = collection.find()
  index = 0
  for c in cursor:
    out.append(c[const.HS300.KEY_NAME['code']])

  return out



def QueryAll():
  client = MongoClient()
  db = client['stock']
  collection = db['stock_list']

  out = []

  cursor = collection.find()
  for c in cursor:
    out.append(c)

  if len(out):
    df = pd.DataFrame(out)
    df.set_index("_id", inplace=True)
    return df
  else:
    return None
  
  
def PrintException(e):
  msg = traceback.format_exc()
  print(msg)


#??????????????????
def LoadData(dbName, collectionName, condition={}, sort=[('_id', 1)], limit=None):
  client = MongoClient()
  db = client[dbName]
  collection = db[collectionName]
  cursor = collection.find(condition).sort(sort)
  if limit is not None:
    cursor = cursor.limit(limit)
  out = []
  for c in cursor:
    out.append(c)

  if len(out):
    df = pd.DataFrame(out)
    # df.drop('date', axis=1, inplace=True)
    df.set_index('_id', inplace=True)
    return df

  return None


#??????code??????????????????
def LoadData2(dbName, collectionName, codes):
  client = MongoClient()
  db = client[dbName]
  collection = db[collectionName]
  out = []
  for code in codes:
    cursor = collection.find({'_id': code})
    for c in cursor:
      out.append(c)
      break

  if len(out):
    df = pd.DataFrame(out)
    try:
      df.drop('name', axis=1, inplace=True)
    except Exception as e:
      pass
    df.set_index('_id', inplace=True)
    return df


def LastPriceNone(codes):
  client = MongoClient()
  
  out = []
  for code in codes:
    db = client['stock_all_kdata_none']
    collection = db[code]
    cursor = collection.find().sort([('_id', -1)]).limit(1)
    for c in cursor:
      out.append({'_id': code, 'price': c['close']})
      break

  if len(out):
    df = pd.DataFrame(out)
    df.set_index('_id', inplace=True)
    return df


  return None



def LoadQuaterPaper(year, code):
  # ????????????
  first = {}
  second = {}
  third = {}
  forth = {}
  client = MongoClient()
  db = client["stock"]
  collection = db["yjbg-" + code]
  strYear = str(year)
  # ?????????
  cursor = collection.find({"_id": strYear + "-03-31"})
  for c in cursor:
    first['sjltz'] = c['sjltz']
    break

  # ?????????
  cursor = collection.find({"_id": strYear + "-06-30"})
  for c in cursor:
    second['sjltz'] = c['sjltz']
    break

  # ?????????
  cursor = collection.find({"_id": strYear + "-09-30"})
  for c in cursor:
    third['sjltz'] = c['sjltz']
    break

  # ?????????
  cursor = collection.find({"_id": strYear + "-12-31"})
  for c in cursor:
    forth['sjltz'] = c['sjltz']
    break

  return (first, second, third, forth)



def LoadForecast(year, code):
  # ????????????
  first = {}
  second = {}
  third = {}
  forth = {}
  client = MongoClient()
  db = client["stock"]
  strYear = str(year)
  
  # ?????????
  collection = db["yjyg-" + str(strYear) + "-03-31"]
  cursor = collection.find({"_id": code})
  for c in cursor:
    first['date'] = c['????????????']
    first['forecast'] = c['????????????']
    break

  # ?????????
  collection = db["yjyg-" + str(strYear) + "-06-30"]
  cursor = collection.find({"_id": code})
  for c in cursor:
    second['date'] = c['????????????']
    second['forecast'] = c['????????????']
    break

  # ?????????
  collection = db["yjyg-" + str(strYear) + "-09-30"]
  cursor = collection.find({"_id": code})
  for c in cursor:
    third['date'] = c['????????????']
    third['forecast'] = c['????????????']
    break

  # ?????????
  collection = db["yjyg-" + str(strYear) + "-12-31"]
  cursor = collection.find({"_id": code})
  for c in cursor:
    forth['date'] = c['????????????']
    forth['forecast'] = c['????????????']
    break

  return (first, second, third, forth)



def LoadYearPaper(y, code):
  # ?????????????????????
  midYear = {}
  year = {}
  client = MongoClient()
  db = client["stock"]
  collection = db["gpfh-" + str(y) + "-06-30"]
  cursor = collection.find({"_id": code})
  for c in cursor:
    midYear[const.GPFH_KEYWORD.KEY_NAME['CQCXR']] = c[const.GPFH_KEYWORD.KEY_NAME['CQCXR']]
    midYear[const.GPFH_KEYWORD.KEY_NAME['AllocationPlan']] = c[const.GPFH_KEYWORD.KEY_NAME['AllocationPlan']]
    midYear[const.GPFH_KEYWORD.KEY_NAME['EarningsPerShare']] = c[const.GPFH_KEYWORD.KEY_NAME['EarningsPerShare']]
    break
  else:
    midYear.update({'notExist': 1})

  collection = db["gpfh-" + str(y) + "-12-31"]
  cursor = collection.find({"_id": code})
  for c in cursor:
    year[const.GPFH_KEYWORD.KEY_NAME['CQCXR']] = c[const.GPFH_KEYWORD.KEY_NAME['CQCXR']]
    year[const.GPFH_KEYWORD.KEY_NAME['AllocationPlan']] = c[const.GPFH_KEYWORD.KEY_NAME['AllocationPlan']]
    year[const.GPFH_KEYWORD.KEY_NAME['EarningsPerShare']] = c[const.GPFH_KEYWORD.KEY_NAME['EarningsPerShare']]
    break
  else:
    year.update({'notExist': 1})

  return (midYear, year)


#########################################################
def Quater2Date(year, quarter):
  # ???????????????????????????????????????
  if quarter == 'first':
    return pd.to_datetime(np.datetime64(str(year) + '-04-30T00:00:00Z'))
  elif quarter == 'second':
    return pd.to_datetime(np.datetime64(str(year) + '-08-31T00:00:00Z'))
  elif quarter == 'third':
    return pd.to_datetime(np.datetime64(str(year) + '-10-31T00:00:00Z'))
  elif quarter == 'forth':
    # ???????????????,???????????????????????????29????????????
    return pd.to_datetime(np.datetime64(str(year + 1) + '-04-29T00:00:00Z'))
  
  
def ForecastString2Int(info):
  infos = {
    "??????": -100,
    "??????": 1,
    "??????": -1,
    "??????": -10,
    "??????": -50,
    "??????": -20,
    "??????": -30,
    "??????": 1,
    "??????": 1,
    "??????": -1,
  }
  if info in infos:
    return infos[info]
  else:
    return -5