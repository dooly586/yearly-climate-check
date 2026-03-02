import streamlit as st
import requests
import pandas as pd
import os
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide", page_title="기온 비교 대시보드")
st.title("🌡️ 연도별 지정 기간 기온 비교 대시보드")

# 인증키 로딩 우선순위: .env → st.secrets → 사이드바 직접 입력
auth_key = os.getenv("KMA_AUTH_KEY", "")
if not auth_key:
    try:
        auth_key = st.secrets["KMA_AUTH_KEY"]
    except Exception:
        auth_key = ""

# ─── 전체 지상관측 지점 데이터 ───────────────────
STATIONS = pd.DataFrame([
    (90,"속초","Sokcho",38.25085,128.56473,"강원도"),
    (93,"북춘천","Bukchuncheon",37.94738,127.75443,"강원도"),
    (95,"철원","Cheorwon",38.14787,127.30420,"강원도"),
    (98,"동두천","Dongducheon",37.90188,127.06070,"경기도"),
    (99,"파주","Paju",37.88589,126.76648,"경기도"),
    (100,"대관령","Daegwallyeong",37.67713,128.71834,"강원도"),
    (101,"춘천","Chuncheon",37.90262,127.73570,"강원도"),
    (102,"백령도","Baengnyeongdo",37.97396,124.71237,"인천"),
    (104,"북강릉","Bukgangneung",37.80456,128.85535,"강원도"),
    (105,"강릉","Gangneung",37.75147,128.89099,"강원도"),
    (106,"동해","Donghae",37.50709,129.12433,"강원도"),
    (108,"서울","Seoul",37.57142,126.96580,"서울"),
    (112,"인천","Incheon",37.47772,126.62490,"인천"),
    (114,"원주","Wonju",37.33749,127.94659,"강원도"),
    (115,"울릉도","Ulleungdo",37.48129,130.89863,"경북"),
    (119,"수원","Suwon",37.25746,126.98300,"경기도"),
    (121,"영월","Yeongwol",37.18126,128.45743,"강원도"),
    (127,"충주","Chungju",36.97045,127.95250,"충북"),
    (129,"서산","Seosan",36.77658,126.49390,"충남"),
    (130,"울진","Uljin",36.99176,129.41278,"경북"),
    (131,"청주","Cheongju",36.63924,127.44066,"충북"),
    (133,"대전","Daejeon",36.37199,127.37210,"대전"),
    (135,"추풍령","Chupungnyeong",36.22025,127.99458,"충북"),
    (136,"안동","Andong",36.57293,128.70733,"경북"),
    (137,"상주","Sangju",36.40837,128.15741,"경북"),
    (138,"포항","Pohang",36.03201,129.38002,"경북"),
    (140,"군산","Gunsan",36.00530,126.76135,"전북"),
    (143,"대구","Daegu",35.87797,128.65296,"대구"),
    (146,"전주","Jeonju",35.84092,127.11718,"전북"),
    (152,"울산","Ulsan",35.58237,129.33469,"울산"),
    (155,"창원","Changwon",35.17019,128.57282,"경남"),
    (156,"광주","Gwangju",35.17294,126.89156,"광주"),
    (159,"부산","Busan",35.10468,129.03203,"부산"),
    (162,"통영","Tongyeong",34.84541,128.43561,"경남"),
    (165,"목포","Mokpo",34.81732,126.38151,"전남"),
    (168,"여수","Yeosu",34.73929,127.74063,"전남"),
    (169,"흑산도","Heuksando",34.68719,125.45105,"전남"),
    (170,"완도","Wando",34.39590,126.70182,"전남"),
    (172,"고창","Gochang",35.34824,126.59900,"전북"),
    (174,"순천","Suncheon",35.02040,127.36940,"전남"),
    (177,"홍성","Hongseong",36.65759,126.68772,"충남"),
    (184,"제주","Jeju",33.51411,126.52969,"제주"),
    (185,"고산","Gosan",33.29382,126.16283,"제주"),
    (188,"성산","Seongsan",33.38677,126.88020,"제주"),
    (189,"서귀포","Seogwipo",33.24616,126.56530,"제주"),
    (192,"진주","Jinju",35.16378,128.04004,"경남"),
    (201,"강화","Ganghwa",37.70739,126.44634,"인천"),
    (202,"양평","Yangpyeong",37.48863,127.49446,"경기도"),
    (203,"이천","Icheon",37.26399,127.48421,"경기도"),
    (211,"인제","Inje",38.05986,128.16714,"강원도"),
    (212,"홍천","Hongcheon",37.68360,127.88043,"강원도"),
    (216,"태백","Taebaek",37.17038,128.98929,"강원도"),
    (217,"정선군","Jeongseon Gun",37.38149,128.64590,"강원도"),
    (221,"제천","Jecheon",37.15928,127.19433,"충북"),
    (226,"보은","Boeun",36.48761,127.73415,"충북"),
    (232,"천안","Cheonan",36.76217,127.29282,"충남"),
    (235,"보령","Boryeong",36.32724,126.55744,"충남"),
    (236,"부여","Buyeo",36.27242,126.92079,"충남"),
    (238,"금산","Geumsan",36.10563,127.48175,"충남"),
    (239,"세종","Sejong",36.48522,127.24438,"세종"),
    (243,"부안","Buan",35.72961,126.71657,"전북"),
    (244,"임실","Imsil",35.61203,127.28556,"전북"),
    (245,"정읍","Jeongeup",35.56337,126.83904,"전북"),
    (247,"남원","Namwon",35.42130,127.39652,"전북"),
    (248,"장수","Jangsu",35.65696,127.52031,"전북"),
    (251,"고창군","Gochanggun",35.42661,126.69700,"전북"),
    (252,"영광군","Yeonggwanggun",35.28366,126.47784,"전남"),
    (253,"김해시","Gimhaesi",35.22981,128.89075,"경남"),
    (254,"순창군","Sunchanggun",35.37131,127.12860,"전북"),
    (255,"북창원","Bukchangwon",35.22655,128.67260,"경남"),
    (257,"양산시","Yangsansi",35.30737,129.02009,"경남"),
    (258,"보성군","Boseonggun",34.76335,127.21226,"전남"),
    (259,"강진군","Gangjingun",34.64457,126.78408,"전남"),
    (260,"장흥","Jangheung",34.68886,126.91951,"전남"),
    (261,"해남","Haenam",34.55375,126.56907,"전남"),
    (262,"고흥","Goheung",34.61826,127.27572,"전남"),
    (263,"의령군","Uiryeonggun",35.32258,128.28812,"경남"),
    (264,"함양군","Hamyanggun",35.51138,127.74538,"경남"),
    (266,"광양시","Gwangyangsi",34.94340,127.69140,"전남"),
    (268,"진도군","Jindogun",34.47296,126.25846,"전남"),
    (271,"봉화","Bonghwa",36.94361,128.91449,"경북"),
    (272,"영주","Yeongju",36.87183,128.51687,"경북"),
    (273,"문경","Mungyeong",36.62727,128.14879,"경북"),
    (276,"청송군","Cheongsonggun",36.43510,129.04005,"경북"),
    (277,"영덕","Yeongdeok",36.53337,129.40926,"경북"),
    (278,"의성","Uiseong",36.35610,128.68864,"경북"),
    (279,"구미","Gumi",36.13055,128.32055,"경북"),
    (281,"영천","Yeongcheon",35.97742,128.95140,"경북"),
    (283,"경주시","Gyeongjusi",35.81740,129.20090,"경북"),
    (284,"거창","Geochang",35.66739,127.90990,"경남"),
    (285,"합천","Hapcheon",35.56505,128.16994,"경남"),
    (288,"밀양","Miryang",35.49147,128.74412,"경남"),
    (289,"산청","Sancheong",35.41300,127.87910,"경남"),
    (294,"거제","Geoje",34.88818,128.60459,"경남"),
    (295,"남해","Namhae",34.81662,127.92641,"경남"),
], columns=["stn_id","name_ko","name_en","lat","lon","region"])

