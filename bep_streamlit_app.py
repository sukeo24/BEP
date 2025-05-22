
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker
import numpy as np

mpl.rcParams['font.family'] = 'IPAexGothic' 

st.set_page_config(page_title="損益分岐点シミュレーター", layout="centered")

# タイトルとロゴ
st.image("TAIMATSU_logo.png", width=289)
st.markdown("<h2 style='color:#EE7700;'>損益分岐点シミュレーター</h2>", unsafe_allow_html=True)

# 入力欄
col1, col2 = st.columns(2)
with col1:
    rent = st.number_input("家賃（月）[万円]", value=100, step=10)
    initial_cost = st.number_input("初期費用 [万円]", value=300, step=10)
with col2:
    sales = st.number_input("月間売上 [万円]", value=500, step=10)
    months = st.slider("シミュレーション月数", 1, 24, value=12)

# 定数
contribution_margin = 0.64

# 損益分岐点計算
monthly_rent = rent * 10000
monthly_sales = sales * 10000
initial_cost_yen = initial_cost * 10000

denominator = monthly_sales * contribution_margin - monthly_rent
if denominator <= 0:
    breakeven_month = None
    breakeven_y = None
    st.error("この条件では損益分岐点売上に達しません。")
else:
    breakeven_month = initial_cost_yen / denominator
    breakeven_y = monthly_sales * breakeven_month
    st.markdown(f"### ■ ペイできるまで：{breakeven_month:.1f}ヶ月")

# グラフ描画
x_fine = np.linspace(0, months, 300)
sales_line = monthly_sales * x_fine
bep_line = (initial_cost_yen + monthly_rent * x_fine) / contribution_margin

fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
ax.plot(x_fine, sales_line, label="予想累積売上", color="#1f77b4", linewidth=2)
ax.plot(x_fine, bep_line, label="累積損益分岐点売上", color="#ff7f0e", linestyle="--", linewidth=2)
ax.set_title("予想売上と回収ラインの比較")
ax.set_xlabel("月")
ax.set_ylabel("金額（円）")
ax.grid(True)
ax.legend()
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# 交点プロット
if breakeven_month is not None:
    ax.plot(breakeven_month, breakeven_y, "ro")
    ax.annotate(f"{breakeven_month:.1f}ヶ月\n¥{int(breakeven_y):,}", 
                xy=(breakeven_month, breakeven_y), 
                xytext=(breakeven_month + 0.3, breakeven_y),
                textcoords="data",
                arrowprops=dict(arrowstyle="->", color="gray"),
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray"),
                fontsize=10)

st.pyplot(fig)
