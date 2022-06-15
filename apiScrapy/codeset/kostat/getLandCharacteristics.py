#!/usr/bin/env python
# coding: utf-8

# ## 1. 필요 라이브러리 선언

# In[1]:


import os
import sys
os.chdir('/data/KITECH/apiScrapy/codeset/kostat/')
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname("./"))))
from common import commonFunc as cf
import pandas as pd
import pickle
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import psycopg2
from sqlalchemy import create_engine
import gc
# from concurrent.futures import ThreadPoolExecutor
# import concurrent.futures


# ## 2. 필요 변수 선언

# ### 2-1. 메타데이터 업로드

# In[2]:


metadata = pd.read_excel("../../input/datalake_meta22.xlsx", sheet_name="3. 통계청",engine="openpyxl")


# ### 2-2. output 폴더 생성 변수
SITENAME = "kostat"
DATANAME= "토지특성속성조회"
targetData = metadata.loc[metadata.자료명==DATANAME]
SERVICENAME = targetData["서비스키"].values[0].split(".")[0]

org_data = pd.DataFrame()
try:
    # 기존 데이터 및 파라미터 정보 불러오기
    org_data = cf.loadparam(SITENAME,DATANAME,SERVICENAME)
## 파일이 없는경우
except Exception as e:
    print(e)

tot_cnt = 0

# ### 2-3. 기본키 설정
# #### 1) API KEY
with open("../../input/ppsapikey.pickle","rb") as fr:
        ServiceKeyLst = pickle.load(fr)

pnuDf = pd.read_csv("./행정구역코드(법정동코드).csv", encoding="ms949")
pnuList = pnuDf.loc[pnuDf.폐지여부 == "존재"].법정동코드.values.tolist()

numOfRows = "999"

BASEPARAM_KEY = targetData.기본키.values[0].split(",")
BASEPARAM_Lst = []

BASEPARAM_VAL = [numOfRows]

for i in range(len(pnuList)):
    BASEPARAM = {}
    BASEPARAM_VAL.append(pnuList[i])
    for j in range(len(BASEPARAM_VAL)):
        BASEPARAM[BASEPARAM_KEY[j]] = BASEPARAM_VAL[j]
    BASEPARAM_Lst.append(BASEPARAM)
    BASEPARAM_VAL.pop()

# ### 2-4. 함수 파라미터
URL = targetData["URL"].values[0]
PAGEYN=1
STDENCODING='utf-8'
APICALL=0
inType = "xml"
mode = 1
jsonkey = "field"


# ## 3. 데이터 수집
# ### 3-2. 데이터 수집
breakPoint = 0
# ## 가) 초기 인증키를 통한 수집
flag = False
pageList = []
dfList = []
failList = []

starttime = time.time()
print("수집시작 : ", time.strftime('%c', time.localtime(time.time())))
for i in range(len(ServiceKeyLst)):
    if flag:
        break
    while (breakPoint < len(BASEPARAM_Lst)):
        if breakPoint == len(BASEPARAM_Lst) - 1:
            flag = True
        try:
            BASEPARAM_Lst[breakPoint]["ServiceKey"] = ServiceKeyLst[i]
            scrapyResult = cf.scrapy(URL,SITENAME,DATANAME,SERVICENAME,BASEPARAM_Lst[breakPoint],PAGEYN,ServiceKeyLst,APICALL, jsonkey=jsonkey,inType=inType)
            resultDf = scrapyResult[0]
            if resultDf is None:
                failList.append(BASEPARAM_Lst[breakPoint])
                if breakPoint <= len(BASEPARAM_Lst) - 1:
                    breakPoint=breakPoint+1
                continue
            elif type(resultDf) == pd.core.frame.DataFrame:
                if resultDf.empty:
                    failList.append(BASEPARAM_Lst[breakPoint])
                    if breakPoint <= len(BASEPARAM_Lst) - 1:
                        breakPoint=breakPoint+1
                    continue
            dfList.append(resultDf)
            pageList.append(scrapyResult[1])
            APICALL = scrapyResult[2]
            tot_cnt = tot_cnt + scrapyResult[3]
        except Exception as e:
            print(e)
            if e.args[0] == "22" or e.args[0] == "20":
                print("LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR")
                break
            else:
                time.sleep(10)
        else:
            if breakPoint <= len(BASEPARAM_Lst) - 1:
                breakPoint=breakPoint+1

##################################

finalResultDf = pd.concat(dfList).reset_index(drop=True)

completed = False
data_chg_cnt = len(finalResultDf)

if tot_cnt == data_chg_cnt or (tot_cnt != data_chg_cnt and len(failList) == 0):
    completed = True
    print("수집 종료 : ", time.time()-starttime)
else:
    print("수집 실패 : ", time.time()-starttime)

