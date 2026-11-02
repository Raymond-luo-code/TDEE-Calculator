"""
TDEE 核心計算模組 (同學 B 負責)

此檔案只負責純粹的數學運算，請勿在這裡使用 input() 或是印出多餘的文字。
請參考 nutrition_parameters.md 中的公式來完成以下函數。
"""

def calculate_bmr(gender, weight, height, age):
    """
    計算基礎代謝率 (BMR) - 使用 Mifflin-St Jeor 公式
    :param gender: "male" 或 "female"
    :param weight: 體重 (kg)
    :param height: 身高 (cm)
    :param age: 年齡 (歲)
    :return: BMR 數值 (float)
    """
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    return bmr

def calculate_tdee(bmr, activity_level):
    """
    計算每日總消耗熱量 (TDEE)
    :param bmr: 基礎代謝率
    :param activity_level: 活動量乘數 (1.2 ～ 1.9)
    :return: TDEE 數值 (float)
    """
    tdee = bmr * activity_level
    return tdee

def calculate_macros(tdee, goal, diet_type="均衡飲食 (Balanced)"):
    """
    計算巨量營養素與目標熱量，並根據飲食法調整三大營養素比例
    :param tdee: 每日總消耗熱量
    :param goal: "fat_loss" (減脂), "maintenance" (維持), "muscle_gain" (增肌)
    :param diet_type: 飲食法類型
    :return: 包含目標熱量、碳水、蛋白質、脂肪(克數與百分比)的字典 (dict)
    """
    # 根據目標設定基本熱量增減與三大營養素基準比例
    if goal == "fat_loss":
        target_calories = tdee - 300  # 減脂：每天少吃 300 大卡
        carbs_ratio, protein_ratio, fat_ratio = 0.40, 0.30, 0.30
    elif goal == "muscle_gain":
        target_calories = tdee + 300  # 增肌：每天多吃 300 大卡
        carbs_ratio, protein_ratio, fat_ratio = 0.50, 0.30, 0.20
    else:
        # 維持 (maintenance)
        target_calories = tdee
        carbs_ratio, protein_ratio, fat_ratio = 0.50, 0.20, 0.30

    # 特殊飲食法校正 (符合醫學與營養學通則)
    if "生酮" in diet_type or "Keto" in diet_type:
        # 生酮飲食：極低碳水化合物 (約 8%)、適量蛋白質 (22%)、高脂肪 (70%)
        carbs_ratio, protein_ratio, fat_ratio = 0.08, 0.22, 0.70
    elif "地中海" in diet_type or "Mediterranean" in diet_type:
        # 地中海飲食：未精製澱粉、高比例不飽和脂肪 (35%)
        carbs_ratio, protein_ratio, fat_ratio = 0.45, 0.20, 0.35

    # 計算克數 (碳水與蛋白質 1克=4大卡，脂肪 1克=9大卡)
    carbs_g = (target_calories * carbs_ratio) / 4
    protein_g = (target_calories * protein_ratio) / 4
    fat_g = (target_calories * fat_ratio) / 9

    # 將結果打包成字典回傳 (使用 round 四捨五入到整數)
    return {
        "target_calories": round(target_calories),
        "carbs_g": round(carbs_g),
        "protein_g": round(protein_g),
        "fat_g": round(fat_g),
        "carbs_ratio": round(carbs_ratio * 100),
        "protein_ratio": round(protein_ratio * 100),
        "fat_ratio": round(fat_ratio * 100)
    }

def calculate_bmi(weight, height):
    """
    計算身體質量指數 (BMI) 與衛生福利部國民健康署標準體位判定
    :param weight: 體重 (kg)
    :param height: 身高 (cm)
    :return: 包含 bmi, 體位狀態, 建議顏色, 理想體重區間的字典
    """
    height_m = height / 100.0
    bmi = round(weight / (height_m ** 2), 1)
    
    # 衛福部國健署健康體位分級標準
    if bmi < 18.5:
        status = "體重過輕"
        color = "#3498db"
        advice = "建議諮詢專業營養師，建立規律飲食與適度阻力訓練以健康增重。"
    elif bmi < 24.0:
        status = "健康體位 (標準)"
        color = "#2ecc71"
        advice = "恭喜！您的體位維持在標準健康區間，請繼續保持優良的生活型態！"
    elif bmi < 27.0:
        status = "體位過重"
        color = "#f39c12"
        advice = "已接近過重邊緣，建議適度微調每日飲食熱量與增加有氧運動習慣。"
    elif bmi < 30.0:
        status = "輕度肥胖"
        color = "#e67e22"
        advice = "建議養成飲食紀錄習慣，減少高糖高油外食，維持規律全身性活動。"
    elif bmi < 35.0:
        status = "中度肥胖"
        color = "#e74c3c"
        advice = "建議尋求專科門診或執業營養師給予個別化飲食規劃與生活介入。"
    else:
        status = "重度肥胖"
        color = "#c0392b"
        advice = "強烈建議至各大醫院之代謝或體重管理特別門診，由跨專科醫師團隊進行評估。"

    ideal_min = round(18.5 * (height_m ** 2), 1)
    ideal_max = round(23.9 * (height_m ** 2), 1)

    return {
        "bmi": bmi,
        "status": status,
        "color": color,
        "advice": advice,
        "ideal_min": ideal_min,
        "ideal_max": ideal_max
    }

def calculate_water(weight, activity_level=1.2, goal="maintenance"):
    """
    計算每日建議水分攝取量 (ml)
    成人一般健康維持: 體重 x 30～35 ml
    減脂期或高活動量者: 體重 x 35～40 ml
    """
    if goal == "fat_loss" or activity_level >= 1.55:
        min_ml = round((weight * 35) / 100) * 100
        max_ml = round((weight * 40) / 100) * 100
    else:
        min_ml = round((weight * 30) / 100) * 100
        max_ml = round((weight * 35) / 100) * 100
    return min_ml, max_ml
