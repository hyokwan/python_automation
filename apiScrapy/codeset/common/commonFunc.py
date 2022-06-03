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

total_count = 0
### 함수정의: 사이트 메타정보를 받아 데이터를 수집 후 수집결과를 반환하는 함수
### 파마리터정의: 
###   - inurl: 메타정보의 "URL"컬럼값 (예: https://www.calspia.go.kr/io/openapi/cm/selectIoCmConstructionList.do )
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)
###   - inParam: 메타정보의 "파라미터 정보" (예: 페이지 파라미터 존재 시 1 값")
###   - inPageYn: 메타정보의 "페이지 정보" (예: 페이지 파라미터 존재 시 1 값")
### 함수정의: 사이트 메타정보를 받아 데이터를 수집 후 수집결과를 반환하는 함수
def scrapy(inUrl, inSiteName, inDataName, inServiceName, inParam, inPageYn, inAPIKey, inApiCall, jsonkey="items", dummy=0, inType="jsonabnormal", prePageNo=1):
    try:
        emptyPd = pd.DataFrame()
        i=prePageNo
        inAPIKeyLen = len(inAPIKey)
        while True:
            inApiCall = inApiCall + 1
            if inType == "jsonabnormal":
                time.sleep(1)
                
                inParam["serviceKey"] = inAPIKey[inApiCall%inAPIKeyLen]
                print("{} page scraping start apicall iter: {} / used {}".format(i,inApiCall,inParam["serviceKey"]))
            if(inPageYn==1):
                inParam["pageNo"] = i
            else:
                inParam["pageNo"] = prePageNo
            
            queryParams = '?' + urlencode(inParam)
            response = requests.get(inUrl+queryParams)
            response.encoding=STDENCODING
            # print(inUrl+queryParams)
            rowData = pd.DataFrame()
            print(inUrl+queryParams)
            
            global total_count

            if (inType == "jsonabnormal"):  # 건설사업정보시스템인 경우
                # 비정상 데이터는 response 섹션이 없음
                if (response.json().get('response') == None):  # response 데이터 중 response 가 없는 경우
                    jsondata = response.json()["header"]["resultMsg"]  # resultMsg 저장
                    if (jsondata != "NORMAL_SERVICE"):  # resultMsg 가 NORMAL_SERVICE가 아닌 경우
                        print("SERVER ERROR ", jsondata)  # 에러 메시지 출력
                        break
                if jsonkey == "items":
                    jsondata = response.json()["response"]["body"][jsonkey] 
                elif jsonkey == "detailList":
                    jsondata = []
                elif jsonkey == "detail1":
                    jsondata = []    
                # jsondata = response.json()["response"]["body"][jsonkey]

                if( jsondata == [] and jsonkey == "items"):
                    print("{} page is empty".format(i))
                    break
                # if( jsonkey == "detail1"):
                #     jsondata["index"]=[0]
                
                if jsonkey == "items":
                    if type(jsondata) == dict:
                        rowData = pd.DataFrame([jsondata])  # JSON 타입의 데이터를 DATAFRAME 형태로 변경 (items 데이터)
                    else:
                        rowData = pd.DataFrame(jsondata)  # JSON 타입의 데이터를 DATAFRAME 형태로 변경 (items 데이터)

                # rowData.rename(columns={'현장번호':'현장번호_d'}, inplace=True)
                detailList = []
                detailList2 = []

                if (i == 1):
                    print("totalCount " + str(response.json()["response"]["body"]["totalCount"]))
                    total_count = int(response.json()["response"]["body"]["totalCount"])
                if (0 < int(response.json()["response"]["body"]["totalCount"])):
                    if (response.json()["response"]["body"].get('detail1') != None):
                        print("we have a data on detail1")
                        detailList.append(pd.DataFrame([response.json()["response"]["body"]["detail1"]]))
                    if (response.json()["response"]["body"].get('detail2') != None):
                        detailList.append(pd.DataFrame([response.json()["response"]["body"]["detail2"]]))
                        print("we have a data on detail2")
                    if (response.json()["response"]["body"].get('detail3') != None):
                        detailList.append(pd.DataFrame([response.json()["response"]["body"]["detail3"]]))
                        print("we have a data on detail3")
                    if (response.json()["response"]["body"].get('detail4') != None):
                        detailList.append(pd.DataFrame([response.json()["response"]["body"]["detail4"]]))
                        print("we have a data on detail4")
                    if (response.json()["response"]["body"].get('detail5') != None):
                        detailList.append(pd.DataFrame([response.json()["response"]["body"]["detail5"]]))
                        print("we have a data on detail5")
                    # print(detailList)

                    if (response.json()["response"]["body"].get('detailList1') != []):
                        print("we have a data on detailList1")
                        detailList2.append(pd.DataFrame([response.json()["response"]["body"]["detailList1"]]))
                    if (response.json()["response"]["body"].get('detailList2') != []):
                        detailList2.append(pd.DataFrame([response.json()["response"]["body"]["detailList2"]]))
                        print("we have a data on detailList2")
                    if (response.json()["response"]["body"].get('detailList3') != []):
                        detailList2.append(pd.DataFrame([response.json()["response"]["body"]["detailList3"]]))
                        print("we have a data on detailList3")
                    if (response.json()["response"]["body"].get('detailList4') != []):
                        detailList2.append(pd.DataFrame([response.json()["response"]["body"]["detailList4"]]))
                        print("we have a data on detailList4")
                    if (response.json()["response"]["body"].get('detailList5') != []):
                        detailList2.append(pd.DataFrame([response.json()["response"]["body"]["detailList5"]]))
                        print("we have a data on detailList5")

                    detailDf = pd.DataFrame()
                    detail2Df = pd.DataFrame()

                    if len(detailList) > 1:
                        detailDf = pd.concat(detailList, axis=1)
                    elif len(detailList) == 1:
                        detailDf = detailList[0]

                    if len(detailList2) > 1:
                        detail2Df = pd.concat(detailList2, axis=1)
                    elif len(detailList2) == 1:
                        detail2Df = detailList2[0]

                  
                    detailCol = detailDf.columns.values.tolist()
                    
                    detail2Col = []
                    if jsonkey == "items":
                        detail2Col = detail2Df.columns.values.tolist()

                    detailTotCol = detailCol + detail2Col
                    
                    for each in rowData.columns:
                        if each in detailTotCol:
                            rowData.rename(columns={each:each+"_d"}, inplace=True)
		
                    if jsonkey == "items":
                        rowData = pd.concat([detailDf, detail2Df, rowData], axis=1)
                    elif jsonkey == "detailList":
                        rowData = pd.concat([detailDf, detail2Df], axis=1)
            
                    rowData[detailTotCol] = rowData[detailTotCol].fillna(method="ffill")
                    # print(rowData[detailTotCol])
                    
            elif(inType=="jsonnormal"):
                # 공공데이터 포털등 일반 json 형태데이터인경우
                try:
                    jsondata = response.json()
                except Exception as e:
                    xmlobj = BeautifulSoup(response.text,"lxml-xml")
                    errorCode = xmlobj.find("returnReasonCode").text
                    raise Exception(errorCode)
                else:
                    respCode = jsondata["response"]["header"]["resultCode"]

                    if respCode == "00" and jsondata["response"]["body"]["totalCount"] != 0: 
                        if jsonkey == "items":
                            rowData = pd.DataFrame(jsondata["response"]["body"][jsonkey])
                        elif jsonkey == "item":
                            rowData = pd.DataFrame(jsondata["response"]["body"]["items"][jsonkey])
                        if i == 1:
                            total_count = int(jsondata["response"]["body"]["totalCount"])
                            print(total_count)
                    else:
                        print(respCode)
                        break

                    if type(rowData) == list and rowData == []:
                        print("{} page is empty".format(i))
                        break
                    elif rowData.empty:
                        print("{} page is empty".format(i))
                        break

                if inDataName == "데이터셋개방표준에따른입찰공고정보":
                    rowData = rowData.loc[(rowData.bsnsDivNm == "공사") | (rowData.bsnsDivNm == "용역")]
                    
            elif inType == "xml":
                # xml 형태 데이터인 경우
                try:
                    xmlobj = BeautifulSoup(response.text, "lxml-xml")
                except:
                    time.sleep(5)
                    response = requests.get(inUrl + queryParams)
                    xmlobj = BeautifulSoup(response.text, "lxml-xml")
                try:
                    if xmlobj.find("totalCount").text == '0' or int(xmlobj.find("totalCount").text) <= (i-1) * 999:
                        print("No Data")
                        break
                except:
                    errorCode = xmlobj.find("returnReasonCode").text
                    raise Exception(errorCode)

                rowDataList = xmlobj.find_all(jsonkey)

                colList = [each.name for each in rowDataList[0].find_all()]

                totalList = []
                for eachList in rowDataList:
                    rowDict = {}
                    eachData = eachList.find_all()
                    for each in eachData:
                        rowDict[each.name] = each.text
                    dupCheck = set(colList) - set([each.name for each in eachData])
                    if len(dupCheck) != 0:
                        for eachCol in dupCheck:
                            rowDict[eachCol] = ""
                    totalList.append(rowDict)

                rowData = pd.DataFrame(totalList)
                
                if rowData.empty:
                    print("{} page is empty".format(i))
                    break
            else:
                rowData = pd.read_json(inUrl+queryParams)          
                
            emptyPd = emptyPd.append(rowData)
            # print(emptyPd)
            
            if(inPageYn == 0):
                print("{} no pageNo".format(inPageYn))
                break
