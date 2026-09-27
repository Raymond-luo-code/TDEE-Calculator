import streamlit as st
from calculator import calculate_bmr, calculate_tdee, calculate_macros
import plotly.express as px
import pandas as pd
import random

# 建立各飲食法的食材資料庫 (品項, 基準份量, 單位)
FOOD_DATABASE = {
    "均衡飲食 (Balanced)": {
        "carbs_breakfast": [("燕麥片", 0.5, "碗"), ("全麥麵包", 2, "片"), ("地瓜", 1, "顆"), ("無糖麥片", 1, "碗"), ("貝果(原味)", 0.5, "個"), ("馬鈴薯", 1, "顆"), ("玉米", 1, "根")],
        "carbs_main": [("糙米飯", 0.8, "碗"), ("地瓜", 1, "顆"), ("十穀米", 0.8, "碗"), ("蕎麥麵", 1, "碗"), ("紫米飯", 0.8, "碗"), ("南瓜", 1, "碗"), ("五穀飯", 0.8, "碗")],
        "protein_breakfast": [("水煮蛋", 1.5, "顆"), ("無糖豆漿", 1, "杯"), ("低脂鮮奶", 1, "杯"), ("荷包蛋", 1.5, "顆"), ("優酪乳(無糖)", 1, "杯"), ("茶碗蒸", 1, "碗"), ("低脂起司", 2, "片")],
        "protein_main": [("烤雞胸肉", 1, "塊"), ("烤鮭魚", 1, "片"), ("滷牛腱", 1, "盤"), ("清蒸鱸魚", 1, "尾"), ("煎豆腐", 1, "塊"), ("豬里肌肉片", 1, "盤"), ("蒜泥白肉(瘦)", 1, "盤"), ("煎鯛魚", 1, "片")],
        "fat": [("綜合堅果", 1, "小把"), ("酪梨", 0.3, "顆"), ("特級初榨橄欖油", 2, "茶匙"), ("芝麻醬", 2, "茶匙"), ("南瓜子", 1, "小把"), ("核桃", 3, "顆"), ("花生醬", 1, "湯匙")],
        "veggies": [("燙高麗菜", 1, "碗"), ("綜合生菜沙拉", 1, "大盤"), ("烤櫛瓜", 1, "碗"), ("花椰菜", 1, "碗"), ("炒菠菜", 1, "碗"), ("涼拌木耳", 1, "盤"), ("玉米筍", 1, "碗"), ("秋葵", 1, "盤")],
        "mixed_breakfast": [("總匯三明治", 1, "份"), ("鮪魚蛋餅", 1, "份"), ("蔬菜起司烤土司", 1, "份"), ("雞肉生菜捲", 1, "份")],
        "mixed_main": [("健康水煮便當", 1, "個"), ("雞肉生菜沙拉碗", 1, "份"), ("鮭魚壽司", 6, "貫"), ("烤雞腿定食", 1, "份"), ("鮮蝦春捲", 3, "卷"), ("蕎麥冷麵套餐", 1, "份")]
    },
    "地中海飲食 (Mediterranean)": {
        "carbs_breakfast": [("燕麥", 0.5, "碗"), ("全麥麵包", 2, "片"), ("全麥皮塔餅", 1, "片"), ("雜糧吐司", 2, "片")],
        "carbs_main": [("藜麥", 0.5, "碗"), ("鷹嘴豆", 0.5, "碗"), ("糙米", 0.5, "碗"), ("蒜香義大利麵", 1, "碗"), ("烤馬鈴薯", 1, "顆"), ("紅腰豆", 0.5, "碗")],
        "protein_breakfast": [("希臘優格", 1, "小碗"), ("水煮蛋", 1.5, "顆"), ("炒蛋", 1.5, "顆"), ("原味優酪乳", 1, "杯")],
        "protein_main": [("煎鯛魚", 1, "片"), ("烤雞腿排(去皮)", 1, "塊"), ("毛豆", 0.5, "碗"), ("香煎鮭魚", 1, "片"), ("地中海烤蝦", 1, "盤"), ("燉扁豆", 1, "碗"), ("烤鱈魚", 1, "片")],
        "fat": [("特級初榨橄欖油", 1, "湯匙"), ("無調味綜合堅果", 1, "小把"), ("酪梨", 0.5, "顆"), ("黑橄欖", 5, "顆"), ("杏仁", 1, "小把"), ("奇亞籽", 1, "湯匙")],
        "veggies": [("番茄酪梨沙拉", 1, "盤"), ("橄欖油大蒜烤蔬菜", 1, "盤"), ("菠菜沙拉", 1, "盤"), ("烤洋蔥與甜椒", 1, "盤"), ("櫛瓜麵", 1, "碗"), ("羽衣甘藍沙拉", 1, "盤")],
        "mixed_breakfast": [("優格燕麥罐", 1, "份"), ("番茄起司烤麵包", 1, "份"), ("鷹嘴豆泥配皮塔餅", 1, "份")],
        "mixed_main": [("地中海烤魚餐盤", 1, "份"), ("雞肉皮塔餅(Pita)", 1, "份"), ("海鮮燉藜麥", 1, "份"), ("希臘沙拉配烤雞肉", 1, "份"), ("蔬菜燉鷹嘴豆", 1, "份")]
    },
    "生酮飲食 (Keto)": {
        "carbs_breakfast": [("低碳蒟蒻麵", 1, "份"), ("大黃瓜片", 1, "碗")],
        "carbs_main": [("花椰菜米", 1, "碗"), ("櫛瓜麵", 1, "大碗"), ("低碳蒟蒻麵", 1, "份"), ("海帶絲", 1, "碗"), ("白蘿蔔", 1, "碗")], # 以極低碳水蔬菜替代主食
        "protein_breakfast": [("炒蛋", 3, "顆"), ("厚切培根", 2, "片"), ("無糖杏仁奶", 1, "杯"), ("德式香腸", 2, "根")],
        "protein_main": [("帶皮烤雞腿", 1, "支"), ("肋眼牛排", 1, "塊"), ("香煎鮭魚", 1.5, "片"), ("五花肉片", 1, "盤"), ("烤鯖魚", 1, "尾"), ("煎鴨胸", 1, "片"), ("奶油煎干貝", 1, "盤")],
        "fat": [("草飼奶油", 1, "湯匙"), ("酪梨", 0.5, "顆"), ("MCT油", 2, "茶匙"), ("起司片", 2, "片"), ("夏威夷豆", 1, "小把"), ("橄欖油", 1, "湯匙"), ("椰子油", 1, "湯匙")],
        "veggies": [("奶油炒蘑菇", 1, "盤"), ("橄欖油拌菠菜", 1, "盤"), ("奶油烤蘆筍", 1, "把"), ("起司焗烤花椰菜", 1, "碗"), ("蒜香炒青江菜", 1, "盤"), ("培根炒高麗菜", 1, "盤")],
        "mixed_breakfast": [("培根起司蛋捲", 1, "份"), ("酪梨鮪魚沙拉", 1, "份"), ("防彈咖啡配水煮蛋", 1, "份")],
        "mixed_main": [("無骨牛小排生菜包", 1, "份"), ("起司烤雞腿排餐", 1, "份"), ("香煎鮭魚配蘆筍", 1, "份"), ("奶油胡椒蝦", 1, "盤"), ("五花肉炒青菜", 1, "份")]
    },
    "外食族 (Eating Out)": {
        "carbs_breakfast": [("吐司", 2, "片"), ("饅頭", 1, "顆"), ("蘿蔔糕", 2, "片"), ("飯糰", 1, "個"), ("鐵板麵", 1, "份"), ("肉包", 1, "顆")],
        "carbs_main": [("白飯", 0.8, "碗"), ("烏龍麵", 1, "碗"), ("乾麵", 1, "碗"), ("冬粉", 1, "碗"), ("滷肉飯", 1, "碗"), ("粄條", 1, "碗")],
        "protein_breakfast": [("煎荷包蛋", 2, "顆"), ("茶葉蛋", 2, "顆"), ("豆漿", 1, "杯"), ("火腿片", 2, "片")],
        "protein_main": [("滷雞腿", 1, "支"), ("白切肉", 1, "盤"), ("煎鯖魚", 1, "片"), ("炸排骨", 1, "塊"), ("蒜泥白肉", 1, "盤"), ("控肉", 1, "塊"), ("滷蛋與豆腐", 1, "份")],
        "fat": [("炒菜用油", 1, "份"), ("滷汁", 1, "份"), ("沙拉醬", 1, "包"), ("香油", 1, "茶匙")],
        "veggies": [("燙青菜", 1, "盤"), ("涼拌小黃瓜", 1, "盤"), ("炒高麗菜", 1, "盤"), ("滷海帶", 1, "盤"), ("燙地瓜葉", 1, "盤"), ("生菜沙拉(便利商店)", 1, "盒")],
        "mixed_breakfast": [("原味蛋餅", 1, "份"), ("火腿三明治", 1, "份"), ("肉鬆飯糰", 1, "個"), ("皮蛋瘦肉粥", 1, "碗"), ("豬肉滿福堡", 1, "個"), ("燒餅油條", 1, "份")],
        "mixed_main": [("紅燒牛肉麵", 1, "碗"), ("肉絲炒飯", 1, "盤"), ("番茄肉醬義大利麵", 1, "份"), ("水餃", 10, "顆"), ("排骨便當", 1, "個"), ("雞肉飯便當", 1, "個"), ("三寶飯", 1, "份"), ("大麥克套餐", 1, "份")]
    }
}

