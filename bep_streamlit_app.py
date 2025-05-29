import streamlit as st
import plotly.graph_objects as go
import numpy as np
from my_japanize import japanize

japanize()
st.set_page_config(page_title="BEP simulator", layout="wide")

if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

st.markdown("""
<div style='display:flex; gap: 20px; margin-bottom: 30px;'>
    <form action="" method="post">
        <button name="page" value="main" style='padding: 10px 20px; background-color: #EE7700; color: white; border: none; border-radius: 5px; font-size: 16px;'>SIMULATOR</button>
        <button name="page" value="setting" style='padding: 10px 20px; background-color: #EE7700; color: white; border: none; border-radius: 5px; font-size: 16px;'>SETTINGS</button>
    </form>
</div>
""", unsafe_allow_html=True)

# Handle page switch manually
from streamlit import session_state as ss
import streamlit as st
import urllib.parse

params = st.experimental_get_query_params()
if "page" in params:
    st.session_state.current_page = params["page"][0]

current_page = st.session_state.current_page

st.markdown(
    """
    <div style='display: flex; align-items: center; justify-content: space-between;'>
        <div>
            <h1 style='color:#EE7700; margin-bottom: 0;'>BEP Simulator</h1>
            <div style='display: flex; align-items: center; margin-top: 0;'>
                <p style='color:#555; font-size:16px; margin: 0;'>powered by&nbsp;</p>
                <img src='https://raw.githubusercontent.com/sukeo24/BEP/bep/TAIMATSU_logo.png' width='80' style='margin-bottom: -2px;'>
            </div>
        </div>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)

if current_page == "setting":
    st.title("🔧 詳細設定")
    utilities = st.number_input("光熱費・水道代・通信費（月）[万円]", value=7, step=1, key="utilities")
    tax_rate_percent = st.number_input("消費税率 [%]", value=10, step=1, key="tax_rate_percent")
else:
    utilities = st.session_state.get("utilities", 7)
    tax_rate_percent = st.session_state.get("tax_rate_percent", 10)
    tax_rate = 1 + (tax_rate_percent / 100)

    left_col, right_col = st.columns([1, 3])

    with left_col:
        st.markdown("### 🗓️ 月間固定費", unsafe_allow_html=True)
        rent = st.number_input("家賃（月）[万円][課税]", value=100, step=10)
        salary = st.number_input("人件費（月）[万円]", value=100, step=10)

        fixed_cost_display = (rent * tax_rate + salary + utilities)
        st.markdown(f"<div style='text-align:right; font-size:14px; color:#444;'>月間固定費合計: <b>¥{int(fixed_cost_display * 10000):,}</b></div>", unsafe_allow_html=True)

        st.markdown("### 💰 初期費用内訳", unsafe_allow_html=True)
        key_money = st.number_input("礼金 [万円][課税]", value=100, step=10)
        deposit = st.number_input("敷金 [万円]", value=100, step=10)
        guarantee_money = st.number_input("保証金 [万円]", value=100, step=10)
        agency_fee = st.number_input("仲介手数料 [万円][課税]", value=100, step=10)
        interior_cost = st.number_input("内装工事費 [万円][課税]", value=100, step=10)
        others = st.number_input("その他費用 [万円][課税]", value=100, step=10)

        initial_cost_display = (key_money * tax_rate + deposit + guarantee_money + agency_fee * tax_rate + interior_cost * tax_rate + others * tax_rate)
        st.markdown(f"<div style='text-align:right; font-size:14px;'>初期費用合計（税抜・税込計算後）: <b>¥{int(initial_cost_display * 10000):,}</b></div>", unsafe_allow_html=True)

        st.markdown("### 📈 シミュレーション設定", unsafe_allow_html=True)
        sales = st.number_input("月間売上（税込）[万円]", value=500, step=10)
        months = st.slider("シミュレーション月数", 1, 24, value=12, step=1)

    contribution_margin = 0.64
    monthly_rent = rent * tax_rate * 10000
    monthly_salary = salary * 10000
    monthly_utilities = utilities * 10000
    monthly_fixed_cost = monthly_rent + monthly_salary + monthly_utilities
    monthly_sales = sales * 10000
    initial_cost_yen = sum([
        key_money * tax_rate,
        deposit,
        guarantee_money,
        agency_fee * tax_rate,
        interior_cost * tax_rate,
        others * tax_rate
    ]) * 10000

    denom = monthly_sales * contribution_margin - monthly_fixed_cost
    if denom <= 0:
        breakeven_month = None
        breakeven_y = None
        result_text = "<span style='color:red;'>この条件では損益分岐点売上に達しません。</span>"
    else:
        breakeven_month = initial_cost_yen / denom
        breakeven_y = monthly_sales * breakeven_month
        result_text = f"""
            <div style='background-color:#FFF3E0; padding: 12px 16px; border-left: 6px solid #EE7700; border-radius: 4px; font-size: 16px;'>
                <b>■ ペイできるまで：</b>
                <span style='color:#d84315; font-weight:bold; font-size: 22px;'>{breakeven_month:.1f}ヶ月</span>
            </div>
        """

    with right_col:
        st.markdown(f"<div style='margin-bottom:20px;'>{result_text}</div>", unsafe_allow_html=True)

        x_fine = np.linspace(1, months, 300)
        sales_line = monthly_sales * x_fine
        bep_line = (initial_cost_yen + monthly_fixed_cost * x_fine) / contribution_margin

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_fine, y=sales_line, mode="lines", name="予想累積売上", line=dict(color="#1f77b4", width=3)))
        fig.add_trace(go.Scatter(x=x_fine, y=bep_line, mode="lines", name="累積損益分岐点売上", line=dict(color="#ff7f0e", width=3, dash="dot")))

        if breakeven_month is not None:
            fig.add_trace(go.Scatter(
                x=[breakeven_month], y=[breakeven_y],
                mode="markers+text",
                name="損益分岐点",
                marker=dict(color="red", size=10),
                text=[f"{breakeven_month:.1f}ヶ月<br>¥{int(breakeven_y):,}"],
                ,
                textposition="top center"
            ))

        fig.update_layout(
            title="予想売上と回収ラインの比較",
            xaxis_title="月",
            yaxis_title="金額（¥）",
            yaxis=dict(tickformat=",.0f", tickprefix="¥", gridcolor="lightgray"),
            xaxis=dict(tickformat=".1f"),
            plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=600
        ),
            xaxis=dict(tickformat=".1f"),
            plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            f"""
            <div style='margin-top: 20px; padding: 12px; background-color: #f9f9f9; border-left: 5px solid #EE7700;'>
                <p style='margin: 0; color: #333; font-size: 14px;'>
                    ※ このシミュレーションでは <b>原価率を 30%</b>、<b>消費税率を {tax_rate_percent}%</b> に設定しています。<br>
                    <b>課税対象:</b> 家賃、礼金、仲介手数料、内装工事費、その他費用<br>
                    <b>非課税対象:</b> 敷金、保証金<br>
                    また、光熱費・水道代・通信費を含む <b>その他固定費（月額 {utilities}万円）</b> も考慮しています。<br>
                    <b>月間売上は税込金額を入力してください。</b>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