STATIONS["label"] = STATIONS["name_ko"] + " (" + STATIONS["region"] + ")"

base_url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php"
month_labels = {i: f"{i}월" for i in range(1, 13)}
max_days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}


# ─── 사이드바 ────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정 패널")

    # 인증키가 없으면 사이드바에서 직접 입력
    if not auth_key:
        st.subheader("🔑 API 인증키 입력")
        input_key = st.text_input(
            "기상청 API 인증키",
            type="password",
            placeholder="apihub.kma.go.kr에서 발급",
            help=".env 파일 또는 st.secrets['KMA_AUTH_KEY']로도 설정 가능합니다."
        )
        if input_key:
            auth_key = input_key
        else:
            st.warning("인증키를 입력해야 데이터를 조회할 수 있습니다.")
        st.divider()

    # 지점 선택 — 검색 + 지도
    st.subheader("📍 관측소 선택")
    search_kw = st.text_input("지역 검색", placeholder="예: 서울, 부산, 제주...")
    if search_kw:
        filtered = STATIONS[STATIONS["label"].str.contains(search_kw, case=False)]
    else:
        filtered = STATIONS

    if filtered.empty:
        st.warning("검색 결과 없음")
        filtered = STATIONS

    selected_label = st.selectbox(
        "관측소 선택",
        filtered["label"].tolist(),
        help="목록에서 선택하거나 위 검색창에서 지역명을 입력하세요."
    )
    selected_row = STATIONS[STATIONS["label"] == selected_label].iloc[0]
    station_id   = str(int(selected_row["stn_id"]))
    station_name = selected_row["name_ko"]

    st.divider()

    # 기간
    st.subheader("📅 비교 기간 설정")
    c1, c2 = st.columns(2)
    with c1:
        s_month = st.selectbox("시작 월", list(month_labels.keys()),
                               format_func=lambda x: month_labels[x], index=0)
        s_day   = st.slider("시작 일", 1, max_days[s_month], 1)
    with c2:
        e_month = st.selectbox("종료 월", list(month_labels.keys()),
                               format_func=lambda x: month_labels[x], index=1)
        e_day   = st.slider("종료 일", 1, max_days[e_month], max_days[e_month])

    valid_range = (s_month, s_day) <= (e_month, e_day)
    if not valid_range:
        st.error("⚠️ 종료일이 시작일보다 앞설 수 없습니다.")

    st.divider()

    # 연도
    st.subheader("📆 비교할 연도")
    selected_years = st.multiselect(
        "연도 선택 (다중 선택 가능)",
        list(range(2015, 2027)),
        default=[2025, 2026]
    )
    st.divider()

    # 기온 항목
    st.subheader("🌡️ 기온 항목")
    obs_options = {
        "일 평균기온 (TA_AVG)": 10,
        "최고기온 (TA_MAX)": 11,
        "최저기온 (TA_MIN)": 13,
    }
    obs_label   = st.selectbox("표시 항목", list(obs_options.keys()))
    obs_col_idx = obs_options[obs_label]


