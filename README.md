# python_automation
automation

# 수행 순서
### 01.ConstructionList.ipynb 실행 : 공사정보 목록
### 09.ProjConstYearContractList.ipynb : 연도별 공사계약 목록
### 02.AcpsRprtList.ipynb : 기성정보 현황
   - '기성정보 현황' 요청시 '연도별 공사계약 목록'의 sptno, sptto 정보를 사용해야 함
   - 09.ProjConstYearContractList.ipynb를 선 수행하여 selectIoCmProjConstYearContractList.csv 파일을 output에 생성해야 함
### 03.QltPlnList.ipynb : 품질계획 현황
   - 첫 요청시 rprtYm(보고년월 YYYYMM) 파라미터를 공백으로 전달하면, stwrDt(착공일자)과 ccwDt(준공일자)를 받을 수 있다.
   - 착공일자와 준공일자를 기준으로 rprtYm(보고년월) 파라미터 정보로 반복 전달하여 정보를 수신한다.  
   - respose.body.totalcount = 0 이면, 세부 데이터가 없는 상태로 respose.body.detail1 데이터만 수집하고 보고년월을 반복하여 호출할 필요 없음
     (예> C2004186, 200802 -> 보고년월을 순차 증가하여 호출해도 무의미 동일 중복데이터만 수신됨)
   - respose.body.totalcount != 0 이면, 세부 데이터가 있음. 데이터는 response.body.detailList1 ~ 5 중에 임의의 리스트에 들어오므로 보고년월을 순차 반복 호출한다.
     (예> C2016001, 201512 는 detailList1에 데이터가 있고, C2016001, 202101는 detailList3에 데이터가 있음)
### 19.selectIoFmMngList.ipynb : 시설물 목록
   - 총 7913개의 시설물 목록이 존재함. 요청시 pageNo: 1, numOfRows: 1000개로 요청하여 남은 목록 수를 계산하여 pageNo를 증가시키면서 반복 호출한다.
   - 이 요청으로 시설물번호(fcno) 정보를 획득할 수 있음 (시설물 관련 타 요청의 필수 키 값임)
### 20.selectIoFmSpcfDtl.ipynb : 시설물 기본제원
   - 20.selectIoFmSpcfDtl.ipynb를 선 수행하여 시설물번호(fcno) 정보를 획득해야 함
   - 응답의 기본정보는 detail1에, 나머지 상세 정보는 detail2에 들어온다.(교량, 터널, 지하차도 동일)
   - 진행 공정으로 보이는 시설물은 DB 에러로 응답이 온다. (fcno : 0175BC91115A1F7F439D3EFD3512381A)
   - 기본 정보 + (교량|터널|지하차도) 조합에 따라 응답 칼럼이 달라지므로, 결과 DataFrame은 모든 칼럼을 미리 선언하여 모든 조합을 수용가능하도록 선언해야 한다.
### 21.selectIoFmChckDinsPlnList.ipynb : 시설물 점검진단계획 목록
   - 20.selectIoFmSpcfDtl.ipynb를 선 수행하여 시설물번호(fcno) 정보를 획득해야 함
   - 응답의 기본정보는 detail1에, 시설물 점검진단계획목록 정보는 response.body.items에 N건 존재
   - 상기 N건 : response.body.totlaCount 만큼 존재, 잔여 목록 수를 계산하여 pageNo++하여 반복 호출한다.
     * 사양서에는 pageNo가 없으나 req param에 전달/호출 가능
### 26.selectIoLcAlRwList.ipynb : 설계VE 목록 조회
   - 이상민 작업
   - 기본키 : serviceKey(인증키), searchSrYr1(기준년도), searchSrYr2(전년도), searchSrYr3(전전년도)
     * 특이사항 : searchSrYr1(기준년도), searchSrYr2(전년도), searchSrYr3(전전년도)에 대한 값 미제공으로 인한 코드상 입력 필요 (형식 YYYY)

### 48.selectIoPtVeBusinessList.ipynb : 설계VE 목록 조회
   - 김미경 작업
### 46.selectIoPtVeBusiness.ipynb : 설계VE 상세 검토조직 조회
   - 김미경 작업
   - '설계VE 상세 검토조직 조회' 요청 시 '설계VE 목록 조회'의 ptlcmno 값이 필요함
   - 48.selectIoPtVeBusinessList.ipynb 선 수행 필요
