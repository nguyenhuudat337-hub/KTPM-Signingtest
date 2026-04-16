import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.decathlon.vn/")  # sửa lại link của bạn

# 👉 Tự login (có thể dùng send_keys hoặc login tay)
input("👉 Sau khi login xong, nhấn Enter để lưu cookie...")

# Lưu cookie
cookies = driver.get_cookies()

with open("cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

print("✅ Đã lưu cookie thành công!")

driver.quit()