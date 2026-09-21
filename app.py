import streamlit as st
from calculator import calculate_bmr, calculate_tdee, calculate_macros
import plotly.express as px
import pandas as pd
import random

# 建立各飲食法的食材資料庫 (品項, 基準份量, 單位)
FOOD_DATABASE = {
    "均衡飲食 (Balanced)": {
        "carbs_breakfast": [("燕麥片", 0.5, "碗"), ("全麥麵包", 2, "片"), ("地瓜", 1, "顆")],
        "carbs_main": [("糙米飯", 0.8, "碗"), ("地瓜", 1, "顆"), ("十穀米", 0.8, "碗")],
        "protein": [("水煮蛋", 1.5, "顆"), ("烤雞胸肉", 1, "塊"), ("無糖豆漿", 1, "杯"), ("烤鮭魚", 1, "片"), ("低脂鮮奶", 1, "杯")],
        "fat": [("綜合堅果", 1, "小把"), ("酪梨", 0.3, "顆"), ("特級初榨橄欖油", 2, "茶匙"), ("芝麻醬", 2, "茶匙")],
        "veggies": [("燙高麗菜", 1, "碗"), ("綜合生菜沙拉", 1, "大盤"), ("烤櫛瓜", 1, "碗"), ("花椰菜", 1, "碗")],
        "mixed_breakfast": [("總匯三明治", 1, "份"), ("鮪魚蛋餅", 1, "份")],
        "mixed_main": [("健康水煮便當", 1, "個"), ("雞肉生菜沙拉碗", 1, "份"), ("鮭魚壽司", 6, "貫")]
    },
    "地中海飲食 (Mediterranean)": {
        "carbs_breakfast": [("燕麥", 0.5, "碗"), ("全麥麵包", 2, "片")],
        "carbs_main": [("藜麥", 0.5, "碗"), ("鷹嘴豆", 0.5, "碗"), ("糙米", 0.5, "碗")],
        "protein": [("煎鯛魚", 1, "片"), ("烤雞腿排(去皮)", 1, "塊"), ("希臘優格", 1, "小碗"), ("毛豆", 0.5, "碗")],
        "fat": [("特級初榨橄欖油", 1, "湯匙"), ("無調味綜合堅果", 1, "小把"), ("酪梨", 0.5, "顆")],
        "veggies": [("番茄酪梨沙拉", 1, "盤"), ("橄欖油大蒜烤蔬菜", 1, "盤"), ("菠菜沙拉", 1, "盤")],
        "mixed_breakfast": [("優格燕麥罐", 1, "份")],
        "mixed_main": [("地中海烤魚餐盤", 1, "份"), ("雞肉皮塔餅(Pita)", 1, "份")]
    },
    "生酮飲食 (Keto)": {
        "carbs_breakfast": [("低碳蒟蒻麵", 1, "份")],
        "carbs_main": [("花椰菜米", 1, "碗"), ("櫛瓜麵", 1, "大碗"), ("低碳蒟蒻麵", 1, "份")], # 以極低碳水蔬菜替代主食
        "protein": [("帶皮烤雞腿", 1, "支"), ("肋眼牛排", 1, "塊"), ("炒蛋", 3, "顆"), ("香煎鮭魚", 1.5, "片"), ("厚切培根", 2, "片")],
        "fat": [("草飼奶油", 1, "湯匙"), ("酪梨", 0.5, "顆"), ("MCT油", 2, "茶匙"), ("起司片", 2, "片")],
        "veggies": [("奶油炒蘑菇", 1, "盤"), ("橄欖油拌菠菜", 1, "盤"), ("奶油烤蘆筍", 1, "把")],
        "mixed_breakfast": [("培根起司蛋捲", 1, "份")],
        "mixed_main": [("無骨牛小排生菜包", 1, "份"), ("起司烤雞腿排餐", 1, "份")]
    },
    "外食族 (Eating Out)": {
        "carbs_breakfast": [("吐司", 2, "片"), ("饅頭", 1, "顆"), ("蘿蔔糕", 2, "片")],
        "carbs_main": [("白飯", 0.8, "碗"), ("烏龍麵", 1, "碗"), ("乾麵", 1, "碗")],
        "protein": [("滷雞腿", 1, "支"), ("煎荷包蛋", 2, "顆"), ("茶葉蛋", 2, "顆"), ("白切肉", 1, "盤")],
        "fat": [("炒菜用油", 1, "份"), ("滷汁", 1, "份")],
        "veggies": [("燙青菜", 1, "盤"), ("涼拌小黃瓜", 1, "盤"), ("炒高麗菜", 1, "盤")],
        "mixed_breakfast": [("原味蛋餅", 1, "份"), ("火腿三明治", 1, "份"), ("肉鬆飯糰", 1, "個"), ("皮蛋瘦肉粥", 1, "碗")],
        "mixed_main": [("紅燒牛肉麵", 1, "碗"), ("肉絲炒飯", 1, "盤"), ("番茄肉醬義大利麵", 1, "份"), ("水餃", 10, "顆"), ("排骨便當", 1, "個")]
    }
}