def format_qty(qty, unit):
    """根據單位自動格式化數字，不可分割的單位強制四捨五入為整數"""
    discrete_units = ["顆", "片", "塊", "支", "份", "尾", "卷", "個", "貫", "根", "包", "盒", "盤", "碗"]
    if unit in discrete_units:
        base = int(qty)
        frac = qty - base
        
        if base == 0:
            return "1"
            
        if frac >= 0.7:
            return str(base + 1)
        elif frac >= 0.3:
            if unit in ["盤", "碗"]:
                return f"{base} (建議可直接買大份)"
            else:
                return f"{base} (💡 若微餓可補充半顆茶葉蛋)"
        else:
            return str(base)
    elif unit == "杯":
        res = round(qty, 1)
        res_str = str(int(res)) if res.is_integer() else str(res)
        ml = int(res * 240)
        return f"{res_str} (約 {ml} 毫升)"
    else:
        res = round(qty, 1)
        return str(int(res)) if res.is_integer() else str(res)

def generate_meal_plan(diet_type, target_calories, restrictions=None):
    """根據飲食法與目標熱量，從資料庫中隨機挑選食材並動態調整份量"""
    if restrictions is None:
        restrictions = []
        
    scale = target_calories / 1500.0
    # 取得對應飲食法的資料庫，若找不到則預設給均衡飲食
    raw_db = FOOD_DATABASE.get(diet_type, FOOD_DATABASE["均衡飲食 (Balanced)"])
    
    # 定義過敏與禁忌關鍵字
    restriction_keywords = {
        "不吃海鮮": ["鮭魚", "鯛魚", "蝦", "魚"],
        "不吃牛肉": ["牛"],
        "不吃豬肉": ["肉絲", "排骨", "培根", "肉醬", "白切肉", "豬"],
        "堅果過敏": ["堅果", "芝麻"],
        "乳糖不耐 (不碰乳製品)": ["奶", "優格", "起司", "奶油"]
    }
    
    forbidden_words = []
    for r in restrictions:
        forbidden_words.extend(restriction_keywords.get(r, []))
        
    def is_allowed(item):
        return not any(bad_word in item[0] for bad_word in forbidden_words)
        
    db = {}
    for cat, items in raw_db.items():
        filtered_items = [item for item in items if is_allowed(item)]
        db[cat] = filtered_items if filtered_items else items # 若全部被過濾，給予保底
    
    # 蔬菜為三餐通用
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
                
            avail_prots = raw_db["protein_breakfast"] if is_breakfast else raw_db["protein_main"]
            # 過濾蛋白質
            avail_prots = [p for p in avail_prots if is_allowed(p[0])]
            if not avail_prots:
                avail_prots = [("低脂鮮奶" if is_breakfast else "烤雞胸肉", 1, "份")] # Fallback
                
            prot = random.choice(avail_prots)
            
            # 過濾脂肪
            avail_fats = [f for f in raw_db["fat"] if is_allowed(f[0])]
            if not avail_fats:
                avail_fats = [("橄欖油", 1, "份")]
            fat = random.choice(avail_fats)
            
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