# ─── 관측소 지도 (메인 상단) ─────────────────
with st.expander("🗺️ 관측소 지도 — 클릭하여 위치 확인", expanded=False):
    fig_map = go.Figure()
    # 전체 지점
    fig_map.add_trace(go.Scattermap(
        lat=STATIONS["lat"], lon=STATIONS["lon"],
        mode="markers+text",
        marker=dict(size=8, color="#4A90D9"),
        text=STATIONS["name_ko"],
        textposition="top center",
        textfont=dict(size=10),
        hovertemplate="%{text}<br>(%{lat:.4f}, %{lon:.4f})<extra></extra>",
        name="관측소"
    ))
    # 선택된 지점 강조
    fig_map.add_trace(go.Scattermap(
        lat=[selected_row["lat"]], lon=[selected_row["lon"]],
        mode="markers+text",
        marker=dict(size=16, color="#E74C3C"),
        text=[selected_row["name_ko"]],
        textposition="top center",
        textfont=dict(size=12, color="#E74C3C"),
        hovertemplate=f"선택: {station_name}<extra></extra>",
        name="선택 관측소"
    ))
    fig_map.update_layout(
        map=dict(style="open-street-map", center=dict(lat=36.5, lon=127.8), zoom=6),
        height=420,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )
    st.plotly_chart(fig_map, width="stretch")
    st.caption(f"🔴 선택된 관측소: **{station_name}** (지점번호: {station_id})")


