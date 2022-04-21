import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup 
import pandas as pd
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote
import os
import time
import pickle

OUTPUTPATH="../output"
STDENCODING="utf-8"
### 함수정의: 사이트 메타정보를 받아 데이터를 수집 후 수집결과를 반환하는 함수
### 파마리터정의: 
###   - inurl: 메타정보의 "URL"컬럼값 (예: https://www.calspia.go.kr/io/openapi/cm/selectIoCmConstructionList.do )
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)
###   - inParam: 메타정보의 "파라미터 정보" (예: 페이지 파라미터 존재 시 1 값")
###   - inPageYn: 메타정보의 "페이지 정보" (예: 페이지 파라미터 존재 시 1 값")
### 함수정의: 사이트 메타정보를 받아 데이터를 수집 후 수집결과를 반환하는 함수
def scrapy(inUrl, inSiteName, inDataName, inServiceName, inParam, inPageYn, jsonkey="items", dummy=0, inType="jsonabnormal"):
    try:
        emptyPd = pd.DataFrame()
        i=1
        while True:
            time.sleep(1.2)
            print("{} page scraping start".format(i))
            
            if(inPageYn==1):
                inParam["pageNo"] = i
            
            queryParams = '?' + urlencode(inParam)
            response = requests.get(inUrl+queryParams)
            response.encoding=STDENCODING
            rowData = pd.DataFrame()
            print(rowData)
            if(inType=="jsonabnormal"):
                # 비정상 데이터는 response 섹션이 없음
                if(response.json().get('response') == None):
                    jsondata = response.json()["header"]["resultMsg"]
                    if( jsondata != "NORMAL_SERVICE"):
                        print("SERVER ERROR ",jsondata)
                        break

                jsondata = response.json()["response"]["body"][jsonkey]

                if( jsondata == []):
                    print("{} page is empty".format(i))
                    break

                if( jsonkey == "detail1"):
                    jsondata["index"]=[0]

                rowData = pd.DataFrame(jsondata)
            elif(inType=="jsonnormal"):
                # 공공데이터 포털등 일반 json 형태데이터인경우
                rowData = pd.read_json(inUrl+queryParams)
            else:
                rowData = pd.read_json(inUrl+queryParams)          
                
            emptyPd = emptyPd.append(rowData)

            if(inPageYn == 0):
                print("{} no pageNo".format(inPageYn))
                break
            i = i+1

        emptyPd.columns = emptyPd.columns.str.lower()
        emptyPd.shape
        print("dataframe{}, param:{} rows: {} completed".format(inDataName,inParam, emptyPd.shape[1] )     )
        return emptyPd       
    except Exception as e:
            print(e)     
### 함수정의: 사이트 메타정보를 받아 데이터를 수집 후 수집결과를 반환하는 함수 (★★TBD 추후 HDFS경로 및 메타정보로 컬럼 추가 필요!!★★)
### 파마리터정의: 
###   - directory: outputpath 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

### 함수정의: 데이터프레임을 OUTPUT PATH에 저장하는 함수
### 파마리터정의:  (★★TBD 추후 HDFS경로 및 메타정보로 컬럼 추가 필요!!★★)
###   - inDf: 저장할 대상 데이터프레임
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)

def savedata(inDf, inSiteName, inDataName, inServiceName, mode=2):
    # DATA SAVE TO THE OUTPUT PATH FOLDER
    outDir = os.path.join(OUTPUTPATH,inSiteName,inDataName)
    outFile = os.path.join( outDir, inServiceName) + ".csv"
    createFolder(outDir)
    if mode==1:
        inDf.to_csv(outFile, index=False, encoding="ms949",mode="a", header=False)
    else:
        inDf.to_csv(outFile, index=False, encoding="ms949")
    print("{} save compled".format(inDataName) )
    
### 함수정의: 파라미터 저장함수
###   - paramData: 저장된 데이터에 적용된 파라미터 정보 (org + new)
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)    
def saveparam(paramData, inSiteName, inDataName, inServiceName):
    # DATA SAVE TO THE OUTPUT PATH FOLDER
    outDir = os.path.join(OUTPUTPATH,inSiteName,inDataName)
    outPickle = os.path.join( outDir, inServiceName) + ".pickle"
    
    ### 피클 파일 저장하기 (바이너리) ###
    with open(outPickle,"wb") as fw:
        pickle.dump(paramData,fw)
        
### 함수정의: 파라미터 불러오는 
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)   
def loadparam(inSiteName, inDataName, inServiceName):
    # DATA SAVE TO THE OUTPUT PATH FOLDER
    outDir = os.path.join(OUTPUTPATH,inSiteName,inDataName)
    outPickle = os.path.join( outDir, inServiceName) + ".pickle"
    
    ### 피클 파일 불러오기 (바이너리) ###
    with open(outPickle,"rb") as fr:
        data = pickle.load(fr)
    return data

### 함수정의: 저장데이터 불러오는 함수
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)   
def loaddata(inSiteName, inDataName, inServiceName):
    # DATA SAVE TO THE OUTPUT PATH FOLDER
    outDir = os.path.join(OUTPUTPATH,inSiteName,inDataName)
    outData = os.path.join( outDir, inServiceName) + ".csv"
    
    ### 피클 파일 불러오기 (바이너리) ###
    data = pd.read_csv(outData)
    return data

# Calcuate Month Duration from given 2 Parameters.
# d1, d2 : datetime format 
# d1 >= d2
def calc_month(d1, d2):
    return (d1.year - d2.year) * 12 + (d1.month - d2.month + 1)