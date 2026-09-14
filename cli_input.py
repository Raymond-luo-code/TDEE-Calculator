"""
CLI 輸入與防呆模組 (同學 A 負責)

此檔案負責終端機的使用者互動，確保拿到的資料都是合法的數字。
請實作計畫書中提到的「防呆機制」。
"""

def get_valid_number(prompt, min_val, max_val):
    """
    不斷提示使用者輸入，直到輸入的數值合法為止。
    :param prompt: 提示文字，例如 "請輸入體重 (kg): "
    :param min_val: 允許的最小值 (例如 0)
    :param max_val: 允許的最大值 (例如 300)
    :return: 合法的浮點數 (float)
    """
    while True:
        try:
            # 取得使用者輸入的字串，並嘗試轉換為浮點數 (小數)
            user_input = float(input(prompt))
            
            # 檢查數值是否在合理範圍內
            if min_val <= user_input <= max_val:
                return user_input
            else:
                print(f"錯誤：數值必須介於 {min_val} 到 {max_val} 之間，請重新輸入。")
                
        except ValueError:
            # 如果輸入的不是數字（例如輸入了英文字母），就會跳到這裡
            print("錯誤：請輸入有效的數字格式！")

def collect_user_data():
    """
    收集所有計算需要的資料。
    :return: 包含性別、體重、身高、年齡、活動量、目標的字典 (dict)
    """
    print("--- 請輸入您的生理數值 ---")
    
    # 收集數值並防呆 (使用我們上面寫好的函數)
    age = get_valid_number("請輸入年齡 (歲): ", 1, 120)
    height = get_valid_number("請輸入身高 (cm): ", 50, 250)
    weight = get_valid_number("請輸入體重 (kg): ", 20, 300)
    
    # 收集性別 (字串防呆)
    while True:
        gender = input("請輸入性別 (男: m, 女: f): ").strip().lower()
        if gender in ['m', 'f']:
            break
        print("錯誤：請輸入 'm' 或 'f'")
        
    print("\n--- 請選擇您的活動量 ---")
    print("1. 久坐 (幾乎不運動)")
    print("2. 輕度活動 (每週運動 1-3 天)")
    print("3. 中度活動 (每週運動 3-5 天)")
    print("4. 高度活動 (每週運動 6-7 天)")
    print("5. 極度活動 (勞力密集)")
    
    # 用我們寫好的 get_valid_number 來確保他只輸入 1 到 5 的數字
    # 注意：get_valid_number 裡面已經有 while True 了，所以這裡外面不用再包一層 while 迴圈！
    activity_choice = get_valid_number("請輸入選項 (1-5): ", 1, 5)
    
    # 根據他的選擇，給予對應的活動量乘數
    if activity_choice == 1:
        activity_multiplier = 1.2
    elif activity_choice == 2:
        activity_multiplier = 1.375
    elif activity_choice == 3:
        activity_multiplier = 1.55
    elif activity_choice == 4:
        activity_multiplier = 1.725
    else:
        activity_multiplier = 1.9

    print("\n--- 請選擇您的目標 ---")
    print("1. 減脂 (Fat Loss)")
    print("2. 維持 (Maintenance)")
    print("3. 增肌 (Muscle Gain)")
    
    # 用我們寫好的 get_valid_number 來確保他只輸入 1 到 3 的數字
    goal_choice = get_valid_number("請輸入選項 (1-3): ", 1, 3)
    
    # 目標不是數字，我們把它轉換成「字串」，方便之後同學 B 拿去判斷
    if goal_choice == 1:
        goal = "fat_loss"
    elif goal_choice == 2:
        goal = "maintenance"
    else:
        goal = "muscle_gain"
            
    return {
        "age": age,
        "height": height,
        "weight": weight,
        "gender": "male" if gender == 'm' else "female",
        "activity_multiplier": activity_multiplier,
        "goal": goal
    }

# 下面這幾行是為了讓我們可以單獨測試這個檔案
if __name__ == "__main__":
    data = collect_user_data()
    print("\n太棒了！我們成功收集到合法的資料：")
    print(data)
