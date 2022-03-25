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
### 47.selectIoPtVEProposalList.ipynb : 설계VE 상세 VE제안목록
   - 김미경 작업
   - '설계VE 상세 VE제안목록' 요청 시 '설계VE 목록 조회'의 ptlcmno 값이 필요함
   - 48.selectIoPtVeBusinessList.ipynb 선 수행 필요
### 49.selectIoPtVeBusiness.ipynb : 설계VE 상세정보
   - 김미경 작업
   - '설계VE 상세정보' 요청 시 '설계VE 목록 조회'의 ptlcmno 값이 필요함
   - 48.selectIoPtVeBusinessList.ipynb 선 수행 필요