def generate_exercise_plan(weight, activity_label, goal):
    """根據體重、活動量與目標，推算具體的運動建議"""
    
    # 決定基礎消耗目標
    target_burn = 200
    base_steps = 3000
    if "輕度" in activity_label:
        base_steps = 5000
    elif "中度" in activity_label:
        base_steps = 8000
    elif "高度" in activity_label:
        base_steps = 10000
    elif "極度" in activity_label:
        base_steps = 12000

    if "輕度" not in activity_label and "久坐" not in activity_label:
        target_burn = 350  # 有運動習慣的人目標調高
    
    if goal == "fat_loss":
        target_burn += 100  # 減脂期多消耗
    elif goal == "muscle_gain":
        target_burn -= 50   # 增肌期不過度消耗熱量
        
    # 計算具體指標
    # 1. 走路步數 (約略公式: 1公斤走1公里消耗0.7大卡，1公里約1400步)
    extra_walk_steps = int((target_burn / (weight * 0.7)) * 1400 / 100) * 100
    total_target_steps = base_steps + extra_walk_steps
    # 加上合理的每日步數上限 (一般人不建議超過 15000 步)
    total_target_steps = min(total_target_steps, 15000)
    # 將總步數四捨五入到最近的 500 步，看起來更像一個整齊的目標
    total_target_steps = round(total_target_steps / 500) * 500
    
    # 2. 爬樓梯 (1層樓約 15 階階梯，60公斤爬1層樓約消耗 2 大卡)
    stairs_burn_per_flight = 2.0 * (weight / 60.0)
    flights_of_stairs = int(target_burn / stairs_burn_per_flight)
    # 合理上限：一般人每天爬 20 層樓已經很厲害了
    flights_of_stairs = min(flights_of_stairs, 20)
    
    # 3. 慢跑 (1公斤跑1公里約消耗 1 大卡)
    jog_km = round(target_burn / (weight * 1.0), 1)
    
    # 4. 居家高強度間歇 HIIT / 燃脂操 (60公斤每分鐘約消耗 8 大卡)
    hiit_burn_per_min = 8.0 * (weight / 60.0)
    hiit_mins = int(target_burn / hiit_burn_per_min)
    
    # 分次完成建議
    steps_per_session = round(total_target_steps / 3 / 100) * 100  # 分3次，取百位整數
    stairs_per_session = max(1, round(flights_of_stairs / 3))       # 分3次
    hiit_per_session = max(5, round(hiit_mins / 2))                 # 分2次
    jog_per_session = round(jog_km / 2, 1)                          # 分2次
    
    return {
        "target_burn": target_burn,
        "option_a": f"每日目標總步數達 **{total_target_steps} 步** (包含日常通勤)，或額外爬 **{flights_of_stairs} 層樓** (每層約 15 階)  \n💡 建議分次完成：早中晚各走 **{steps_per_session} 步**，或分 3 次各爬 **{stairs_per_session} 層**",
        "option_b": f"每天在家跟做 YouTube 燃脂操或 HIIT 共 **{hiit_mins} 分鐘**，搭配簡單徒手深蹲  \n💡 建議分次完成：早晚各做 **{hiit_per_session} 分鐘**，輕鬆無壓力",
        "option_c": f"每天去公園或操場慢跑 **{jog_km} 公里**，或切換為快走 (距離需加倍)  \n💡 建議分次完成：早晚各跑 **{jog_per_session} 公里**，更容易持之以恆"
    }

