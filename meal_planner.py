"""
飲食與生活規劃模組 (meal_planner.py)
負責食材資料庫管理、動態份量換算、單日與每週飲食搭配生成、以及日常活動量建議推算。
"""
import random

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
        "carbs_main": [("花椰菜米", 1, "碗"), ("櫛瓜麵", 1, "大碗"), ("低碳蒟蒻麵", 1, "份"), ("海帶絲", 1, "碗"), ("白蘿蔔", 1, "碗")],
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
                return f"{base} (建議可直接點大份)"
            else:
                return f"{base} (💡 若微餓可補充半顆水煮蛋)"
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
    raw_db = FOOD_DATABASE.get(diet_type, FOOD_DATABASE["均衡飲食 (Balanced)"])
    
    # 定義過敏與禁忌關鍵字
    restriction_keywords = {
        "不吃海鮮": ["鮭魚", "鯛魚", "蝦", "魚", "干貝", "鱈魚"],
        "不吃牛肉": ["牛"],
        "不吃豬肉": ["肉絲", "排骨", "培根", "肉醬", "白切肉", "豬", "控肉", "香腸"],
        "堅果過敏": ["堅果", "芝麻", "核桃", "花生", "杏仁", "夏威夷豆"],
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
    
    veg_pool = random.sample(db["veggies"], min(len(db["veggies"]), 3))
    mixed_prob = 0.8 if "外食族" in diet_type else 0.3
    
    meals = {}
    meal_names = ["早餐", "午餐", "晚餐"]
    
    used_carbs_main = []
    used_mixed_main = []
    
    for i, meal_name in enumerate(meal_names):
        is_breakfast = (meal_name == "早餐")
        
        carbs_list = db.get("carbs_breakfast", []) if is_breakfast else db.get("carbs_main", [])
        mixed_list = db.get("mixed_breakfast", []) if is_breakfast else db.get("mixed_main", [])
        
        if not is_breakfast:
            avail_carbs = [c for c in carbs_list if c not in used_carbs_main]
            if not avail_carbs: avail_carbs = carbs_list
            
            avail_mixed = [m for m in mixed_list if m not in used_mixed_main]
            if not avail_mixed: avail_mixed = mixed_list
        else:
            avail_carbs = carbs_list
            avail_mixed = mixed_list
            
        is_mixed_meal = random.random() < mixed_prob and len(avail_mixed) > 0
        
        if is_mixed_meal:
            mixed_item = random.choice(avail_mixed)
            if not is_breakfast: 
                used_mixed_main.append(mixed_item)
                
            veg_item = veg_pool[i % len(veg_pool)]
            mixed_qty = format_qty(mixed_item[1] * scale, mixed_item[2])
            
            meal_lines = [
                f"🍲 綜合餐點：{mixed_item[0]} **{mixed_qty}** {mixed_item[2]}",
                f"🥬 搭配蔬菜：{veg_item[0]} (隨意吃飽，補充豐富膳食纖維)"
            ]
            meals[meal_name] = "  \n".join(meal_lines)
            
        else:
            carb = random.choice(avail_carbs)
            if not is_breakfast: 
                used_carbs_main.append(carb)
                
            avail_prots = raw_db["protein_breakfast"] if is_breakfast else raw_db["protein_main"]
            avail_prots = [p for p in avail_prots if is_allowed(p[0])]
            if not avail_prots:
                avail_prots = [("低脂鮮奶" if is_breakfast else "烤雞胸肉", 1, "份")]
                
            prot = random.choice(avail_prots)
            
            avail_fats = [f for f in raw_db["fat"] if is_allowed(f[0])]
            if not avail_fats:
                avail_fats = [("橄欖油", 1, "份")]
            fat = random.choice(avail_fats)
            
            veg = veg_pool[i % len(veg_pool)]
            
            carb_qty = format_qty(carb[1] * scale, carb[2])
            prot_qty = format_qty(prot[1] * scale, prot[2])
            fat_qty = format_qty(fat[1] * scale, fat[2])
            
            is_cooking_oil = any(k in fat[0] for k in ["油", "奶油", "醬"])
            
            high_fat_keywords = ["鮭魚", "牛排", "培根", "帶皮", "白切肉"]
            is_fatty_protein = any(k in prot[0] for k in high_fat_keywords)
            
            if is_fatty_protein:
                meal_lines = [
                    f"🌾 主食：{carb[0]} **{carb_qty}** {carb[2]}",
                    f"🥩 蛋白質：{prot[0]} **{prot_qty}** {prot[2]} (💡 富含油脂，建議本餐烹調減油)",
                    f"🥬 蔬菜：{veg[0]} (建議水煮或清蒸，攝取充足纖維)"
                ]
            else:
                meal_lines = [
                    f"🌾 主食：{carb[0]} **{carb_qty}** {carb[2]}",
                    f"🥩 蛋白質：{prot[0]} **{prot_qty}** {prot[2]}"
                ]
                
                if is_cooking_oil:
                    meal_lines.append(f"🥬 蔬菜：{veg[0]} (建議以 {fat[0]} **{fat_qty}** {fat[2]} 烹調/拌沙拉)")
                else:
                    meal_lines.append(f"🥑 優質油脂/點心：{fat[0]} **{fat_qty}** {fat[2]}")
                    meal_lines.append(f"🥬 蔬菜：{veg[0]} (隨意吃飽，確保纖維足夠)")
                
            meals[meal_name] = "  \n".join(meal_lines)
        
    return meals

def generate_weekly_meal_plan(diet_type, target_calories, restrictions=None):
    """生成週一至週日 (7天) 的生活型態菜單參考"""
    days = ["週一 (Mon)", "週二 (Tue)", "週三 (Wed)", "週四 (Thu)", "週五 (Fri)", "週六 (Sat)", "週日 (Sun)"]
    weekly_plan = {}
    for d in days:
        weekly_plan[d] = generate_meal_plan(diet_type, target_calories, restrictions)
    return weekly_plan

def generate_exercise_plan(weight, activity_label, goal):
    """
    根據 WHO 與 ACSM (美國運動醫學會) 實證指引，提供非線性、符合人體運動生理學的生活活動處方。
    拒絕單純以卡路里線性外推，考量邊際效益遞減、關節保護與連續 vs 分段運動之生理差異。
    """
    # 1. 步數甜蜜點判定 (依據 The Lancet Public Health 2022 統合分析：8,000 至 10,000 步為心血管與全因死亡率效益高原期)
    if "久坐" in activity_label:
        target_steps = "7,000 至 8,000"
        steps_advice = "初學者建議從每日 7,000 步建立基礎習慣，避免一次過量造成阿基里斯腱與足底負擔。"
    elif goal == "fat_loss" or "高度" in activity_label or "極度" in activity_label:
        target_steps = "8,500 至 10,000"
        steps_advice = "此區間為健康促進與代謝活躍的最佳甜蜜點。研究顯示超過 10,000 步後邊際效益顯著遞減，無需刻意追求極端高步數。"
    else:
        target_steps = "8,000 至 9,000"
        steps_advice = "維持穩定的 8,000 至 9,000 步即可獲得絕佳的心血管與代謝維持效益。"

    # 2. 樓梯與關節保護 (3 至 5 層樓，避免過度壓迫髕骨股骨關節面)
    stairs_flights = "3 至 5"
    
    # 3. WHO 心肺適能建議 (每週 150 分鐘中強度)
    cardio_mins = 30 if goal == "fat_loss" else 25
    cardio_days = 4 if goal == "fat_loss" else 3
    
    # 4. ACSM 阻力訓練建議 (維持無脂肪體重，避免減脂期掉肌肉導致代謝降低)
    strength_focus = "徒手深蹲、分腿蹲、伏地挺身或核心棒式" if "久坐" in activity_label else "深蹲、硬舉、推胸與引體向上等大肌群多關節動作"
    
    return {
        "guideline_title": "WHO / ACSM 運動醫學指引：日常微活動 + 每週 150 分鐘心肺 + 2 天肌力維護",
        "option_a": (
            f"**每日步數目標：{target_steps} 步**  \n"
            f"• 💡 **科學實證依據**：{steps_advice}  \n"
            f"• 🪜 **關節友善爬樓梯**：每日僅需累計 **{stairs_flights} 層樓**（如搭捷運或上班時走 1 至 2 段），嚴禁連續爬高樓或快速下樓，以保護髕骨股骨關節軟骨。  \n"
            f"• ⏰ **打破久坐習慣**：每連續坐姿 50 至 60 分鐘，務必起身走動伸展 2 至 3 分鐘，活化下肢大肌肉與微血管血流。"
        ),
        "option_b": (
            f"**心肺適能連續訓練：每次 {cardio_mins} 分鐘，每週 {cardio_days} 天**  \n"
            f"• 🏃 **建議形式**：戶外慢跑、操場快走、室內飛輪或游泳，強度維持在「微喘但仍能完整說話」的中等強度心率區間（最大心率的 64% 至 76%）。  \n"
            f"• 🔬 **運動生理學關鍵差異**：**單次連續 25 至 30 分鐘訓練**能持續刺激心肌收縮與粒線體密度，提升最大攝氧量 (VO₂max)；"
            f"生活零碎快走雖能促進餐後血糖利用，但**對心肺耐力的長期結構性提升機制不同**，建議每週至少維持 2 至 3 次完整不中斷的連續運動！"
        ),
        "option_c": (
            f"**抗阻力與肌力維持：每週 2 至 3 天，每次 20 至 30 分鐘**  \n"
            f"• 🏋️ **建議動作**：優先針對大肌群進行【{strength_focus}】，每組 8 至 12 下，進行 3 組。  \n"
            f"• 💡 **代謝醫學核心**：減脂期人體傾向流失瘦肉組織。若僅死命做有氧，基礎代謝率將大幅下降並引發能量代償反彈；"
            f"**每週 2 次大肌群阻力訓練是守住基礎代謝率（BMR）與維持胰島素敏感度的最關鍵防線！**"
        )
    }

