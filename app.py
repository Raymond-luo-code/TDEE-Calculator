import streamlit as st
from calculator import calculate_bmr, calculate_tdee, calculate_macros
import plotly.express as px
import pandas as pd
import random

# 建立各飲食法的食材資料庫 (品項, 基準份量, 單位)
FOOD_DATABASE = {
    "均衡飲食 (Balanced)": {
        "carbs": [("燕麥片", 0.5, "碗"), ("糙米飯", 0.8, "碗"), ("地瓜", 1, "個拳頭大"), ("全麥麵包", 2, "片")],
        "protein": [("水煮蛋", 1.5, "顆"), ("烤雞胸肉", 1, "個手掌大"), ("無糖豆漿", 1, "杯"), ("烤鮭魚", 1, "個手掌大"), ("低脂鮮奶", 1, "杯")],
        "fat": [("綜合堅果", 1, "小把"), ("酪梨", 0.3, "顆"), ("特級初榨橄欖油", 2, "茶匙"), ("芝麻醬", 2, "茶匙")],
        "veggies": [("燙高麗菜", 1, "碗"), ("綜合生菜沙拉", 1, "大盤"), ("烤櫛瓜", 1, "碗"), ("花椰菜", 1, "碗")]
    },
    "地中海飲食 (Mediterranean)": {
        "carbs": [("藜麥", 0.5, "碗"), ("全麥麵包", 2, "片"), ("鷹嘴豆", 0.5, "碗"), ("燕麥", 0.5, "碗")],
        "protein": [("煎鯛魚", 1, "個手掌大"), ("烤雞腿排(去皮)", 1, "個手掌大"), ("希臘優格", 1, "小碗"), ("毛豆", 0.5, "碗")],
        "fat": [("特級初榨橄欖油", 1, "湯匙"), ("無調味綜合堅果", 1, "小把"), ("酪梨", 0.5, "顆")],
        "veggies": [("番茄酪梨沙拉", 1, "盤"), ("橄欖油大蒜烤蔬菜", 1, "盤"), ("菠菜沙拉", 1, "盤")]
    },
    "生酮飲食 (Keto)": {
        "carbs": [("花椰菜米", 1, "碗"), ("櫛瓜麵", 1, "大碗"), ("低碳蒟蒻麵", 1, "份")], # 以極低碳水蔬菜替代主食
        "protein": [("帶皮烤雞腿", 1, "支"), ("肋眼牛排", 1, "個手掌大"), ("炒蛋", 3, "顆"), ("香煎鮭魚", 1.5, "個手掌大"), ("厚切培根", 2, "片")],
        "fat": [("草飼奶油", 1, "湯匙"), ("酪梨", 0.5, "顆"), ("MCT油", 2, "茶匙"), ("起司片", 2, "片")],
        "veggies": [("奶油炒蘑菇", 1, "盤"), ("橄欖油拌菠菜", 1, "盤"), ("奶油烤蘆筍", 1, "把")]
    }
}

def generate_meal_plan(diet_type, target_calories):
    """根據飲食法與目標熱量，從資料庫中隨機挑選食材並動態調整份量"""
    scale = target_calories / 1500.0
    # 取得對應飲食法的資料庫，若找不到則預設給均衡飲食
    db = FOOD_DATABASE.get(diet_type, FOOD_DATABASE["均衡飲食 (Balanced)"])
    
    meals = {}
    for meal_name in ["早餐", "午餐", "晚餐"]:
        # 隨機挑選各類別的一種食材
        carb = random.choice(db["carbs"])
        prot = random.choice(db["protein"])
        fat = random.choice(db["fat"])
        veg = random.choice(db["veggies"])
        
        # 依照熱量比例計算實際份量
        carb_qty = round(carb[1] * scale, 1)
        prot_qty = round(prot[1] * scale, 1)
        fat_qty = round(fat[1] * scale, 1)
        
        # 去除小數點 .0 讓畫面更乾淨
        carb_qty = int(carb_qty) if carb_qty.is_integer() else carb_qty
        prot_qty = int(prot_qty) if prot_qty.is_integer() else prot_qty
        fat_qty = int(fat_qty) if fat_qty.is_integer() else fat_qty
        
        # 組合成文字回傳
        meals[meal_name] = (
            f"🌾 主食：{carb[0]} **{carb_qty}** {carb[2]}  \n"
            f"🥩 蛋白質：{prot[0]} **{prot_qty}** {prot[2]}  \n"
            f"🥑 優質油脂：{fat[0]} **{fat_qty}** {fat[2]}  \n"
            f"🥬 蔬菜：{veg[0]} (隨意吃到飽)"
        )
        
    return meals

