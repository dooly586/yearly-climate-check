import streamlit as st
import requests
import pandas as pd
import os
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

# ─── 인증키 (우선순위: .env → st.secrets → 직접 입력) ──
auth_key = os.getenv("KMA_AUTH_KEY", "") or os.getenv("KMA_API_KEY", "")
if not auth_key:
    try:
        auth_key = st.secrets.get("KMA_API_KEY", "") or st.secrets.get("KMA_AUTH_KEY", "")
    except Exception:
        auth_key = ""

st.set_page_config(page_title="기온 비교 대시보드", page_icon="🌡️")

# ─── 모바일 최적화 CSS ───────────────────────────────
st.markdown("""
<style>
  /* 전체 패딩 축소 */
  .block-container { padding: 1rem 1rem 3rem !important; max-width: 100% !important; }

  /* 버튼 크게 */
  .stButton > button {
    width: 100%;
    height: 3rem;
    font-size: 1.1rem;
    font-weight: bold;
    border-radius: 0.5rem;
  }

  /* 입력 필드 높이 편하게 */
  .stSelectbox > div, .stTextInput > div { font-size: 1rem; }

  /* 슬라이더 터치 친화적 */
  .stSlider > div { padding: 0.25rem 0; }

  /* 메트릭 카드 중앙 정렬 */
  [data-testid="metric-container"] { text-align: center; }

  /* expander 터치 영역 확장 */
  .streamlit-expanderHeader { font-size: 1rem; padding: 0.75rem 0; }

  /* 상단 헤더 */
  h1 { font-size: 1.5rem !important; }
  h3 { font-size: 1.1rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🌡️ 연도별 기온 비교")
st.caption("기상청 API · 지정 기간 연도별 비교")

# ─── 전체 지상관측 지점 ─────────────────────────────
STATIONS = pd.DataFrame([
    (90,"속초",38.25085,128.56473,"강원"),(93,"북춘천",37.94738,127.75443,"강원"),
    (95,"철원",38.14787,127.30420,"강원"),(98,"동두천",37.90188,127.06070,"경기"),
    (99,"파주",37.88589,126.76648,"경기"),(100,"대관령",37.67713,128.71834,"강원"),
    (101,"춘천",37.90262,127.73570,"강원"),(102,"백령도",37.97396,124.71237,"인천"),
    (104,"북강릉",37.80456,128.85535,"강원"),(105,"강릉",37.75147,128.89099,"강원"),
    (106,"동해",37.50709,129.12433,"강원"),(108,"서울",37.57142,126.96580,"서울"),
    (112,"인천",37.47772,126.62490,"인천"),(114,"원주",37.33749,127.94659,"강원"),
    (115,"울릉도",37.48129,130.89863,"경북"),(119,"수원",37.25746,126.98300,"경기"),
    (121,"영월",37.18126,128.45743,"강원"),(127,"충주",36.97045,127.95250,"충북"),
    (129,"서산",36.77658,126.49390,"충남"),(130,"울진",36.99176,129.41278,"경북"),
    (131,"청주",36.63924,127.44066,"충북"),(133,"대전",36.37199,127.37210,"대전"),
    (135,"추풍령",36.22025,127.99458,"충북"),(136,"안동",36.57293,128.70733,"경북"),
    (137,"상주",36.40837,128.15741,"경북"),(138,"포항",36.03201,129.38002,"경북"),
    (140,"군산",36.00530,126.76135,"전북"),(143,"대구",35.87797,128.65296,"대구"),
    (146,"전주",35.84092,127.11718,"전북"),(152,"울산",35.58237,129.33469,"울산"),
    (155,"창원",35.17019,128.57282,"경남"),(156,"광주",35.17294,126.89156,"광주"),
    (159,"부산",35.10468,129.03203,"부산"),(162,"통영",34.84541,128.43561,"경남"),
    (165,"목포",34.81732,126.38151,"전남"),(168,"여수",34.73929,127.74063,"전남"),
    (169,"흑산도",34.68719,125.45105,"전남"),(170,"완도",34.39590,126.70182,"전남"),
    (172,"고창",35.34824,126.59900,"전북"),(174,"순천",35.02040,127.36940,"전남"),
    (177,"홍성",36.65759,126.68772,"충남"),(184,"제주",33.51411,126.52969,"제주"),
    (185,"고산",33.29382,126.16283,"제주"),(188,"성산",33.38677,126.88020,"제주"),
    (189,"서귀포",33.24616,126.56530,"제주"),(192,"진주",35.16378,128.04004,"경남"),
    (201,"강화",37.70739,126.44634,"인천"),(202,"양평",37.48863,127.49446,"경기"),
    (203,"이천",37.26399,127.48421,"경기"),(211,"인제",38.05986,128.16714,"강원"),
    (212,"홍천",37.68360,127.88043,"강원"),(216,"태백",37.17038,128.98929,"강원"),
    (217,"정선",37.38149,128.64590,"강원"),(221,"제천",37.15928,127.19433,"충북"),
    (226,"보은",36.48761,127.73415,"충북"),(232,"천안",36.76217,127.29282,"충남"),
    (235,"보령",36.32724,126.55744,"충남"),(236,"부여",36.27242,126.92079,"충남"),
    (238,"금산",36.10563,127.48175,"충남"),(239,"세종",36.48522,127.24438,"세종"),
    (243,"부안",35.72961,126.71657,"전북"),(244,"임실",35.61203,127.28556,"전북"),
    (245,"정읍",35.56337,126.83904,"전북"),(247,"남원",35.42130,127.39652,"전북"),
    (248,"장수",35.65696,127.52031,"전북"),(251,"고창군",35.42661,126.69700,"전북"),
    (252,"영광",35.28366,126.47784,"전남"),(253,"김해",35.22981,128.89075,"경남"),
    (254,"순창",35.37131,127.12860,"전북"),(255,"북창원",35.22655,128.67260,"경남"),
    (257,"양산",35.30737,129.02009,"경남"),(258,"보성",34.76335,127.21226,"전남"),
    (259,"강진",34.64457,126.78408,"전남"),(260,"장흥",34.68886,126.91951,"전남"),
    (261,"해남",34.55375,126.56907,"전남"),(262,"고흥",34.61826,127.27572,"전남"),
    (263,"의령",35.32258,128.28812,"경남"),(264,"함양",35.51138,127.74538,"경남"),
    (266,"광양",34.94340,127.69140,"전남"),(268,"진도",34.47296,126.25846,"전남"),
    (271,"봉화",36.94361,128.91449,"경북"),(272,"영주",36.87183,128.51687,"경북"),
    (273,"문경",36.62727,128.14879,"경북"),(276,"청송",36.43510,129.04005,"경북"),
    (277,"영덕",36.53337,129.40926,"경북"),(278,"의성",36.35610,128.68864,"경북"),
    (279,"구미",36.13055,128.32055,"경북"),(281,"영천",35.97742,128.95140,"경북"),
    (283,"경주",35.81740,129.20090,"경북"),(284,"거창",35.66739,127.90990,"경남"),
    (285,"합천",35.56505,128.16994,"경남"),(288,"밀양",35.49147,128.74412,"경남"),
    (289,"산청",35.41300,127.87910,"경남"),(294,"거제",34.88818,128.60459,"경남"),
    (295,"남해",34.81662,127.92641,"경남"),
], columns=["stn_id","name","lat","lon","region"])
STATIONS["label"] = STATIONS["name"] + " (" + STATIONS["region"] + ")"

base_url = "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd3.php"
max_days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
month_labels = {i: f"{i}월" for i in range(1, 13)}

# ─── 인증키 입력 (없을 때만 표시) ──────────────────
if not auth_key:
    st.warning("🔑 기상청 API 인증키를 입력해주세요.")
    auth_key = st.text_input("인증키", type="password",
                              placeholder="apihub.kma.go.kr에서 발급")
    if not auth_key:
        st.stop()
    st.divider()

# ─── 설정 폼 (모바일 친화: 한 번에 모두 입력 후 조회) ──
with st.form("search_form"):
    st.subheader("📍 관측소 선택")
    search_kw = st.text_input("지역 검색", placeholder="예: 서울, 부산, 제주...")
    filtered = STATIONS[STATIONS["label"].str.contains(search_kw, case=False)] \
               if search_kw else STATIONS
    if filtered.empty:
        filtered = STATIONS
    selected_label = st.selectbox("관측소", filtered["label"].tolist())

    st.subheader("📅 비교 기간")
    c1, c2 = st.columns(2)
    with c1:
        s_month = st.selectbox("시작 월", list(range(1, 13)),
                               format_func=lambda x: f"{x}월", index=0)
        s_day = st.number_input("시작 일", 1, 31, 1)
    with c2:
        e_month = st.selectbox("종료 월", list(range(1, 13)),
                               format_func=lambda x: f"{x}월", index=1)
        e_day = st.number_input("종료 일", 1, 31, 28)

    st.subheader("📆 비교 연도")
    selected_years = st.multiselect(
        "연도 선택",
        list(range(2015, 2027)),
        default=[2025, 2026],
        help="여러 연도를 선택하면 하나의 그래프에서 비교합니다."
    )

    st.subheader("🌡️ 기온 항목")
    obs_label = st.radio(
        "표시 항목",
        ["일 평균기온 (TA_AVG)", "최고기온 (TA_MAX)", "최저기온 (TA_MIN)"],
        horizontal=True
    )
    obs_col_idx = {"일 평균기온 (TA_AVG)": 10, "최고기온 (TA_MAX)": 11, "최저기온 (TA_MIN)": 13}[obs_label]

    submitted = st.form_submit_button("🚀 기온 데이터 조회", use_container_width=True)

# ─── 관측소 지도 ────────────────────────────────────
selected_row = STATIONS[STATIONS["label"] == selected_label].iloc[0]
station_id   = str(int(selected_row["stn_id"]))
station_name = selected_row["name"]

with st.expander("🗺️ 관측소 위치 확인"):
    fig_map = go.Figure()
    fig_map.add_trace(go.Scattermap(
        lat=STATIONS["lat"], lon=STATIONS["lon"],
        mode="markers", marker=dict(size=7, color="#4A90D9"),
        text=STATIONS["label"],
        hovertemplate="%{text}<extra></extra>",
    ))
    fig_map.add_trace(go.Scattermap(
        lat=[selected_row["lat"]], lon=[selected_row["lon"]],
        mode="markers+text",
        marker=dict(size=15, color="#E74C3C"),
        text=[station_name], textposition="top center",
        hovertemplate=f"선택: {station_name}<extra></extra>",
    ))
    fig_map.update_layout(
        map=dict(style="open-street-map",
                 center=dict(lat=selected_row["lat"], lon=selected_row["lon"]), zoom=7),
        height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
    )
    st.plotly_chart(fig_map, width="stretch")


# ─── fetch 함수 ──────────────────────────────────────
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
                rows.append({"mmdd": f"{parts[0][4:6]}-{parts[0][6:8]}", "ta": parts[obs_col]})
        if not rows:
            return pd.DataFrame(), "데이터 없음"
        df = pd.DataFrame(rows)
        df["ta"] = pd.to_numeric(df["ta"], errors="coerce")
        df.loc[df["ta"] <= -9.0, "ta"] = float("nan")
        df = df.dropna(subset=["ta"])
        return df[["mmdd", "ta"]].rename(columns={"ta": f"{year}년"}), "성공"
    except Exception as e:
        return pd.DataFrame(), str(e)


# ─── 조회 결과 ───────────────────────────────────────
if submitted:
    if not selected_years:
        st.warning("비교할 연도를 하나 이상 선택해주세요.")
        st.stop()
    if (s_month, int(s_day)) > (e_month, int(e_day)):
        st.error("종료일이 시작일보다 앞설 수 없습니다.")
        st.stop()

    # 공통 x축 날짜 목록
    all_mmdd = []
    for m in range(s_month, e_month + 1):
        d_start = int(s_day) if m == s_month else 1
        d_end   = int(e_day) if m == e_month else max_days[m]
        for d in range(d_start, d_end + 1):
            all_mmdd.append(f"{m:02d}-{d:02d}")

    merged_df = pd.DataFrame({"mmdd": all_mmdd}).set_index("mmdd")
    fetch_log = []
    prog = st.progress(0)

    for i, y in enumerate(sorted(selected_years)):
        prog.progress((i + 1) / len(selected_years), text=f"{y}년 조회 중...")
        df_y, status = fetch_kma_data(y, s_month, int(s_day), e_month, int(e_day),
                                      station_id, auth_key, obs_col_idx)
        if not df_y.empty:
            merged_df[f"{y}년"] = df_y.set_index("mmdd")[f"{y}년"]
            fetch_log.append((y, "✅", f"{df_y[f'{y}년'].notna().sum()}일"))
        else:
            fetch_log.append((y, "❌", status))

    prog.empty()

    data_cols = [c for c in merged_df.columns if merged_df[c].notna().any()]

    period_str = f"{s_month}/{int(s_day)} ~ {e_month}/{int(e_day)}"
    st.success(f"✅ {station_name} · {period_str}")

    # 수신 로그
    with st.expander("📡 수신 결과"):
        for y, icon, msg in fetch_log:
            st.write(f"{icon} {y}년: {msg}")

    if data_cols:
        # 차트
        fig = go.Figure()
        for col in data_cols:
            y_vals = [
                float(merged_df.at[d, col]) if d in merged_df.index and pd.notna(merged_df.at[d, col]) else None
                for d in all_mmdd
            ]
            fig.add_trace(go.Scatter(
                x=all_mmdd, y=y_vals,
                mode="lines+markers", name=col,
                marker=dict(size=5), line=dict(width=2.5),
                connectgaps=False,
                hovertemplate="%{x}: %{y:.1f}°C<extra></extra>"
            ))
        fig.update_layout(
            xaxis=dict(type="category", categoryorder="array", categoryarray=all_mmdd,
                       title="날짜 (월-일)", tickangle=-60, tickfont=dict(size=10)),
            yaxis=dict(title="기온 (°C)", tickfont=dict(size=11)),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
            height=380,
            margin=dict(l=40, r=10, t=40, b=60),
        )
        st.plotly_chart(fig, width="stretch")

        # 평균 카드 — 2열로 (모바일 화면 폭 고려)
        st.subheader("📊 평균 기온")
        n = len(data_cols)
        col_count = min(n, 2)  # 모바일에서 2열 이상은 너무 좁음
        rows = [data_cols[i:i+col_count] for i in range(0, n, col_count)]
        for row in rows:
            cs = st.columns(len(row))
            for ci, col in enumerate(row):
                mean_val = merged_df[col].mean()
                cnt = int(merged_df[col].notna().sum())
                cs[ci].metric(
                    label=col,
                    value=f"{mean_val:.1f} °C" if not pd.isna(mean_val) else "없음",
                    delta=f"{cnt}일 관측"
                )

        # 상세 테이블
        with st.expander("📋 상세 데이터"):
            st.dataframe(
                merged_df[data_cols].style.format("{:.1f}", na_rep="-"),
                width="stretch"
            )
    else:
        st.error("데이터를 불러오지 못했습니다.")