import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from my_japanize import japanize
import numpy as np

japanize()
st.set_page_config(page_title="損益分岐点シミュレーター", layout="wide")

# ページタイトルとロゴ
st.image("TAIMATSU_logo.png", width=289)
st.markdown("<h2 style='color:#EE7700;'>損益分岐点シミュレーター</h2>", unsafe_allow_html=True)

# 2カラムレイアウト（入力左、グラフ右）
left_col, right_col = st.columns([1, 2])

with left_col:
    st.subheader("🏠 物件情報")
    rent = st.number_input("家賃（月）[万円]", value=100, step=10)

    st.subheader("👥 人件費")
    salary = st.number_input("人件費（月）[万円]", value=100, step=10)

    st.subheader("💰 初期費用内訳")
    key_money = st.number_input("礼金 [万円]", value=100)
    deposit = st.number_input("敷金 [万円]", value=100)
    guarantee_money = st.number_input("保証金 [万円]", value=100)
    agency_fee = st.number_input("仲介手数料 [万円]", value=100)
    interior_cost = st.number_input("内装工事費 [万円]", value=100)
    others = st.number_input("その他費用 [万円]", value=100)

    st.subheader("📈 シミュレーション設定")
    sales = st.number_input("月間売上 [万円]", value=500, step=10)
    months = st.slider("シミュレーション月数", 1, 24, value=12)

# 定数
contribution_margin = 0.64

# 金額換算（万円 → 円）
monthly_rent = rent * 10000
monthly_salary = salary * 10000
monthly_fixed_cost = monthly_rent + monthly_salary
monthly_sales = sales * 10000

# 初期費用合計
initial_cost_yen = sum([
    key_money, deposit, guarantee_money,
    agency_fee, interior_cost, others
]) * 10000

# 損益分岐点計算
denominator = monthly_sales * contribution_margin - monthly_fixed_cost
if denominator <= 0:
    breakeven_month = None
    breakeven_y = None
    result_text = "この条件では損益分岐点売上に達しません。"
else:
    breakeven_month = initial_cost_yen / denominator
    breakeven_y = monthly_sales * breakeven_month
    result_text = f"■ ペイできるまで：{breakeven_month:.1f}ヶ月"

with right_col:
    st.markdown(f"<h4 style='font-weight:bold;'>{result_text}</h4>", unsafe_allow_html=True)

    x_fine = np.linspace(1, months, 300)
    sales_line = monthly_sales * x_fine
    bep_line = (initial_cost_yen + monthly_fixed_cost * x_fine) / contribution_margin

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    ax.plot(x_fine, sales_line, label="予想累積売上", color="#1f77b4", linewidth=2)
    ax.plot(x_fine, bep_line, label="累積損益分岐点売上", color="#ff7f0e", linestyle="--", linewidth=2)
    ax.set_title("予想売上と回収ラインの比較")
    ax.set_xlabel("月")
    ax.set_ylabel("金額（円）")
    ax.grid(True)
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