if completed:
    exit_date = datetime.now().strftime("%Y%m%d")

    typical_col = ['ctgry_cd', 'ctgry_nm', 'phase_cd', 'phase_nm', 'lifecycle_cd',
           'lifecycle_nm', 'clnt_cd', 'clnt_nm', 'biz_regst_num', 'cntrct_frm_nm',
           'domain_cd', 'domain_nm', 'facility_cd', 'facility_nm',
           'cnstrct_wrk_cd', 'cnstrct_wrk_nm', 'wbslv1_cd', 'wbslv1_nm',
           'wbslv2_cd', 'wbslv2_nm', 'authrt_lv_cd', 'authrt_lv_nm', 'reg_ymd',
           'end_ymd', 'strg_dir', 'strg_filename', 'data_src', 'ntwrk',
           'clct_mthd', 'clmn_nm_hanguel', 'clmn_nm', 'preprcs', 'updt_cycle',
           'req_url', 'svc_key', 'base_key', 'req_param', 'data_type']

    dtype = {}

    for each in typical_col:
        dtype[each] = str

    clc_typcial = pd.read_csv("../../../input/meta/clc_typical.csv", names=typical_col, dtype=dtype)

    index = clc_typcial[(clc_typcial.ctgry_nm == "통계청") & (clc_typcial.strg_filename == f'{DATANAME}.csv')].index.values[0]
    clc_typcial.loc[index,"reg_ymd"] = exit_date

    clc_typcial.to_csv("../../../input/meta/clc_typical.csv", encoding="utf8",index=False,header=False)

    update_query = "update experdba.prov_data set reg_ymd = '{0}' where ctgry_nm = '통계청' and strg_filename = '{1}.csv'".format(exit_date, DATANAME)

    try:
        #  conn = psycopg2.connect(database="postgres",user="postgres",password="kopo",host="localhost",port="5432")
        conn = psycopg2.connect(database="experdb", user="experdb", password="experdb", host="172.16.0.153",
                                port="5432")
        cur = conn.cursor()

        cur.execute(update_query)
        #   cur.execute(del_query)
        conn.commit()
        print("execute success")
    except Exeception as e:
        print("database connection error")
        print(e)
    finally:
        if conn:
            conn.close()

# # 6. 적재를 위한 테이블 가공 및 적재

# In[36]:

data_tot_cnt = 0
if completed:
    columnNm = targetData.한글컬럼명.values[0].split(",")

    finalResultDf.columns = columnNm

    mergedDf = pd.DataFrame()

    if not org_data.empty:
        mergedDf = pd.concat([org_data, finalResultDf])
    else:
        mergedDf = pd.concat([org_data, finalResultDf])

    del org_data
    del finalResultDf
    gc.collect()

    mergedDf.reset_index(drop=True, inplace=True)

    cf.savedata(mergedDf, SITENAME, DATANAME, SERVICENAME)
    cf.saveparam(mergedDf, SITENAME, DATANAME, SERVICENAME)

    data_tot_cnt = len(mergedDf)
# 수집실패했을경우에도 기존 org 데이터의 건수정보는 total_cnt에 저장한다.
else:
    data_tot_cnt = len(org_data)

end_time = time.time()

try:
    engine = create_engine("postgresql://experdb:experdb@172.16.0.153:5432/experdb", encoding='utf8')

    conn_engine = engine.connect()

    if completed:
        exec_df = pd.DataFrame([{"site_name": SITENAME, "pg_name": DATANAME, "data_upt_cnt": data_chg_cnt,
                                 "data_tot_cnt": data_tot_cnt,
                                 "exec_date": datetime.fromtimestamp(end_time).strftime("%Y-%m-%d"),
                                 "start_time": datetime.fromtimestamp(starttime).strftime("%Y-%m-%d %H:%M:%S"),
                                 "end_time": datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                                 "exec_time": time.strftime('%H:%M:%S', time.gmtime(end_time - starttime)),
                                 "exec_yn": 'Y'}])
    else:
        exec_df = pd.DataFrame([{"site_name": SITENAME, "pg_name": DATANAME, "data_upt_cnt": data_chg_cnt,
                                 "data_tot_cnt": data_tot_cnt,
                                 "exec_date": datetime.fromtimestamp(end_time).strftime("%Y-%m-%d"),
                                 "start_time": datetime.fromtimestamp(starttime).strftime("%Y-%m-%d %H:%M:%S"),
                                 "end_time": datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S"),
                                 "exec_time": time.strftime('%H:%M:%S', time.gmtime(end_time - starttime)),
                                 "exec_yn": 'N'}])
    exec_df.to_sql("prov_stat", engine, if_exists="append", index=False)
except Exception as e:
    print(e)
else:
    conn_engine.close()





