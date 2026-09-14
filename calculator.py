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
    :param activity_level: 活動量乘數 (1.2 ~ 1.9)
    :return: TDEE 數值 (float)
    """
    tdee = bmr * activity_level
    return tdee

def calculate_macros(tdee, goal):
    """
    計算巨量營養素與目標熱量
    :param tdee: 每日總消耗熱量
    :param goal: "fat_loss" (減脂), "maintenance" (維持), "muscle_gain" (增肌)
    :return: 包含目標熱量、碳水、蛋白質、脂肪(克數)的字典 (dict)
    """
    # 根據目標設定熱量增減與三大營養素比例
    if goal == "fat_loss":
        target_calories = tdee - 300  # 減脂：每天少吃 300 大卡
        carbs_ratio, protein_ratio, fat_ratio = 0.4, 0.3, 0.3
    elif goal == "muscle_gain":
        target_calories = tdee + 300  # 增肌：每天多吃 300 大卡
        carbs_ratio, protein_ratio, fat_ratio = 0.5, 0.3, 0.2
    else:
        # 維持 (maintenance)
        target_calories = tdee
        carbs_ratio, protein_ratio, fat_ratio = 0.5, 0.2, 0.3

    # 計算克數 (碳水與蛋白質 1克=4大卡，脂肪 1克=9大卡)
    carbs_g = (target_calories * carbs_ratio) / 4
    protein_g = (target_calories * protein_ratio) / 4
    fat_g = (target_calories * fat_ratio) / 9

    # 將結果打包成字典回傳 (使用 round 四捨五入到整數)
    return {
        "target_calories": round(target_calories),
        "carbs_g": round(carbs_g),
        "protein_g": round(protein_g),
        "fat_g": round(fat_g)
    }