def format_qty(qty, unit):
    """根據單位自動格式化數字，不可分割的單位強制四捨五入為整數"""
    discrete_units = ["顆", "片", "塊", "支", "份"]
    if unit in discrete_units:
        return max(1, round(qty))  # 至少給 1 單位
    else:
        res = round(qty, 1)
        return int(res) if res.is_integer() else res

def generate_meal_plan(diet_type, target_calories):
    """根據飲食法與目標熱量，從資料庫中隨機挑選食材並動態調整份量"""
    scale = target_calories / 1500.0
    # 取得對應飲食法的資料庫，若找不到則預設給均衡飲食
    db = FOOD_DATABASE.get(diet_type, FOOD_DATABASE["均衡飲食 (Balanced)"])
    
    # 從資料庫抽出不重複的食材 (肉類、油脂、蔬菜為三餐通用)
    prot_pool = random.sample(db["protein"], min(len(db["protein"]), 3))
    fat_pool = random.sample(db["fat"], min(len(db["fat"]), 3))
    veg_pool = random.sample(db["veggies"], min(len(db["veggies"]), 3))
    
    # 外食族有 80% 機率抽中綜合餐點，一般飲食有 30% 機率
    mixed_prob = 0.8 if "外食族" in diet_type else 0.3
    
    meals = {}
    meal_names = ["早餐", "午餐", "晚餐"]
    
    # 記錄已經用過的午晚餐，避免中餐跟晚餐吃到一樣的
    used_carbs_main = []
    used_mixed_main = []
    
    for i, meal_name in enumerate(meal_names):
        is_breakfast = (meal_name == "早餐")
        
        # 根據時段決定籤筒
        carbs_list = db.get("carbs_breakfast", []) if is_breakfast else db.get("carbs_main", [])
        mixed_list = db.get("mixed_breakfast", []) if is_breakfast else db.get("mixed_main", [])
        
        # 如果是正餐，過濾掉今天已經吃過的品項 (防呆機制)
        if not is_breakfast:
            avail_carbs = [c for c in carbs_list if c not in used_carbs_main]
            if not avail_carbs: avail_carbs = carbs_list  # 如果全部都吃過了就重置
            
            avail_mixed = [m for m in mixed_list if m not in used_mixed_main]
            if not avail_mixed: avail_mixed = mixed_list
        else:
            avail_carbs = carbs_list
            avail_mixed = mixed_list
            
        # 決定這一餐要吃綜合餐點還是標準拼盤
        is_mixed_meal = random.random() < mixed_prob and len(avail_mixed) > 0
        
        if is_mixed_meal:
            # 綜合餐點模式
            mixed_item = random.choice(avail_mixed)
            if not is_breakfast: 
                used_mixed_main.append(mixed_item)
                
            veg_item = veg_pool[i % len(veg_pool)]
            mixed_qty = format_qty(mixed_item[1] * scale, mixed_item[2])
            
            meal_lines = [
                f"🍲 綜合主餐：{mixed_item[0]} **{mixed_qty}** {mixed_item[2]}",
                f"🥬 搭配蔬菜：{veg_item[0]} (隨意吃到飽，確保纖維足夠)"
            ]
            meals[meal_name] = "  \n".join(meal_lines)
            
        else:
            # 標準拼盤模式
            carb = random.choice(avail_carbs)
            if not is_breakfast: 
                used_carbs_main.append(carb)
                
            prot = prot_pool[i % len(prot_pool)]
            fat = fat_pool[i % len(fat_pool)]
            veg = veg_pool[i % len(veg_pool)]
            
            carb_qty = format_qty(carb[1] * scale, carb[2])
            prot_qty = format_qty(prot[1] * scale, prot[2])
            fat_qty = format_qty(fat[1] * scale, fat[2])
            
            is_cooking_oil = any(k in fat[0] for k in ["油", "奶油", "醬"])
            
            # 智能減油機制：如果抽到高脂肉類，自動移除額外油脂
            high_fat_keywords = ["鮭魚", "牛排", "培根", "帶皮", "白切肉"]
            is_fatty_protein = any(k in prot[0] for k in high_fat_keywords)
            
            if is_fatty_protein:
                meal_lines = [
                    f"🌾 主食：{carb[0]} **{carb_qty}** {carb[2]}",
                    f"🥩 蛋白質：{prot[0]} **{prot_qty}** {prot[2]} (💡 富含油脂，本餐自動減油)",
                    f"🥬 蔬菜：{veg[0]} (建議水煮/清蒸，隨意吃到飽)"
                ]
            else:
                meal_lines = [
                    f"🌾 主食：{carb[0]} **{carb_qty}** {carb[2]}",
                    f"🥩 蛋白質：{prot[0]} **{prot_qty}** {prot[2]}"
                ]
                
                if is_cooking_oil:
                    meal_lines.append(f"🥬 蔬菜：{veg[0]} (建議搭配 {fat[0]} **{fat_qty}** {fat[2]} 烹調/拌沙拉)")
                else:
                    meal_lines.append(f"🥑 優質油脂/點心：{fat[0]} **{fat_qty}** {fat[2]}")
                    meal_lines.append(f"🥬 蔬菜：{veg[0]} (隨意吃到飽)")
                
            meals[meal_name] = "  \n".join(meal_lines)
        
    return meals