# --- 1. 網頁標題與設定 ---
st.set_page_config(page_title="TDEE 計算器", page_icon="💪", layout="wide")
st.title("💪 個人化智慧 TDEE 計算器")
st.markdown("這是一個由 **Raymond** 與 **Andy** 共同開發的健康數據分析系統！")
st.divider()

# --- 2. 側邊欄 (Sidebar) 輸入區 ---
with st.sidebar:
    st.header("📝 生理數據設定")
    gender_input = st.radio("您的性別是？", options=["男生", "女生"])
    age = st.number_input("年齡 (歲)", min_value=1, max_value=120, value=20)
    height = st.number_input("身高 (cm)", min_value=50, max_value=250, value=170)
    weight = st.number_input("體重 (kg)", min_value=20, max_value=300, value=60)
    
    st.divider()
    st.header("🎯 目標設定")
    
    activity_options = {
        "久坐 (幾乎不運動)": 1.2,
        "輕度活動 (每週 1-3 天)": 1.375,
        "中度活動 (每週 3-5 天)": 1.55,
        "高度活動 (每週 6-7 天)": 1.725,
        "極度活動 (勞力密集)": 1.9
    }
    activity_label = st.selectbox("活動量", options=activity_options.keys())
    activity_multiplier = activity_options[activity_label]
    
    goal_options = {
        "減脂 (Fat Loss)": "fat_loss",
        "維持 (Maintenance)": "maintenance",
        "增肌 (Muscle Gain)": "muscle_gain"
    }
    goal_label = st.selectbox("您的目標", options=goal_options.keys())
    goal = goal_options[goal_label]

    diet_type = st.selectbox("飲食偏好", options=["均衡飲食 (Balanced)", "地中海飲食 (Mediterranean)", "生酮飲食 (Keto)"])

    calculate_btn = st.button("🚀 開始計算", type="primary", use_container_width=True)

# --- 3. 主畫面分頁 (Tabs) ---
tab_report, tab_data = st.tabs(["📊 健康數據報告", "📂 穿戴裝置數據匯入"])

