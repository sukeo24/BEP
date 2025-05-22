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
# 2カラムレイアウト
# -----------------------------
left_col, right_col = st.columns([1.4, 2])

with left_col:
    st.markdown("### 🏠 物件情報", unsafe_allow_html=True)
    rent = st.number_input("家賃（月）[万円]", value=100, step=10)

    st.markdown("### 👥 人件費", unsafe_allow_html=True)
    salary = st.number_input("人件費（月）[万円]", value=100, step=10)

    st.markdown("### 💰 初期費用内訳", unsafe_allow_html=True)
    key_money = st.number_input("礼金 [万円]", value=100, step=10)
    deposit = st.number_input("敷金 [万円]", value=100, step=10)
    guarantee_money = st.number_input("保証金 [万円]", value=100, step=10)
    agency_fee = st.number_input("仲介手数料 [万円]", value=100, step=10)
    interior_cost = st.number_input("内装工事費 [万円]", value=100, step=10)
    others = st.number_input("その他費用 [万円]", value=100, step=10)

    st.markdown("### 📈 シミュレーション設定", unsafe_allow_html=True)
    sales = st.number_input("月間売上 [万円]", value=500, step=10)
    months = st.slider("シミュレーション月数", 1, 24, value=12, step=1)

# -----------------------------
# 💹 損益分岐点計算
# -----------------------------
contribution_margin = 0.64
monthly_rent = rent * 10000
monthly_salary = salary * 10000
monthly_fixed_cost = monthly_rent + monthly_salary
monthly_sales = sales * 10000
initial_cost_yen = sum([
    key_money, deposit, guarantee_money,
    agency_fee, interior_cost, others
]) * 10000

denominator = monthly_sales * contribution_margin - monthly_fixed_cost
if denominator <= 0:
    breakeven_month = None
    breakeven_y = None
    result_text = "<span style='color:red;'>この条件では損益分岐点売上に達しません。</span>"
else:
    breakeven_month = initial_cost_yen / denominator
    breakeven_y = monthly_sales * breakeven_month
    result_text = f"<b>■ ペイできるまで：</b> <span style='color:#EE7700;'>{breakeven_month:.1f}ヶ月</span>"

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
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

    if breakeven_month is not None:
        ax.plot(breakeven_month, breakeven_y, "ro")
        ax.annotate(f"{breakeven_month:.1f}ヶ月\n¥{int(breakeven_y):,}",
                    xy=(breakeven_month, breakeven_y),
                    xytext=(breakeven_month + 0.5, breakeven_y),
                    textcoords="data",
                    arrowprops=dict(arrowstyle="->", color="gray"),
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"),
                    fontsize=10)

    st.pyplot(fig)
