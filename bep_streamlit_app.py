import streamlit as st
import plotly.graph_objects as go
import numpy as np
from my_japanize import japanize

japanize()
st.set_page_config(page_title="BEP simulator", layout="wide")

st.markdown(
    """
    <div style='display: flex; align-items: center; justify-content: space-between;'>
        <div>
            <h1 style='color:#EE7700; margin-bottom: 0;'>BEP Simulator</h1>
            <div style='display: flex; align-items: center; margin-top: 0;'>
                <p style='color:#555; font-size:16px; margin-top: 0;'>powered by&nbsp;</p>
                <img src='https://raw.githubusercontent.com/sukeo24/BEP/bep/TAIMATSU_logo.png' width='110' style='margin-top: -15px;'>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


utilities = st.session_state.get("utilities", 7)
tax_rate_percent = st.session_state.get("tax_rate_percent", 10)
tax_rate = 1 + (tax_rate_percent / 100)

tabs = st.tabs(["予測①", "予測②", "予測③", "比較"])
results = []  # ← 比較用データ保持リスト

for idx, tab in enumerate(tabs, start=1):
    if idx <= 3:
        with tab:
            left_col, right_col = st.columns([1, 2])

            with left_col:
                st.markdown(f"### 📊 予想売上", unsafe_allow_html=True)
                sales = st.number_input("月間売上（税込）[万円]", value=500, step=10, key=f"sales_{idx}")
                
                st.markdown(f"### 🗓️ 月間固定費", unsafe_allow_html=True)
                rent = st.number_input("家賃（月）[万円][課税]", value=100, step=10, key=f"rent_{idx}")
                salary = st.number_input("人件費（月）[万円]", value=100, step=10, key=f"salary_{idx}")

                fixed_cost_display = (rent * tax_rate + salary + utilities)
                st.markdown(f"<div style='text-align:right; font-size:14px; color:#444;'>月間固定費合計: <b>¥{int(fixed_cost_display * 10000):,}</b></div>", unsafe_allow_html=True)

                st.markdown(f"### 💰 初期費用", unsafe_allow_html=True)
                key_money = st.number_input("礼金 [万円][課税]", value=100, step=10, key=f"key_money_{idx}")
                deposit = st.number_input("敷金 [万円]", value=100, step=10, key=f"deposit_{idx}")
                guarantee_money = st.number_input("保証金 [万円]", value=100, step=10, key=f"guarantee_{idx}")
                agency_fee = st.number_input("仲介手数料 [万円][課税]", value=100, step=10, key=f"agency_{idx}")
                interior_cost = st.number_input("内装工事費 [万円][課税]", value=100, step=10, key=f"interior_{idx}")
                others = st.number_input("その他費用 [万円][課税]", value=100, step=10, key=f"others_{idx}")

                initial_cost_display = (key_money * tax_rate + deposit + guarantee_money + agency_fee * tax_rate + interior_cost * tax_rate + others * tax_rate)
                st.markdown(f"<div style='text-align:right; font-size:14px;'>初期費用合計（税抜・税込計算後）: <b>¥{int(initial_cost_display * 10000):,}</b></div>", unsafe_allow_html=True)

                with st.expander("詳細設定", expanded=False):
                    months = st.slider("シミュレーション月数", 1, 24, value=12, step=1, key=f"months_{idx}")
                    contribution_margin = st.slider("粗利率", min_value=0.4, max_value=0.8, value=0.64, step=0.01, key=f"margin_{idx}")
                    utilities = st.number_input("光熱費・水道代・通信費（月）[万円]", value=7, step=1, key=f"utilities_{idx}")
                    tax_rate_percent = st.number_input("消費税率 [%]", value=10, step=1, key=f"tax_rate_percent_{idx}")


            # 計算
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
                fig.add_trace(go.Scatter(x=x_fine, y=sales_line, mode="lines", name="累積予想売上", line=dict(color="#1f77b4", width=3)))
                fig.add_trace(go.Scatter(x=x_fine, y=bep_line, mode="lines", name="累積損益分岐点売上", line=dict(color="#ff7f0e", width=3, dash="dot")))

                if breakeven_month is not None:
                    fig.add_trace(go.Scatter(
                        x=[breakeven_month], y=[breakeven_y],
                        mode="markers+text",
                        name="損益分岐点",
                        marker=dict(color="red", size=10),
                        text=[f"{breakeven_month:.1f}ヶ月<br>¥{int(breakeven_y):,}"],
                        textposition="top center",
                        textfont=dict(color="black", size=14, family="Arial")
                    ))

                fig.update_layout(
                    xaxis_title="月",
                    yaxis_title="金額（¥）",
                    yaxis=dict(tickformat=",.0f", tickprefix="¥", gridcolor="lightgray"),
                    xaxis=dict(tickformat=".1f"),
                    plot_bgcolor="white",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    height=600
                )

                st.plotly_chart(fig, use_container_width=True, key=f"chart_{idx}")

                st.markdown(
                    f"""
                    <div style='margin-top: 20px; padding: 12px; background-color: #f9f9f9; border-left: 5px solid #EE7700;'>
                        <p style='margin: 0; color: #333; font-size: 14px;'>
                            ※ このシミュレーションでは <b>消費税率を {tax_rate_percent}%</b> に設定しています。<br>
                            <b>課税対象:</b> 家賃、礼金、仲介手数料、内装工事費、その他費用<br>
                            <b>非課税対象:</b> 敷金、保証金<br>
                            また、光熱費・水道代・通信費を含む <b>その他固定費（月額 {utilities}万円）</b> も考慮しています。<br>
                            <b>月間売上は税込金額を入力してください。</b>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            # 👇 ループの最後に結果を記録
            results.append({
            "予測": f"予測 {idx}",
            "月間売上": sales,
            "家賃": rent,
            "人件費": salary,
            "礼金": key_money,
            "敷金": deposit,
            "保証金": guarantee_money,
            "仲介手数料": agency_fee,
            "内装工事費": interior_cost,
            "その他費用": others,
            "損益分岐点": breakeven_month if breakeven_month else float("nan"),
            "x": x_fine,
            "sales_line": sales_line,
            "bep_line": bep_line
        })

    elif idx == 4:
        with tab:
            st.markdown("### 📊 予測比較")

            # ✅ テーブル表示
            import pandas as pd

            df = pd.DataFrame(results)[[
                "予測", "月間売上", "家賃", "人件費", "礼金", "敷金", "保証金",
                "仲介手数料", "内装工事費", "その他費用", "損益分岐点"
            ]]

            # ✅ 損益分岐点の最小値インデックスを取得
            min_bep_idx = df["損益分岐点"].astype(float).idxmin()

            # ✅ カラムごとのヒートマップ（axis=0で列単位）
            styled_df = (
                df.style
                .format({
                    "月間売上": "{:.0f}万円",
                    "家賃": "{:.0f}万円",
                    "人件費": "{:.0f}万円",
                    "礼金": "{:.0f}万円",
                    "敷金": "{:.0f}万円",
                    "保証金": "{:.0f}万円",
                    "仲介手数料": "{:.0f}万円",
                    "内装工事費": "{:.0f}万円",
                    "その他費用": "{:.0f}万円",
                    "損益分岐点": "{:.1f}ヶ月"
                })
                .background_gradient(
                    subset=[
                        "月間売上", "家賃", "人件費", "礼金", "敷金", "保証金",
                        "仲介手数料", "内装工事費", "その他費用"
                    ],
                    cmap="Oranges",
                    axis=0,  # ← 各列ごとのグラデーションに変更
                    low=0, high=0.9,
                )
                .background_gradient(
                    subset=["損益分岐点"],
                    cmap="Reds",
                    axis=0,  # 各列ごとのグラデーションに変更
                    low=0, high=0.5,
                )
            )

            st.dataframe(styled_df, hide_index=True)
            
            # ✅ グラフ表示
            fig = go.Figure()
            colors = ["#1f77b4", "#2ca02c", "#d62728"]

            for i, result in enumerate(results):
                fig.add_trace(go.Scatter(
                    x=result["x"], y=result["sales_line"],
                    mode="lines", name=f'{result["予測"]}：累積予想売上',
                    line=dict(color=colors[i], width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=result["x"], y=result["bep_line"],
                    mode="lines", name=f'{result["予測"]}：累積損益分岐点売上',
                    line=dict(color=colors[i], width=2, dash="dot")
                ))
                
                # 損益分岐点マーカー＋テキスト
                if not np.isnan(result["損益分岐点"]):
                    bep_month = result["損益分岐点"]
                    bep_y = result["sales_line"][np.searchsorted(result["x"], bep_month)]
                    fig.add_trace(go.Scatter(
                        x=[bep_month],
                        y=[bep_y],
                        mode="markers+text",
                        name=f"{result['予測']}：損益分岐点",
                        marker=dict(color=colors[i], size=10),
                    ))

            fig.update_layout(
                xaxis_title="月",
                yaxis_title="金額（¥）",
                yaxis=dict(tickformat=",.0f", tickprefix="¥"),
                plot_bgcolor="white",
                height=700,
                legend=dict(
                    orientation="v",
                    x=1,
                    xanchor="right",
                    y=0.1,
                    yanchor="bottom",
                    font=dict(size=10, family="Arial", color="black"),
                    bgcolor="lightgray",  # 背景を透明に
                )
            )
            
            # 📌 グラフの前に必ずこれを記述
            st.markdown("""
                <style>
                .modebar {
                    display: none !important;
                }
                </style>
            """, unsafe_allow_html=True)

            st.plotly_chart(fig, use_container_width=True, 
                            key="comparison_chart", 
                            config={"displayModeBar": False})