#            print(i)
            i = i+1
        if inType=="jsonabnormal":
            emptyPd.columns = emptyPd.columns.str.lower()
        emptyPd.shape
        # print("dataframe{}, param:{} rows: {} completed".format(inDataName, inParam, emptyPd.shape[1]))
        return [emptyPd, i, inApiCall, total_count]
    except Exception as e:
            print(e)
            if inType=="jsonnormal" or inType=="xml":
                raise Exception(e.args[0])
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
    global OUTPUTPATH
    if inSiteName == "pps" or inSiteName == "kostat":
        OUTPUTPATH = "../../output"
    outDir = os.path.join(OUTPUTPATH,inSiteName)
    outFile = os.path.join(outDir, inDataName) + ".csv"
    createFolder(outDir)
    if mode==1:
        inDf.to_csv(outFile, index=False, encoding="utf8",mode="a", header=False)
    else:
        inDf.to_csv(outFile, index=False, encoding="utf8")
    print("{} save compled".format(inDataName) )
    
### 함수정의: 파라미터 저장함수
###   - paramData: 저장된 데이터에 적용된 파라미터 정보 (org + new)
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)    
def saveparam(paramData, inSiteName, inDataName, inServiceName):
    # DATA SAVE TO THE OUTPUT PATH FOLDER
    outDir = os.path.join(OUTPUTPATH,inSiteName)
    outPickle = os.path.join( outDir,inDataName) + ".pickle"
    
    ### 피클 파일 저장하기 (바이너리) ###
    with open(outPickle,"wb") as fw:
        pickle.dump(paramData,fw)
        
### 함수정의: 파라미터 불러오는 함수
###   - inSiteName: 메타정보의 "자료대상" (예: 건설사업정보시스템)
###   - inDataName: 메타정보의 "자료명" (예: 공사정보 목록)
###   - inServiceName: 메타정보의 "기본키" (예: serviceKey + Format)   
def loadparam(inSiteName, inDataName, inServiceName):
    # DATA SAVE TO THE OUTPUT PATH FOLDER
    outDir = os.path.join(OUTPUTPATH,inSiteName)
    outPickle = os.path.join( outDir, inDataName) + ".pickle"
    
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
    outDir = os.path.join(OUTPUTPATH,inSiteName)
    outData = os.path.join( outDir,inDataName) + ".csv"
    
    ### 피클 파일 불러오기 (바이너리) ###
    data = pd.read_csv(outData)
    return data
# Calcuate Month Duration from given 2 Parameters.
# d1, d2 : datetime format 
# d1 >= d2
def calc_month(d1, d2):
    return (d1.year - d2.year) * 12 + (d1.month - d2.month + 1)