# --- 1. 網頁標題與設定 ---
st.set_page_config(page_title="TDEE 計算器", page_icon="💪", layout="wide", initial_sidebar_state="expanded")
st.title("💪 個人化智慧 TDEE 計算器")
st.markdown("這是一個由 **Raymond** 與 **Andy** 共同開發的健康數據分析系統！")
st.divider()

# --- 2. 側邊欄 (Sidebar) 輸入區 ---
with st.sidebar:
    st.header("📝 生理數據設定")
    gender_input = st.radio("您的性別是？", options=["男生", "女生"])
    age = st.number_input("年齡 (歲)", value=20)
    if age < 1 or age > 120:
        st.warning("⚠️ 提醒：您輸入的年齡數值超出一般常見範圍 (1~120歲)。")
        
    height = st.number_input("身高 (cm)", value=170)
    if height < 50 or height > 250:
        st.warning("⚠️ 提醒：您輸入的身高異常，可能會導致計算結果不準確。")
        
    weight = st.number_input("體重 (kg)", value=60)
    if weight < 20 or weight > 300:
        st.warning("⚠️ 提醒：您輸入的體重異常，可能會導致計算結果不準確。")
    
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

    diet_type = st.selectbox("飲食偏好", options=["均衡飲食 (Balanced)", "地中海飲食 (Mediterranean)", "生酮飲食 (Keto)", "外食族 (Eating Out)"])

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
        st.info(
            "👈 請在左側側邊欄輸入資料，並點擊「開始計算」。\n\n"
            "📱 **手機版用戶小提醒**：如果沒有看到輸入框，請點擊畫面左上角的 **`>` 箭頭符號**，就能打開隱藏的選單囉！"
        )

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
