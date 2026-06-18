# ============================================================
# 서울시 상권분석서비스(추정매출-상권) 2025년 분석
#
# 분석 질문:
# "어떤 업종이 어떤 상권에서 잘되는가?"
#
# 사용 범위
# - ComPhy-1-Python:
#   open(), while, for, if, list, dictionary, function, sort()
# - ComPhy-3-Matplotlib:
#   plt.subplots(), ax.bar(), ax.plot(), ax.legend()
#
# 사용하지 않음:
# pandas, seaborn, scikit-learn, tensorflow 등
# ============================================================

import matplotlib.pyplot as plt


# ============================================================
# 0. 파일 이름 설정
# ============================================================

DATA_FILE = "서울시 상권분석서비스(추정매출-상권)_2025년.csv"


# ============================================================
# 1. CSV 파일 읽기
#
# 파일은 cp949 인코딩이다.
# 한 줄씩 읽어서 상권-업종별로 매출을 누적한다.
# ============================================================

pair_data = {}
line_count = 0

with open(DATA_FILE, encoding="cp949") as fp:

    # 첫 줄은 컬럼명
    header_line = fp.readline()
    header = header_line.strip()[1:-1].split('","')

    # 두 번째 줄부터 실제 데이터
    line = fp.readline()

    while line:

        # CSV 한 줄을 리스트로 변환
        row = line.strip()[1:-1].split('","')

        # ----------------------------------------------------
        # CSV의 필요한 열만 사용
        # ----------------------------------------------------
        quarter_code = row[0]       # 기준_년분기_코드
        market_type = row[2]        # 상권_구분_코드_명
        market_code = row[3]        # 상권_코드
        market_name = row[4]        # 상권_코드_명
        industry_code = row[5]      # 서비스_업종_코드
        industry_name = row[6]      # 서비스_업종_코드_명
        sales = int(row[7])         # 당월_매출_금액
        transactions = int(row[8])  # 당월_매출_건수

        # 예: 20251 -> 마지막 숫자 1은 1분기
        quarter_number = int(quarter_code[-1])

        # 상권유형 + 상권코드 + 업종코드를 하나의 key로 설정
        pair_key = market_type + "|" + market_code + "|" + industry_code

        # 처음 나온 상권-업종 조합이면 리스트 생성
        if pair_key not in pair_data:

            # 리스트 구조
            # [0] 상권유형
            # [1] 상권코드
            # [2] 상권명
            # [3] 업종코드
            # [4] 업종명
            # [5] 연간 누적 매출액
            # [6] 연간 누적 매출건수
            # [7] 1분기 매출
            # [8] 2분기 매출
            # [9] 3분기 매출
            # [10] 4분기 매출
            # [11] 데이터가 존재하는 분기 수

            pair_data[pair_key] = [
                market_type,
                market_code,
                market_name,
                industry_code,
                industry_name,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ]

        # 연간 매출액 누적
        pair_data[pair_key][5] = pair_data[pair_key][5] + sales

        # 연간 매출건수 누적
        pair_data[pair_key][6] = pair_data[pair_key][6] + transactions

        # 분기별 매출 누적
        pair_data[pair_key][6 + quarter_number] = \
            pair_data[pair_key][6 + quarter_number] + sales

        # 몇 개 분기가 존재하는지 확인
        pair_data[pair_key][11] = pair_data[pair_key][11] + 1

        line_count = line_count + 1
        line = fp.readline()


print("====================================================")
print("CSV 읽기 완료")
print("읽은 데이터 행 수 =", line_count)
print("상권-업종 조합 수 =", len(pair_data))
print("====================================================")


# ============================================================
# 2. Dictionary를 List로 변환
#
# 정렬을 위해 dictionary 값을 리스트에 넣는다.
# ============================================================

records = []

for pair_key in pair_data:
    records.append(pair_data[pair_key])


# ============================================================
# 3. 특정 상권유형에서 매출이 큰 상권-업종 조합 찾기
# ============================================================