with tab_report:
    if calculate_btn:
        gender_en = "male" if gender_input == "男生" else "female"
        bmr = calculate_bmr(gender_en, weight, height, age)
        tdee = calculate_tdee(bmr, activity_multiplier)
        macros = calculate_macros(tdee, goal)
        
        st.success("計算成功！以下是您的專屬報告：")
        
        # 使用欄位來排版數字卡片
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric(label="基礎代謝率 (BMR)", value=f"{bmr:.1f} 大卡")
        col_res2.metric(label="每日總消耗量 (TDEE)", value=f"{tdee:.1f} 大卡")
        col_res3.metric(label="🎯 每日建議攝取熱量", value=f"{macros['target_calories']} 大卡")
        
        st.divider()
        
        # 互動式圖表與營養素詳細數據
        col_chart, col_details = st.columns([2, 1])
        
        with col_chart:
            st.subheader("三大營養素比例")
            df_macros = pd.DataFrame({
                "營養素": ["碳水化合物", "蛋白質", "脂肪"],
                "克數 (g)": [macros['carbs_g'], macros['protein_g'], macros['fat_g']]
            })
            fig = px.pie(df_macros, values="克數 (g)", names="營養素", hole=0.4, 
                         color_discrete_sequence=['#ff9999', '#66b3ff', '#99ff99'])
            st.plotly_chart(fig, use_container_width=True)
            
        with col_details:
            st.subheader("營養素詳細數據")
            st.metric(label="🍚 碳水化合物", value=f"{macros['carbs_g']} g")
            st.metric(label="🥩 蛋白質", value=f"{macros['protein_g']} g")
            st.metric(label="🥑 脂肪", value=f"{macros['fat_g']} g")
            
        st.divider()
        st.subheader(f"🍽️ {diet_type} - 專屬三餐食譜建議")
        st.markdown(f"為滿足您每日 **{macros['target_calories']} 大卡** 的需求，系統為您動態配置了以下食譜份量：")
        
        meal_plan = generate_meal_plan(diet_type, macros['target_calories'])
        
        st.info(f"**☀️ 早餐**：\n\n{meal_plan['早餐']}")
        st.warning(f"**🍱 午餐**：\n\n{meal_plan['午餐']}")
        st.success(f"**🌙 晚餐**：\n\n{meal_plan['晚餐']}")
        
        # 建立下載報告內容
        report_text = f"=== 專屬健康數據報告 ===\n"
        report_text += f"基礎代謝率 (BMR): {bmr:.1f} 大卡\n"
        report_text += f"每日總消耗量 (TDEE): {tdee:.1f} 大卡\n"
        report_text += f"🎯 每日建議攝取熱量: {macros['target_calories']} 大卡\n\n"
        report_text += f"[ 營養素分配 ]\n"
        report_text += f"🍚 碳水化合物: {macros['carbs_g']} g\n"
        report_text += f"🥩 蛋白質: {macros['protein_g']} g\n"
        report_text += f"🥑 脂肪: {macros['fat_g']} g\n\n"
        report_text += f"[ 🍽️ {diet_type} - 三餐食譜 ]\n"
        report_text += f"早餐：\n{meal_plan['早餐'].replace('*', '')}\n\n"
        report_text += f"午餐：\n{meal_plan['午餐'].replace('*', '')}\n\n"
        report_text += f"晚餐：\n{meal_plan['晚餐'].replace('*', '')}\n"
        
        st.divider()
        st.download_button(
            label="💾 一鍵下載專屬健康與食譜報告",
            data=report_text,
            file_name="TDEE_Meal_Plan.txt",
            mime="text/plain",
            type="primary"
        )
            
    else:
        st.info("👈 請在左側側邊欄輸入資料，並點擊「開始計算」。")

with tab_data:
    st.header("📂 穿戴裝置 CSV 檔案上傳")
    st.markdown("在這裡上傳 Apple Watch 或 Garmin 的運動紀錄 (需包含熱量或步數欄位)，系統將自動幫您推算活動量！")
    uploaded_file = st.file_uploader("上傳您的運動數據 (CSV 格式)", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("成功讀取檔案！以下是資料預覽：")
            st.dataframe(df.head())
            
            # 嘗試尋找熱量相關欄位
            cal_cols = [c for c in df.columns if 'cal' in c.lower() or '熱量' in c or '消耗' in c]
            if cal_cols:
                avg_cal = df[cal_cols[0]].mean()
                st.info(f"📊 **資料分析結果**：系統偵測到您的每日平均活動消耗約為 **{avg_cal:.1f} 大卡**！")
                
                # 自動推算建議
                if avg_cal < 200:
                    rec_act = "久坐 (幾乎不運動) [乘數: 1.2]"
                elif avg_cal < 400:
                    rec_act = "輕度活動 (每週 1-3 天) [乘數: 1.375]"
                elif avg_cal < 700:
                    rec_act = "中度活動 (每週 3-5 天) [乘數: 1.55]"
                else:
                    rec_act = "高度活動 (每週 6-7 天) 或 極度活動 [乘數: 1.725+]"
                    
                st.success(f"💡 **AI 建議**：根據您的真實數據，建議您在左側側邊欄的活動量選擇：**{rec_act}**")
            else:
                st.warning("未能自動識別熱量欄位，請確認 CSV 是否包含 'calories', '熱量' 等欄位。")
                
        except Exception as e:
            st.error(f"讀取失敗：{e}")
