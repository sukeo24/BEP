import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from my_japanize import japanize
import numpy as np

japanize()
st.set_page_config(page_title="BEP simulator", layout="wide")

# -----------------------------
# 🎨 ヘッダー部（ロゴ＋タイトル＋サブタイトル）
# -----------------------------
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

# -----------------------------
# 🔧 詳細設定（共通）
# -----------------------------
with st.expander("🔧 詳細設定"):
    utilities = st.number_input("光熱費・水道代・通信費（月）[万円]", value=7, step=1)
    tax_rate_percent = st.number_input("消費税率 [%]", value=10, step=1)

tax_rate = 1 + (tax_rate_percent / 100)

# -----------------------------
# 2カラムレイアウト
# -----------------------------
left_col, right_col = st.columns([1.4, 2])

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

# -----------------------------
# 📊 損益分岐点計算
# -----------------------------
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

# -----------------------------
# 📊 グラフ表示
# -----------------------------
with right_col:
    st.markdown(f"<div style='margin-bottom:20px;'>{result_text}</div>", unsafe_allow_html=True)

    x_fine = np.linspace(1, months, 300)
    sales_line = monthly_sales * x_fine
    bep_line = (initial_cost_yen + monthly_fixed_cost * x_fine) / contribution_margin

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    ax.plot(x_fine, sales_line, label="予想累積売上", color="#1f77b4", linewidth=2)
    ax.plot(x_fine, bep_line, label="累積損益分岐点売上", color="#ff7f0e", linestyle="--", linewidth=2)
    ax.set_title("予想売上と回収ラインの比較", fontsize=14)
    ax.set_xlabel("月")
    ax.grid(True, linestyle="dotted", alpha=0.7)
    ax.legend()
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"\u00a5{int(x):,}"))

    if breakeven_month is not None:
        ax.plot(breakeven_month, breakeven_y, "ro")
        ax.annotate(f"{breakeven_month:.1f}ヶ月\n\u00a5{int(breakeven_y):,}",
                    xy=(breakeven_month, breakeven_y),
                    xytext=(breakeven_month + 0.5, breakeven_y),
                    textcoords="data",
                    arrowprops=dict(arrowstyle="->", color="gray"),
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"),
                    fontsize=10)

    st.pyplot(fig)

    st.markdown(
        f"""
        <div style='margin-top: 20px; padding: 12px; background-color: #f9f9f9; border-left: 5px solid #EE7700;'>
            <p style='margin: 0; color: #333; font-size: 14px;'>
                ※ このシミュレーションでは <b>原価率を 30%</b>、<b>消費税率を {tax_rate_percent}%</b> に設定しています。<br>
                <b>課税対象:</b> 家賃、礼金、仲介手数料、内装工事費、その他費用<br>
                <b>非課税対象:</b> 敷金、保証金<br>
                また、光熱費・水道代・通信費を含む <b>その他固定費（月額 {utilities}万円）</b> も考慮しています。<br>
                <b>月間売上は税込金額として入力してください。</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