def top_records_in_type(records, target_type, number_of_records):

    selected = []

    for record in records:

        if record[0] == target_type:

            # 정렬을 위해 연간 매출액을 맨 앞에 둔다.
            selected.append([
                record[5],   # 연간 매출
                record[6],   # 연간 매출건수
                record[0],   # 상권유형
                record[2],   # 상권명
                record[4],   # 업종명
                record[7],   # 1분기
                record[8],   # 2분기
                record[9],   # 3분기
                record[10],  # 4분기
                record[11]   # 존재하는 분기 수
            ])

    # 매출액 기준 오름차순 정렬
    selected.sort()

    # 뒤에서부터 상위 N개 선택
    selected = selected[-number_of_records:]

    # 내림차순으로 뒤집기
    selected = selected[::-1]

    return selected


# ============================================================
# 4. 상권유형별 단순 매출 Top 5 출력
# ============================================================

market_types = [
    "발달상권",
    "전통시장",
    "관광특구",
    "골목상권"
]

print("\n")
print("====================================================")
print("상권유형별 연간 누적 매출 Top 5")
print("====================================================")

for market_type in market_types:

    top5 = top_records_in_type(records, market_type, 5)

    print("\n[" + market_type + "]")

    rank = 1

    for item in top5:

        annual_sales_billion = item[0] / 1000000000.0
        average_ticket = item[0] / item[1]

        print(
            str(rank) + ". "
            + item[3]
            + " / "
            + item[4]
            + " : "
            + str(round(annual_sales_billion, 1))
            + " billion KRW"
            + ", 거래건수 = "
            + str(item[1])
            + ", 건당 매출 = "
            + str(round(average_ticket))
            + " KRW"
        )

        rank = rank + 1


# ============================================================
# 5. LQ(Location Quotient, 상권특화도) 계산 준비
#
# LQ =
# (특정 상권 안에서 특정 업종의 매출 비중)
# /
# (같은 상권유형 전체에서 해당 업종의 매출 비중)
#
# LQ > 1 이면 해당 상권에서 평균보다 특화된 업종
# LQ >= 1.5 이면 특화도가 꽤 높은 업종으로 판단
# ============================================================

market_total = {}
industry_total = {}
type_total = {}


for record in records:

    market_key = record[0] + "|" + record[1]
    industry_key = record[0] + "|" + record[3]
    market_type = record[0]
    annual_sales = record[5]

    # 상권 전체 매출
    if market_key not in market_total:
        market_total[market_key] = 0

    # 상권유형별 업종 전체 매출
    if industry_key not in industry_total:
        industry_total[industry_key] = 0

    # 상권유형 전체 매출
    if market_type not in type_total:
        type_total[market_type] = 0

    market_total[market_key] = market_total[market_key] + annual_sales
    industry_total[industry_key] = industry_total[industry_key] + annual_sales
    type_total[market_type] = type_total[market_type] + annual_sales


# ============================================================
# 6. 상권유형별 상위 10% 매출 기준 계산
#
# 상권유형마다 매출 규모가 다르기 때문에
# 전체 데이터가 아니라 각 유형 안에서 상위 10%를 계산한다.
# ============================================================

sales_by_type = {}

for record in records:

    market_type = record[0]

    if market_type not in sales_by_type:
        sales_by_type[market_type] = []

    sales_by_type[market_type].append(record[5])


sales_threshold = {}

for market_type in sales_by_type:

    sales_by_type[market_type].sort()

    position = int(len(sales_by_type[market_type]) * 0.90)

    sales_threshold[market_type] = \
        sales_by_type[market_type][position]


# ============================================================
# 7. "잘되는 업종" 판단 기준
#
# 아래 4개 조건을 모두 만족하면 strong_fit에 저장
#
# 1) 같은 상권유형 안에서 매출 상위 10%
# 2) LQ >= 1.5
# 3) 1~4분기 데이터가 모두 존재
# 4) 분기별 변동계수(CV) <= 0.35
#
# CV가 너무 높으면 특정 분기에만 매출이 튄 것으로 판단
# ============================================================

strong_fit = []