# --- 1. 網頁標題與設定 ---
st.set_page_config(page_title="TDEE 計算器", page_icon="💪", layout="wide", initial_sidebar_state="expanded")
st.title("💪 個人化智慧 TDEE 計算器")
st.markdown("這是一個由 **Raymond** 與 **Andy** 共同開發的健康數據分析系統！")
st.divider()

# --- 2. 側邊欄 (Sidebar) 輸入區 ---
with st.sidebar:
    st.header("📝 生理數據設定")
    gender_input = st.radio("您的性別是？", options=["男生", "女生"], horizontal=True)
    
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
    st.header("🎯 目標設定")
    
    activity_options = {
        "久坐 (幾乎不運動)": 1.2,
        "輕度活動 (每週 1-3 天)": 1.375,
        "中度活動 (每週 3-5 天)": 1.55,
        "高度活動 (每週 6-7 天)": 1.725,
        "極度活動 (勞力密集)": 1.9
    }
    activity_label = st.radio("活動量", options=activity_options.keys())
    activity_multiplier = activity_options[activity_label]
    
    goal_options = {
        "減脂 (Fat Loss)": "fat_loss",
        "維持 (Maintenance)": "maintenance",
        "增肌 (Muscle Gain)": "muscle_gain"
    }
    goal_label = st.radio("您的目標", options=goal_options.keys())
    goal = goal_options[goal_label]

    diet_type = st.radio("飲食偏好", options=["均衡飲食 (Balanced)", "地中海飲食 (Mediterranean)", "生酮飲食 (Keto)", "外食族 (Eating Out)"])
    
    restrictions = st.multiselect("過敏與飲食禁忌", options=[
        "不吃海鮮", "不吃牛肉", "不吃豬肉", "堅果過敏", "乳糖不耐 (不碰乳製品)"
    ])

    calculate_btn = st.button("🚀 開始計算", type="primary", use_container_width=True)
    
    st.divider()
    st.header("⚙️ 顯示設定")
    font_size_label = st.select_slider("字體大小", options=["小", "中", "大", "特大"], value="大")