# ─── 데이터 fetch ─────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_kma_data(year, sm, sd, em, ed, stn_id, key, obs_col):
    tm1 = f"{year}{sm:02d}{sd:02d}"
    tm2 = f"{year}{em:02d}{ed:02d}"
    params = {"tm1": tm1, "tm2": tm2, "stn": stn_id, "authKey": key, "help": "0"}
    try:
        res = requests.get(base_url, params=params, timeout=15)
        res.raise_for_status()
        rows = []
        for line in res.text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) > obs_col and parts[0].isdigit() and len(parts[0]) == 8:
                mmdd = f"{parts[0][4:6]}-{parts[0][6:8]}"
                rows.append({"mmdd": mmdd, "ta": parts[obs_col]})
        if not rows:
            return pd.DataFrame(), "데이터 없음"
        df = pd.DataFrame(rows)
        df["ta"] = pd.to_numeric(df["ta"], errors="coerce")
        df.loc[df["ta"] <= -9.0, "ta"] = float("nan")
        df = df.dropna(subset=["ta"])
        return df[["mmdd","ta"]].rename(columns={"ta": f"{year}년"}), "성공"
    except Exception as e:
        return pd.DataFrame(), str(e)


# ─── 메인 영역 ───────────────────────────────
period_str = f"{s_month}월 {s_day}일 ~ {e_month}월 {e_day}일"
st.info(f"**{station_name}** | 기간: **{period_str}** | 항목: **{obs_label}**")

if not valid_range:
    st.warning("올바른 기간을 설정해주세요.")
elif not selected_years:
    st.warning("비교할 연도를 하나 이상 선택해주세요.")
elif st.button("🚀 데이터 불러오기", type="primary"):

    # 공통 x축 날짜 목록 생성
    all_mmdd = []
    for m in range(s_month, e_month + 1):
        d_start = s_day if m == s_month else 1
        d_end   = e_day if m == e_month else max_days[m]
        for d in range(d_start, d_end + 1):
            all_mmdd.append(f"{m:02d}-{d:02d}")

    merged_df  = pd.DataFrame({"mmdd": all_mmdd}).set_index("mmdd")
    fetch_log  = []
    progress   = st.progress(0, text="데이터를 가져오는 중...")

    for i, y in enumerate(sorted(selected_years)):
        progress.progress((i+1)/len(selected_years), text=f"{y}년 데이터 요청 중...")
        df_y, status = fetch_kma_data(y, s_month, s_day, e_month, e_day,
                                      station_id, auth_key, obs_col_idx)
        if not df_y.empty:
            df_y = df_y.set_index("mmdd")
            merged_df[f"{y}년"] = df_y[f"{y}년"]
            fetch_log.append((y, "✅", f"{df_y[f'{y}년'].notna().sum()}일 수신"))
        else:
            fetch_log.append((y, "❌", status))

    progress.empty()

    with st.expander("📡 데이터 수신 결과", expanded=False):
        for y, icon, msg in fetch_log:
            st.write(f"{icon} **{y}년**: {msg}")

    data_cols = [c for c in merged_df.columns if merged_df[c].notna().any()]

    if data_cols:
        st.success(f"✅ {station_name} / {period_str} 비교 결과")

        fig = go.Figure()
        for col in data_cols:
            y_vals = [
                (float(merged_df.at[d, col])
                 if d in merged_df.index and pd.notna(merged_df.at[d, col])
                 else None)
                for d in all_mmdd
            ]
            fig.add_trace(go.Scatter(
                x=all_mmdd, y=y_vals,
                mode="lines+markers", name=col,
                marker=dict(size=4), line=dict(width=2),
                connectgaps=False,
                hovertemplate="%{x}: %{y:.1f}°C<extra></extra>"
            ))
        fig.update_layout(
            xaxis=dict(type="category", categoryorder="array",
                       categoryarray=all_mmdd, title="날짜 (월-일)", tickangle=-45),
            yaxis_title="기온 (°C)",
            legend_title="연도", hovermode="x unified",
            height=440, margin=dict(l=40, r=20, t=30, b=60),
        )
        st.plotly_chart(fig, width="stretch")

        st.subheader("📊 기간 평균 기온")
        cols = st.columns(len(data_cols))
        for i, col in enumerate(data_cols):
            mean_val = merged_df[col].mean()
            cnt = int(merged_df[col].notna().sum())
            cols[i].metric(
                label=col,
                value=f"{mean_val:.1f} °C" if not pd.isna(mean_val) else "없음",
                delta=f"{cnt}일 관측"
            )

        with st.expander("📋 상세 데이터 보기"):
            st.dataframe(
                merged_df[data_cols].style.format("{:.1f}", na_rep="-"),
                use_container_width=True
            )
    else:
        st.error("데이터를 불러오지 못했습니다. 기간 또는 연도를 확인해주세요.")