"""
主程式整合 (第 9 週)

將同學 A 的輸入與同學 B 的計算結合起來。
"""
from cli_input import collect_user_data
from calculator import calculate_bmr, calculate_tdee, calculate_macros

def main():
    print("=== 歡迎使用個人化智慧 TDEE 計算器 ===")
    
    # 1. 取得同學 A 模組整理好的使用者資料
    user_data = collect_user_data()
    
    # 2. 將資料丟給同學 B 模組進行計算
    bmr = calculate_bmr(
        gender=user_data["gender"], 
        weight=user_data["weight"], 
        height=user_data["height"], 
        age=user_data["age"]
    )
    
    tdee = calculate_tdee(
        bmr=bmr, 
        activity_level=user_data["activity_multiplier"]
    )
    
    macros = calculate_macros(
        tdee=tdee, 
        goal=user_data["goal"]
    )
    
    # 3. 印出結果報告
    print("\n==============================")
    print("📊 您的專屬健康數據報告 📊")
    print("==============================")
    print(f"基礎代謝率 (BMR): {bmr:.1f} 大卡")
    print(f"每日總消耗量 (TDEE): {tdee:.1f} 大卡")
    print("------------------------------")
    print(f"🎯 目標攝取熱量: {macros['target_calories']} 大卡")
    print(f"🍚 碳水化合物: {macros['carbs_g']} 克")
    print(f"🥩 蛋白質: {macros['protein_g']} 克")
    print(f"🥑 脂肪: {macros['fat_g']} 克")
    print("==============================\n")

if __name__ == "__main__":
    main()