# --- 全域字體大小設定 ---
font_size_map = {"小": "14px", "中": "16px", "大": "19px", "特大": "22px"}
selected_font_size = font_size_map[font_size_label]
st.markdown(f"""
<style>
    /* 主內容區域 — 使用萬用選擇器確保所有文字都被覆蓋 */
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] span,
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] li,
    [data-testid="stAppViewContainer"] [data-testid="stVerticalBlockBorderWrapper"] label,
    [data-testid="stAppViewContainer"] [data-testid="stMetricValue"] > div,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li {{
        font-size: {selected_font_size} !important;
    }}
    
    /* 分頁標籤：加大加粗 */
    [data-testid="stAppViewContainer"] button[data-baseweb="tab"] {{
        font-size: {selected_font_size} !important;
        font-weight: 700 !important;
        padding: 12px 20px !important;
    }}
    
    /* 選中的分頁標籤加紅色底線高亮 */
    [data-testid="stAppViewContainer"] button[data-baseweb="tab"][aria-selected="true"] {{
        border-bottom: 3px solid #ff4b4b !important;
    }}

    /* 側邊欄維持原始大小 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {{
        font-size: 14px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. 主畫面分頁 (Tabs) ---
tab_report, tab_data = st.tabs(["📊 健康數據報告", "📂 穿戴裝置數據匯入"])

with tab_report:
    if calculate_btn:
        st.session_state["show_report"] = True
        # 按下開始計算時，強制重新產生新的食譜
        if "meal_plan" in st.session_state:
            del st.session_state["meal_plan"]
            
    if st.session_state.get("show_report", False):
        is_youth = age < 18
        actual_goal = "maintenance" if (is_youth and goal == "fat_loss") else goal
            
        gender_en = "male" if gender_input == "男生" else "female"
        bmr = calculate_bmr(gender_en, weight, height, age)
        tdee = calculate_tdee(bmr, activity_multiplier)
        macros = calculate_macros(tdee, actual_goal)
        
        st.success("計算成功！以下是您的專屬報告，請點擊下方分頁查看各項建議：")
        
        if is_youth:
            st.warning("⚠️ **青少年發育期提醒**：您目前未滿 18 歲，發育期間強烈不建議進行節食或熱量赤字。系統已將您的目標自動調整為「充足營養配置」，請著重於均衡飲食與規律運動！")
        
        # 預先產生資料，供各分頁共用
        if "meal_plan" not in st.session_state:
            st.session_state["meal_plan"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)
        exercise_plan = generate_exercise_plan(weight, activity_label, actual_goal)
        
        # 將報告拆成三個子分頁，讓每項建議都是同等地位
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📊 數據總覽", "🍽️ 飲食建議", "🏃‍♂️ 運動建議"])
        
        with sub_tab1:
            # 數字卡片
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
        
        with sub_tab2:
            st.subheader(f"🍽️ {diet_type} - 專屬三餐食譜建議")
            st.markdown(f"為滿足您每日 **{macros['target_calories']} 大卡** 的需求，系統為您動態配置了以下食譜份量：")
            
            if is_youth:
                st.info("💡 **發育期加碼建議**：每天建議額外攝取 1~2 杯牛奶（或無糖豆漿），以確保充足的鈣質與優質蛋白幫助長高！")
            
            # 早餐
            col_b_btn, col_b_text = st.columns([1, 6])
            with col_b_btn:
                if st.button("🔄 換早餐", use_container_width=True):
                    st.session_state["meal_plan"]["早餐"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)["早餐"]
            with col_b_text:
                st.info(f"**☀️ 早餐**：\n\n{st.session_state['meal_plan']['早餐']}")
                
            # 午餐
            col_l_btn, col_l_text = st.columns([1, 6])
            with col_l_btn:
                if st.button("🔄 換午餐", use_container_width=True):
                    st.session_state["meal_plan"]["午餐"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)["午餐"]
            with col_l_text:
                st.warning(f"**🍱 午餐**：\n\n{st.session_state['meal_plan']['午餐']}")
                
            # 晚餐
            col_d_btn, col_d_text = st.columns([1, 6])
            with col_d_btn:
                if st.button("🔄 換晚餐", use_container_width=True):
                    st.session_state["meal_plan"]["晚餐"] = generate_meal_plan(diet_type, macros['target_calories'], restrictions)["晚餐"]
            with col_d_text:
                st.success(f"**🌙 晚餐**：\n\n{st.session_state['meal_plan']['晚餐']}")
        
        with sub_tab3:
            st.subheader("🏃‍♂️ 專屬運動與生活建議")
            st.markdown(f"為達到您的健康目標，建議您每日可以額外消耗 **{exercise_plan['target_burn']} 大卡**，您可以從以下方案中「擇一」進行：")
            
            if is_youth:
                st.info("💡 **青少年專屬運動建議**：除了下方的日常活動外，強烈建議多做「跳繩、打籃球」等縱向跳躍運動，刺激生長板幫助長高！")

            st.info(f"**🚶 選項 A (微習慣養成)**：{exercise_plan['option_a']}")
            st.warning(f"**🏠 選項 B (居家運動)**：{exercise_plan['option_b']}")
            st.success(f"**🌳 選項 C (戶外運動)**：{exercise_plan['option_c']}")
        
        # 下載報告（放在分頁外面，任何分頁都看得到）
        st.divider()
        
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
        report_text += f"早餐：\n{st.session_state['meal_plan']['早餐'].replace('*', '')}\n\n"
        report_text += f"午餐：\n{st.session_state['meal_plan']['午餐'].replace('*', '')}\n\n"
        report_text += f"晚餐：\n{st.session_state['meal_plan']['晚餐'].replace('*', '')}\n\n"
        report_text += f"[ 🏃‍♂️ 專屬運動建議 ]\n"
        report_text += f"目標額外消耗: {exercise_plan['target_burn']} 大卡\n"
        report_text += f"選項 A (微習慣): {exercise_plan['option_a'].replace('*', '')}\n"
        report_text += f"選項 B (居家): {exercise_plan['option_b'].replace('*', '')}\n"
        report_text += f"選項 C (戶外): {exercise_plan['option_c'].replace('*', '')}\n"
        
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
