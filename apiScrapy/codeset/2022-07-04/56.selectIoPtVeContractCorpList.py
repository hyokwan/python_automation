#!/usr/bin/env python
# coding: utf-8

# ### ** 포털공사관리번호 필요 ptlCmno (설계VE 목록 조회) 

# ### 1. 기본 수집정보 불러오기

# In[1]:

import subprocess
import os
import sys
os.chdir('/data/KITECH/apiScrapy/codeset/calspia/')
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname("./"))))
from common import commonFunc_03 as cf
import pandas as pd
import pickle
import os
import time
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine

pd.set_option('display.max_columns', None)
metadata = pd.read_excel("../../input/datalake_meta22.xlsx",engine="openpyxl")

SITENAME = "calspia"
DATANAME= "설계VE목록조회"
### APIKEY 불러오기 ###
with open("../../input/calsapikey.pickle","rb") as fr:
    APIKEY = pickle.load(fr)

targetData = metadata.loc[metadata.자료명==DATANAME]
preSetFolder = targetData["저장폴더"].values[0]

targetPath = targetData.저장폴더.values[0]

conList = pd.read_csv(targetPath, encoding="utf8")

ptlCmnoList = conList.공사관리번호.drop_duplicates().tolist()

#print(ptlCmnoList)

APIKEYLEN = len(APIKEY)

tot_cnt = 0
data_tot_cnt = 0

### 기본정보 설정 및 파라미터 설정 ###
SITENAME = "calspia"
DATANAME= "설계VE계약정보"

targetData = metadata.loc[metadata.자료명==DATANAME]
URL = targetData["URL"].values[0]
SERVICENAME = targetData["서비스키"].values[0]
SERVICENAME = SERVICENAME.split(".")[0]
REQPARAM = targetData["요청변수"].values[0]
REQPARAM = REQPARAM.split(",")
PRIMARYKEY = targetData["기본키"].values[0]
### 기본정보 설정 및 파라미터 설정 ###

columnNm = targetData.한글컬럼명.values[0].split(",")

breakPoint = 0

# 페이지번호 설정
PAGEYN=1
if REQPARAM.count("pageNo") == 0:
    PAGEYN = 0
else:
    PAGEYN = 1
### 기본정보 설정 및 파라미터 설정 ###

pageNo = 1
numOfRows = 1000
JSONKEY = "items"
DUMMY = 0

print("수집시작 : ", time.strftime('%c', time.localtime(time.time())))

newParam = ptlCmnoList.copy()

orgParam = []
try:
    # 기존 데이터 및 파라미터 정보 불러오기
    # 리스트로 불러오기로 변경 0425
    orgParam = cf.loadparam(SITENAME,DATANAME,SERVICENAME)
    # outData = cf.loaddata(SITENAME,DATANAME,SERVICENAME)
## 파일이 없는경우
except Exception as e:
    orgParam = []
    print(e)

ptlCmnoList = list( set(newParam) - set(orgParam) )
# 모드: 0=종료 1=append 2=새로생성
mode = 2
print(len(ptlCmnoList))
# 업데이트 할 내용이 없으면 종료
if ptlCmnoList == []:
    mode = 0
    print("{} 정보 quit모드 {} ".format(DATANAME, mode))
  #  quit()
# orgParam == []
elif orgParam == []:
    mode = 2
    print("{} 정보 new 모드 {} ".format(DATANAME, mode))
# 이외에는 append 모드
else:
    mode = 1
    print("{} 정보 append 모드 {} ".format(DATANAME, mode))

starttime = time.time()

### 개별 코드 작업 영역 ###
### baseparam은 수동설정필요

ptlCmnoListLen = len(ptlCmnoList)
pageList = [] 

APICALL = 0
resultDfMerged = pd.DataFrame()

for i in range(0, ptlCmnoListLen):
    BASEPARAM={"serviceKey":APIKEY[0], "type":"json", "ptlCmno": ptlCmnoList[i]} #변경 apiNo -> 0
    # scrapyResult = cf.scrapy(URL,SITENAME,DATANAME,SERVICENAME,BASEPARAM,PAGEYN)
    scrapyResult = cf.scrapy(URL,SITENAME,DATANAME,SERVICENAME,BASEPARAM,PAGEYN,APIKEY,APICALL) #추가
    resultDf = scrapyResult[0]
    pageList.append( scrapyResult[1] )
    APICALL = scrapyResult[2]  #추가
    if resultDf.empty: # 정상 데이터가 없는 경우
        print("No Data")
    else:
        resultDfMerged = resultDfMerged.append(resultDf) 

Df = pd.DataFrame({"계약정보사업자등록번호내용":['711021-1079411']})

Df = Df[Df.계약정보사업자등록번호내용 != '711021-1079411']

data_tot_cnt = len(resultDfMerged)

dataEx = True 
if resultDfMerged.empty:
    dataEx = False

if dataEx: 
    resultDfMerged.columns = columnNm

completed = True
data_chg_cnt = len(resultDfMerged)
print("수집 종료 : ", time.time()-starttime)


data_tot_cnt = data_chg_cnt
if dataEx:
    cf.savedata(resultDfMerged, SITENAME,DATANAME,SERVICENAME,mode=mode)
else:
    org_df = cf.loaddata(SITENAME, DATANAME, SERVICENAME)
    print(org_df)
    data_tot_cnt = len(org_df)
    cf.savedata(org_df, SITENAME,DATANAME,SERVICENAME)

if dataEx:
# 기존사용된 파라미터 정보에 추가 파라미터 append 후 저장
    ptlCmnoList = orgParam + ptlCmnoList
    # 최종 파라미터 저장
    print(ptlCmnoList)
    cf.saveparam(ptlCmnoList, SITENAME,DATANAME,SERVICENAME)
else:
    cf.saveparam(newParam, SITENAME,DATANAME,SERVICENAME)

AA = pd.read_csv('/data/KITECH/input/calspia/설계VE계약정보.csv', encoding='utf8')
print("AA")
print(AA)
# # 5. 수집 종료일자 업데이트

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

    index = clc_typcial[(clc_typcial.ctgry_nm == "건설사업정보시스템") & (clc_typcial.strg_filename == f'{DATANAME}.csv')].index.values[0]
    clc_typcial.loc[index,"reg_ymd"] = exit_date

    clc_typcial.to_csv("../../../input/meta/clc_typical.csv", encoding="utf8",index=False,header=False)

    update_query = "update experdba.prov_data set reg_ymd = '{0}' where ctgry_nm = '건설사업정보시스템' and strg_filename = '{1}.csv'".format(exit_date, DATANAME)

    
# 하둡
    subprocess.call(["sh","/data/KITECH/shell/calspia/hdfs_cals_56.sh"])
        
    try:
        #         conn = psycopg2.connect(database="postgres",user="postgres",password="kopo",host="localhost",port="5432")
        conn = psycopg2.connect(database="experdb", user="experdb", password="Tjfcl!.12", host="10.11.21.27",port="5432")
        cur = conn.cursor()

        cur.execute(update_query)
        #         cur.execute(del_query)
        conn.commit()
        print("execute success")
    except Exeception as e:
        print("database connection error")
        print(e)
    finally:
        if conn:
            conn.close()

# # 6. 적재를 위한 테이블 가공 및 적재


end_time = time.time()

try:
    engine = create_engine("postgresql://experdb:Tjfcl!.12@10.11.21.27:5432/experdb", encoding='utf8')

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