for record in records:

    market_type = record[0]

    market_key = record[0] + "|" + record[1]
    industry_key = record[0] + "|" + record[3]

    annual_sales = record[5]
    annual_transactions = record[6]

    q1 = record[7]
    q2 = record[8]
    q3 = record[9]
    q4 = record[10]

    reported_quarters = record[11]

    # 해당 상권에서 해당 업종이 차지하는 매출 비중
    market_share = annual_sales / market_total[market_key]

    # 같은 상권유형 전체에서 해당 업종이 차지하는 매출 비중
    industry_share = industry_total[industry_key] / type_total[market_type]

    # 상권특화도 LQ
    lq = market_share / industry_share

    # 분기 평균
    quarterly_average = (q1 + q2 + q3 + q4) / 4.0

    # 분기별 분산
    quarterly_variance = (
        (q1 - quarterly_average) ** 2
        + (q2 - quarterly_average) ** 2
        + (q3 - quarterly_average) ** 2
        + (q4 - quarterly_average) ** 2
    ) / 4.0

    # 표준편차
    quarterly_standard_deviation = quarterly_variance ** 0.5

    # 변동계수 CV
    coefficient_of_variation = \
        quarterly_standard_deviation / quarterly_average

    # 1분기 대비 4분기 매출 변화율
    if q1 == 0:
        q1_to_q4_change = 0
    else:
        q1_to_q4_change = (q4 - q1) / q1

    # 잘되는 업종 조건
    if annual_sales >= sales_threshold[market_type] \
       and lq >= 1.5 \
       and reported_quarters == 4 \
       and coefficient_of_variation <= 0.35:

        strong_fit.append([
            annual_sales,
            lq,
            coefficient_of_variation,
            q1_to_q4_change,
            market_type,
            record[2],
            record[4],
            annual_transactions,
            q1,
            q2,
            q3,
            q4
        ])


# ============================================================
# 8. 상권유형별 "잘되는 상권-업종 조합" 출력
# ============================================================

print("\n")
print("====================================================")
print("상권유형별 강한 상권-업종 조합")
print("조건: 매출 상위 10%, LQ >= 1.5, CV <= 0.35")
print("====================================================")

for market_type in market_types:

    selected = []

    for item in strong_fit:

        if item[4] == market_type:
            selected.append(item)

    # 매출액을 기준으로 정렬
    selected.sort()

    # 상위 10개
    selected = selected[-10:]

    # 내림차순으로 변경
    selected = selected[::-1]

    print("\n[" + market_type + "]")

    rank = 1

    for item in selected:

        annual_sales_billion = item[0] / 1000000000.0

        print(
            str(rank) + ". "
            + item[5]
            + " / "
            + item[6]
            + " : "
            + str(round(annual_sales_billion, 1))
            + " billion KRW"
            + " | LQ = "
            + str(round(item[1], 2))
            + " | CV = "
            + str(round(item[2], 2))
            + " | Q1 to Q4 = "
            + str(round(item[3] * 100.0, 1))
            + "%"
        )

        rank = rank + 1


# ============================================================
# 9. 그래프 1
#
# 발달상권에서 연간 매출이 가장 큰 상위 5개
# ============================================================

selected_type = "발달상권"

top5 = top_records_in_type(records, selected_type, 5)

labels = []
values = []

rank = 1

for item in top5:

    labels.append("Rank " + str(rank))
    values.append(item[0] / 1000000000.0)

    rank = rank + 1


fig, ax = plt.subplots(figsize=(8, 4.5))

ax.bar(labels, values)

ax.set_title("Top 5 annual-sales pairs: commercial districts")
ax.set_xlabel("Market-industry ranking")
ax.set_ylabel("2025 cumulative sales (billion KRW)")

plt.show()


# ============================================================
# 10. 그래프 2
#
# 위 상위 5개 상권-업종의 분기별 매출 변화
# ============================================================

quarters = ["Q1", "Q2", "Q3", "Q4"]

fig, ax = plt.subplots(figsize=(8, 4.5))

rank = 1

for item in top5:

    q_sales = [
        item[5] / 1000000000.0,
        item[6] / 1000000000.0,
        item[7] / 1000000000.0,
        item[8] / 1000000000.0
    ]

    ax.plot(
        quarters,
        q_sales,
        label="Rank " + str(rank)
    )

    rank = rank + 1


ax.set_title("Quarterly sales trend: top commercial-district pairs")
ax.set_xlabel("Quarter")
ax.set_ylabel("Sales (billion KRW)")
ax.legend()

plt.show()
