import streamlit as st
import importlib
import meal_planner
importlib.reload(meal_planner)
from calculator import calculate_bmr, calculate_tdee, calculate_macros, calculate_bmi, calculate_water
from meal_planner import generate_meal_plan, generate_weekly_meal_plan, generate_exercise_plan
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

# --- 1. 網頁標題與設定 ---
st.set_page_config(
    page_title="個人化智慧 TDEE 計算器與健康生活分析系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("個人化智慧 TDEE 計算器與健康生活分析系統")
st.markdown("這是一個由 **Raymond** 與 **Andy** 共同開發的健康數據分析與生活型態輔助系統！")

# 科學依據與參考文獻折疊區 (醫學倫理與公衛標準依據)
with st.expander("本系統之科學依據、演算法與參考文獻 (Scientific References)", expanded=False):
    st.markdown(r"""
    本專案致力於將具備同儕審查（Peer-reviewed）之科學公式與公共衛生指引進行數位化實現：
    
    1. **基礎代謝率 (BMR) 公式**：
       - 採用 **Mifflin-St Jeor Formula (1990)**。研究證實此公式相較於傳統 Harris-Benedict 公式，在現代成年人體重評估上具備更高之預測精確度 ($\pm 10\%$ 誤差區間內比例最高)。
       - 文獻：*Mifflin MD, St Jeor ST, et al. "A new predictive equation for resting energy expenditure in healthy individuals." Am J Clin Nutr. 1990;51(2):241-247.*
    2. **每日總能量消耗 (TDEE) 與身體活動係數 (PAL)**：
       - 依據 **聯合國糧農組織 / 世界衛生組織 / 聯合國大學 (FAO/WHO/UNU)** 身體活動水準係數標準 (Physical Activity Level, 1.2 ～ 1.9)。
    3. **身體質量指數 (BMI) 與健康體位判定**：
       - 依據 **中華民國衛生福利部國民健康署 (HPA)** 國人健康體位分級指引：過輕 ($<18.5$)、標準 ($18.5 \le \text{BMI} < 24$)、過重 ($24 \le \text{BMI} < 27$)、輕度肥胖 ($27 \le \text{BMI} < 30$)、中度肥胖 ($30 \le \text{BMI} < 35$)、重度肥胖 ($\ge 35$)。
    4. **巨量營養素與膳食配置**：
       - 參考衛福部國健署《每日飲食指南手冊》及國際運動營養學會 (ISSN) 之能量與蛋白質攝取指引。
    """)

st.divider()

# --- 2. 側邊欄 (Sidebar) 輸入區 ---
with st.sidebar:
    st.header("生理數據設定")
    gender_input = st.radio("您的生理性別是？", options=["男生", "女生"], horizontal=True)
    
    # 雙向同步：滑桿 ↔ 輸入格
    def sync_slider_to_input(slider_key, input_key):
        st.session_state[input_key] = st.session_state[slider_key]
    def sync_input_to_slider(input_key, slider_key):
        st.session_state[slider_key] = st.session_state[input_key]
    
    # 初始化 session_state
    for key, default in [("age_s", 20), ("age_n", 20), ("height_s", 170), ("height_n", 170), ("weight_s", 60), ("weight_n", 60)]:
        if key not in st.session_state:
            st.session_state[key] = default
    
    st.slider("年齡 (歲)", min_value=1, max_value=100, key="age_s", on_change=sync_slider_to_input, args=("age_s", "age_n"))
    st.number_input("手動輸入年齡", min_value=1, max_value=100, key="age_n", on_change=sync_input_to_slider, args=("age_n", "age_s"), label_visibility="collapsed")
    age = st.session_state["age_n"]
    
    st.slider("身高 (cm)", min_value=100, max_value=220, key="height_s", on_change=sync_slider_to_input, args=("height_s", "height_n"))
    st.number_input("手動輸入身高", min_value=100, max_value=220, key="height_n", on_change=sync_input_to_slider, args=("height_n", "height_s"), label_visibility="collapsed")
    height = st.session_state["height_n"]
    
    st.slider("體重 (kg)", min_value=30, max_value=200, key="weight_s", on_change=sync_slider_to_input, args=("weight_s", "weight_n"))
    st.number_input("手動輸入體重", min_value=30, max_value=200, key="weight_n", on_change=sync_input_to_slider, args=("weight_n", "weight_s"), label_visibility="collapsed")
    weight = st.session_state["weight_n"]
    
    st.divider()
    st.header("生活目標設定")
    
    activity_options = {
        "久坐 (幾乎不運動)": 1.2,
        "輕度活動 (每週 1～3 天)": 1.375,
        "中度活動 (每週 3～5 天)": 1.55,
        "高度活動 (每週 6～7 天)": 1.725,
        "極度活動 (勞力密集)": 1.9
    }
    
    if "activity_choice" not in st.session_state:
        st.session_state["activity_choice"] = "久坐 (幾乎不運動)"
        
    current_act_index = list(activity_options.keys()).index(st.session_state["activity_choice"]) if st.session_state["activity_choice"] in activity_options else 0
    activity_label = st.radio("活動量水準", options=list(activity_options.keys()), index=current_act_index)
    st.session_state["activity_choice"] = activity_label
    activity_multiplier = activity_options[activity_label]
    
    goal_options = {
        "減脂 (Fat Loss)": "fat_loss",
        "維持 (Maintenance)": "maintenance",
        "增肌 (Muscle Gain)": "muscle_gain"
    }
    goal_label = st.radio("健康管理目標", options=list(goal_options.keys()))
    goal = goal_options[goal_label]

    diet_type = st.radio("日常飲食偏好", options=["均衡飲食 (Balanced)", "地中海飲食 (Mediterranean)", "生酮飲食 (Keto)", "外食族 (Eating Out)"])
    
    restrictions = st.multiselect("食材過敏與飲食禁忌", options=[
        "不吃海鮮", "不吃牛肉", "不吃豬肉", "堅果過敏", "乳糖不耐 (不碰乳製品)"
    ])

    calculate_btn = st.button("開始計算健康報告", type="primary", use_container_width=True)
    
    st.divider()
    st.header("顯示設定")
    font_size_label = st.select_slider("字體大小", options=["小", "中", "大", "特大"], value="大")
    
    st.divider()
    # 側邊欄醫療免責聲明 (醒目警示框，倫理合規)
    st.warning(
        "**醫學倫理與免責聲明 (Disclaimer)**\n\n"
        "本系統為自主學習專案之生活型態健康數據輔助工具，依據公開公衛文獻推算，"
        "**非屬醫療診斷，亦不能取代醫師或營養師之專業臨床諮詢**。\n\n"
        "若有特殊疾病、受傷病史或身體不適，請務必尋求合格醫療專業團隊協助。"
    )

# --- 全域字體大小與樣式設定 ---
font_size_map = {"小": "14px", "中": "16px", "大": "19px", "特大": "22px"}
selected_font_size = font_size_map[font_size_label]
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@300;400;500;600;700&display=swap');

    /* 全站字體全面採用 思源黑體 (Noto Sans TC) 與 Inter */
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stMarkdownContainer"], button, input, textarea, select {{
        font-family: 'Noto Sans TC', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    /* 主內容區域萬用字體調整 */
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] span,
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] li,
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] label,
    [data-testid="stAppViewContainer"] [data-testid="stMetricValue"] > div,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li {{
        font-family: 'Noto Sans TC', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        font-size: {selected_font_size} !important;
        line-height: 1.65;
        letter-spacing: 0.015em;
    }}

    /* 標題加重字重，提升視覺階層感 */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Noto Sans TC', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
    }}
    
    /* 分頁標籤加大加粗 */
    [data-testid="stAppViewContainer"] button[data-baseweb="tab"] {{
        font-family: 'Noto Sans TC', 'Inter', sans-serif !important;
        font-size: {selected_font_size} !important;
        font-weight: 700 !important;
        padding: 12px 20px !important;
        letter-spacing: 0.02em !important;
    }}
    
    [data-testid="stAppViewContainer"] button[data-baseweb="tab"][aria-selected="true"] {{
        border-bottom: 3px solid #ff4b4b !important;
    }}

    /* 側邊欄文字固定大小 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {{
        font-family: 'Noto Sans TC', 'Inter', sans-serif !important;
        font-size: 14px !important;
        letter-spacing: 0.01em;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. 主畫面分頁 (Tabs) ---
tab_report, tab_data = st.tabs(["健康數據報告", "穿戴裝置數據分析"])

with tab_report:
    if calculate_btn:
        st.session_state["show_report"] = True
        # 強制重新產生新的食譜快取
        if "meal_plan" in st.session_state:
            del st.session_state["meal_plan"]
        if "weekly_plan" in st.session_state:
            del st.session_state["weekly_plan"]
            
    if st.session_state.get("show_report", False):
        # 1. 倫理與生理邊界保護：未滿 18 歲青少年保護
        is_youth = age < 18
        actual_goal = "maintenance" if (is_youth and goal == "fat_loss") else goal
            
        gender_en = "male" if gender_input == "男生" else "female"
        bmr = calculate_bmr(gender_en, weight, height, age)
        tdee = calculate_tdee(bmr, activity_multiplier)
        macros = calculate_macros(tdee, actual_goal, diet_type)
        bmi_data = calculate_bmi(weight, height)
        water_min, water_max = calculate_water(weight, activity_multiplier, actual_goal)
        
        # 2. 生理極端數值安全防護網警示 (Safety Guardrails)
        min_safe_cal = 1200 if gender_en == "female" else 1500
        
        # 置頂醒目免責聲明橫幅 (倫理合規最高防線)
        st.warning(
            "**系統聲明與使用須知 (Disclaimer)**：本報告依據 WHO、ACSM 與衛福部國健署之公共衛生常規指引推算，旨在提供日常生活型態與體適能之輔助參考，"
            "**非屬個別醫療診斷或治療處方，亦不可取代醫師或營養師之臨床診療**。若有慢性病、受傷病史、孕哺期或急性不適，請務必尋求合格醫療專業團隊評估。"
        )
        
        st.success("計算成功！以下為依據公共衛生科學模型推算之生活型態健康分析報告：")
        
        # 醫療安全防護警示區塊
        if is_youth:
            st.warning("**青少年發育期保護提醒**：您目前未滿 18 歲，發育成長期間強烈不建議進行熱量赤字或節食。系統已將您的目標自動切換為「充足營養配置」，請著重於均衡營養與規律睡眠！")
            
        if macros['target_calories'] < bmr or macros['target_calories'] < min_safe_cal:
            st.error(
                f"**生理代謝安全警示**：您當前的目標建議熱量（**{macros['target_calories']} 大卡**）"
                f"已低於基礎代謝率 (BMR: {bmr:.1f} 大卡) 或人體最低生理安全底線 ({min_safe_cal} 大卡)。"
                "長期熱量赤字過大易引發基礎代謝適應性下降、肌肉損耗及甲狀腺/性腺荷爾蒙紊亂。強烈建議每日攝取不低於 BMR，或在合格營養師監督下進行。"
            )
            
        if bmi_data["bmi"] < 16.0 or bmi_data["bmi"] >= 35.0:
            st.error(
                f"**極端體位安全警示**：您的 BMI 為 **{bmi_data['bmi']}** ({bmi_data['status']})，已超出一般日常健康促進工具之建議範疇。"
                "強烈建議優先至大醫院之新陳代謝科或體重管理門診，由跨專科臨床醫師與營養師團隊進行深入生理評估。"
            )

        # 預先生成食譜資料快取
        if "meal_plan" not in st.session_state:
            st.session_state["meal_plan"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)
        exercise_plan = generate_exercise_plan(weight, activity_label, actual_goal)
        
        # 報告子分頁
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["生理數據總覽", "日常飲食搭配參考", "日常活動量建議"])
        
        with sub_tab1:
            st.subheader("核心生理指標分析")
            
            # 第一列：BMI、健康體位判定與理想體重
            col_b1, col_b2, col_b3 = st.columns(3)
            col_b1.metric(label="身體質量指數 (BMI)", value=f"{bmi_data['bmi']}")
            col_b2.metric(label="健康體位判定 (衛福部標準)", value=f"{bmi_data['status']}")
            col_b3.metric(label="身高理想體重區間", value=f"{bmi_data['ideal_min']} ～ {bmi_data['ideal_max']} kg")
            
            st.caption(f"**體位衛教說明**：{bmi_data['advice']}")
            st.divider()
            
            # 第二列：BMR, TDEE, 目標熱量與水分
            col_res1, col_res2, col_res3, col_res4 = st.columns(4)
            col_res1.metric(label="基礎代謝率 (BMR)", value=f"{bmr:.1f} 大卡")
            col_res2.metric(label="每日總消耗量 (TDEE)", value=f"{tdee:.1f} 大卡")
            col_res3.metric(label="每日建議攝取熱量", value=f"{macros['target_calories']} 大卡")
            glasses_approx = round(water_min / 250)
            col_res4.metric(label="每日建議飲水量", value=f"{water_min} ～ {water_max} ml", help=f"約為 {glasses_approx} ～ {glasses_approx+2} 杯馬克杯水量 (以 250ml/杯 計算)。建議定時小口慢飲，茶或黑咖啡不可完全取代純水。")
            
            st.divider()
            
            # 巨量營養素比例與詳細數據
            col_chart, col_details = st.columns([2, 1])
            
            with col_chart:
                st.subheader(f"三大營養素熱量佔比 ({diet_type})")
                df_macros = pd.DataFrame({
                    "營養素": ["碳水化合物", "蛋白質", "脂肪"],
                    "克數 (g)": [macros['carbs_g'], macros['protein_g'], macros['fat_g']],
                    "熱量百分比": [f"{macros['carbs_ratio']}%", f"{macros['protein_ratio']}%", f"{macros['fat_ratio']}%"]
                })
                fig = px.pie(
                    df_macros,
                    values="克數 (g)",
                    names="營養素",
                    hole=0.42,
                    hover_data=["熱量百分比"],
                    color="營養素",
                    color_discrete_map={"碳水化合物": "#ff7675", "蛋白質": "#74b9ff", "脂肪": "#55efc4"}
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(margin=dict(t=20, b=20, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)
                
            with col_details:
                st.subheader("營養素詳細克數")
                st.metric(label=f"碳水化合物 ({macros['carbs_ratio']}%)", value=f"{macros['carbs_g']} g")
                st.metric(label=f"蛋白質 ({macros['protein_ratio']}%)", value=f"{macros['protein_g']} g")
                st.metric(label=f"脂肪 ({macros['fat_ratio']}%)", value=f"{macros['fat_g']} g")
                
                if "生酮" in diet_type:
                    st.caption("**生酮飲食模式**：大幅限制碳水化合物至 10% 以下，提高健康優質油脂以促使身體運用酮體供能。")
                elif "地中海" in diet_type:
                    st.caption("**地中海飲食模式**：著重未精製全穀、深海魚類優質蛋白與初榨橄欖油好油。")
        
        with sub_tab2:
            st.subheader(f"{diet_type} ｜ 日常生活菜單搭配參考")
            st.markdown(f"為滿足您每日約 **{macros['target_calories']} 大卡** 的熱量目標，系統為您動態配置了以下菜單分量：")
            
            if is_youth:
                st.info("**發育期加碼建議**：每天建議額外攝取 1～2 杯牛奶（或無糖豆漿），以確保充足的鈣質與優質蛋白幫助骨骼成長！")
                
            plan_mode = st.radio("菜單顯示模式", ["今日三餐搭配 (可個別換菜)", "一週七天菜單 (週一至週日)"], horizontal=True)
            
            if "今日三餐搭配" in plan_mode:
                # 早餐
                col_b_btn, col_b_text = st.columns([1, 6])
                with col_b_btn:
                    if st.button("換早餐", use_container_width=True):
                        st.session_state["meal_plan"]["早餐"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)["早餐"]
                        st.rerun()
                with col_b_text:
                    st.info(f"**早餐**：\n\n{st.session_state['meal_plan']['早餐']}")
                    
                # 午餐
                col_l_btn, col_l_text = st.columns([1, 6])
                with col_l_btn:
                    if st.button("換午餐", use_container_width=True):
                        st.session_state["meal_plan"]["午餐"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)["午餐"]
                        st.rerun()
                with col_l_text:
                    st.warning(f"**午餐**：\n\n{st.session_state['meal_plan']['午餐']}")
                    
                # 晚餐
                col_d_btn, col_d_text = st.columns([1, 6])
                with col_d_btn:
                    if st.button("換晚餐", use_container_width=True):
                        st.session_state["meal_plan"]["晚餐"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)["晚餐"]
                        st.rerun()
                with col_d_text:
                    st.success(f"**晚餐**：\n\n{st.session_state['meal_plan']['晚餐']}")
            else:
                # 一週七天菜單模式
                if st.button("重新配置整週七天菜單", type="secondary"):
                    st.session_state["weekly_plan"] = generate_weekly_meal_plan(diet_type, macros['target_calories'], restrictions)
                    st.rerun()
                    
                if "weekly_plan" not in st.session_state:
                    st.session_state["weekly_plan"] = generate_weekly_meal_plan(diet_type, macros['target_calories'], restrictions)
                    
                week_tabs = st.tabs(list(st.session_state["weekly_plan"].keys()))
                for w_tab, day_name in zip(week_tabs, st.session_state["weekly_plan"].keys()):
                    with w_tab:
                        day_meals = st.session_state["weekly_plan"][day_name]
                        st.markdown(f"#### {day_name} 菜單規劃")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.info(f"**早餐**\n\n{day_meals['早餐']}")
                        with col2:
                            st.warning(f"**午餐**\n\n{day_meals['午餐']}")
                        with col3:
                            st.success(f"**晚餐**\n\n{day_meals['晚餐']}")
            
            # 一鍵複製今日菜單功能 (使用 st.code 內建之複製按鈕)
            st.divider()
            st.markdown("**一鍵複製今日菜單文字 (點擊程式碼區塊右上角圖標即可快速複製，方便傳至 LINE 或筆記)**：")
            copy_content = (
                f"【{diet_type} 今日健康菜單 ｜ 目標 {macros['target_calories']} kcal】\n"
                f"早餐：\n{st.session_state['meal_plan']['早餐'].replace('*', '')}\n\n"
                f"午餐：\n{st.session_state['meal_plan']['午餐'].replace('*', '')}\n\n"
                f"晚餐：\n{st.session_state['meal_plan']['晚餐'].replace('*', '')}\n\n"
                f"今日建議飲水量：{water_min} ～ {water_max} ml\n"
                f"本內容僅供自主健康管理生活參考，非醫療處方。"
            )
            st.code(copy_content, language="markdown")
        
        with sub_tab3:
            st.subheader("日常活動量與生活處方 (WHO / ACSM 實證指引)")
            st.markdown(
                "**運動醫學核心原則**：體態與體重控制中，能量赤字 **80% 取決於飲食管理，20% 來自運動調節**。"
                "運動的核心價值在於**刺激心肺適能、提升最大攝氧量 ($VO_2\\max$)、維持瘦肉組織（防止代謝適應衰退）**，而非盲目線性抵銷熱量。"
                "國際運動醫學會強烈建議將以下三大生活處方融入每週規劃："
            )
            
            if is_youth:
                st.info("**青少年體適能加碼建議**：除了日常步數外，強烈建議每週安排「跳繩、打籃球」等縱向跳躍活動，促進生長板物理刺激！")

            st.info(f"**模組一：日常微活動量 (NEAT ｜ 步數甜蜜點與少坐多動)**  \n{exercise_plan['option_a']}")
            st.warning(f"**模組二：心肺適能連續訓練 (Cardiorespiratory Fitness)**  \n{exercise_plan['option_b']}")
            st.success(f"**模組三：骨骼肌肉抗阻訓練 (Resistance Training ｜ 守住代謝)**  \n{exercise_plan['option_c']}")
        
        # 下載報告區塊
        st.divider()
        
        report_text = f"=== 個人化智慧健康與生活數據分析報告 ===\n"
        report_text += f"【醫學倫理與免責聲明】\n"
        report_text += f"本報告由自主學習專案系統自動生成，所有數值與建議均依據公開公衛文獻推算，\n"
        report_text += f"非屬醫療診斷或治療處方，亦不能替代合格醫師或執業營養師之專業臨床諮詢。\n"
        report_text += f"若有特殊生理狀況、受傷病史或身體不適，請務必尋求醫療專業人員協助。\n\n"
        report_text += f"[ 生理指標評估 ]\n"
        report_text += f"身體質量指數 (BMI): {bmi_data['bmi']} ({bmi_data['status']})\n"
        report_text += f"理想體重區間: {bmi_data['ideal_min']} ～ {bmi_data['ideal_max']} kg\n"
        report_text += f"基礎代謝率 (BMR): {bmr:.1f} 大卡\n"
        report_text += f"每日總消耗量 (TDEE): {tdee:.1f} 大卡\n"
        report_text += f"每日建議攝取熱量: {macros['target_calories']} 大卡\n"
        report_text += f"每日建議飲水量: {water_min} ～ {water_max} 毫升\n\n"
        report_text += f"[ 營養素目標分配 ({diet_type}) ]\n"
        report_text += f"碳水化合物 ({macros['carbs_ratio']}%): {macros['carbs_g']} g\n"
        report_text += f"蛋白質 ({macros['protein_ratio']}%): {macros['protein_g']} g\n"
        report_text += f"脂肪 ({macros['fat_ratio']}%): {macros['fat_g']} g\n\n"
        report_text += f"[ 三餐搭配參考 ]\n"
        report_text += f"早餐：\n{st.session_state['meal_plan']['早餐'].replace('*', '')}\n\n"
        report_text += f"午餐：\n{st.session_state['meal_plan']['午餐'].replace('*', '')}\n\n"
        report_text += f"晚餐：\n{st.session_state['meal_plan']['晚餐'].replace('*', '')}\n\n"
        report_text += f"[ 日常活動量與生活處方 (WHO / ACSM 實證指引) ]\n"
        report_text += f"醫學核心: 80%靠飲食管理，運動著重改善心肺適能與維持瘦肉組織防代謝衰退\n\n"
        report_text += f"模組一 (日常微活動 NEAT):\n{exercise_plan['option_a'].replace('*', '')}\n\n"
        report_text += f"模組二 (心肺適能連續訓練):\n{exercise_plan['option_b'].replace('*', '')}\n\n"
        report_text += f"模組三 (骨骼肌肉抗阻訓練):\n{exercise_plan['option_c'].replace('*', '')}\n"
        
        st.download_button(
            label="一鍵下載專屬健康與飲食分析報告 (.txt)",
            data=report_text,
            file_name="Personal_Health_Report.txt",
            mime="text/plain",
            type="primary"
        )
            
    else:
        st.info(
            "請在左側側邊欄輸入生理數值與目標，並點擊「開始計算健康報告」。\n\n"
            "**手機端用戶貼心小提醒**：若未看見輸入選單，請點擊畫面左上角的 **`>` 箭頭符號**，即可展開側邊欄填寫資料！"
        )

with tab_data:
    st.header("穿戴式裝置數據分析 (Wearable Data Analytics)")
    st.markdown(
        "本模組支援匯入 Apple Watch 或 Garmin 之每日運動與體適能紀錄 (CSV 格式)，"
        "系統將以真實活動消耗自動校正活動量係數，取代傳統粗估填答！"
    )
    
    col_demo, col_blank = st.columns([2, 5])
    with col_demo:
        load_sample = st.button("快速體驗：載入 Apple Watch 7 天範例數據", use_container_width=True)
        
    uploaded_file = st.file_uploader("上傳您的個人運動數據 (CSV 格式)", type=["csv"])
    
    df = None
    if load_sample:
        # 生成擬真 7 天 Apple Watch 數據
        today = datetime.date.today()
        dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        sample_data = {
            "Date": dates,
            "Active_Calories (kcal)": [420, 560, 310, 480, 620, 510, 450],
            "Total_Steps (步)": [8400, 10200, 6300, 9100, 11800, 9900, 8800],
            "Exercise_Minutes (分鐘)": [35, 52, 25, 45, 60, 48, 40],
            "Avg_Heart_Rate (bpm)": [118, 132, 110, 126, 138, 129, 122]
        }
        df = pd.DataFrame(sample_data)
        st.session_state["loaded_sample_df"] = df
        st.success("已成功載入 Apple Watch 7 日擬真運動數據！")
    elif "loaded_sample_df" in st.session_state and uploaded_file is None:
        df = st.session_state["loaded_sample_df"]
    elif uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("成功讀取上傳檔案！")
        except Exception as e:
            st.error(f"讀取失敗：{e}")
            
    if df is not None:
        st.markdown("### 數據預覽")
        st.dataframe(df, use_container_width=True)
        
        # 尋找熱量與步數相關欄位
        cal_cols = [c for c in df.columns if any(k in c.lower() for k in ['cal', '熱量', '消耗', 'active'])]
        step_cols = [c for c in df.columns if any(k in c.lower() for k in ['step', '步數', '步'])]
        date_cols = [c for c in df.columns if any(k in c.lower() for k in ['date', 'day', '日期', '時間'])]
        
        if cal_cols:
            cal_col = cal_cols[0]
            avg_cal = float(df[cal_col].mean())
            max_cal = float(df[cal_col].max())
            min_cal = float(df[cal_col].min())
            
            # 指標卡片
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("每日平均活動消耗", f"{avg_cal:.1f} 大卡")
            m_col2.metric("單日最高活動消耗", f"{max_cal:.1f} 大卡")
            m_col3.metric("單日最低活動消耗", f"{min_cal:.1f} 大卡")
            
            # 7 天活動走勢圖 (Plotly 折線圖 + 平均基準線)
            x_axis = df[date_cols[0]] if date_cols else df.index
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=x_axis,
                y=df[cal_col],
                name="每日活動熱量 (kcal)",
                marker_color="#ff7675"
            ))
            fig_trend.add_hline(
                y=avg_cal,
                line_dash="dash",
                line_color="#0984e3",
                annotation_text=f"7 日平均線: {avg_cal:.1f} kcal",
                annotation_position="bottom right"
            )
            fig_trend.update_layout(
                title="每日活動能量消耗走勢與基準線",
                xaxis_title="日期",
                yaxis_title="活動消耗 (kcal)",
                margin=dict(t=40, b=20, l=10, r=10)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 自動推算建議活動量級距
            if avg_cal < 200:
                rec_act_label = "久坐 (幾乎不運動)"
                rec_desc = "日常活動量偏低，建議從微習慣每日 6000 步開始養成。"
            elif avg_cal < 400:
                rec_act_label = "輕度活動 (每週 1～3 天)"
                rec_desc = "具備基礎日常活動量，建議維持並漸進增加規律運動。"
            elif avg_cal < 700:
                rec_act_label = "中度活動 (每週 3～5 天)"
                rec_desc = "活動量相當充實健康，能有效促進心肺耐力與代謝健康！"
            else:
                rec_act_label = "高度活動 (每週 6～7 天)"
                rec_desc = "高強度體能消耗者，請特別注意補充充足水分與碳水化合物以利恢復。"
                
            st.info(f"**AI 數據洞察**：根據您的穿戴裝置紀錄，系統建議活動量等級為：**{rec_act_label}**\n\n*{rec_desc}*")
            
            if st.button("一鍵套用此活動量至計算機 (自動更新側邊欄設定)", type="primary"):
                st.session_state["activity_choice"] = rec_act_label
                st.session_state["show_report"] = True
                st.toast(f"已自動更新活動量為「{rec_act_label}」！")
                st.rerun()
        else:
            st.warning("未能從上傳的 CSV 中識別出熱量相關欄位（例如：Calories、熱量、Active_Calories），請確認檔案格式。")
