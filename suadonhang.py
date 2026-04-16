from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pickle
import time

# ===== Setup =====
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://decathlon.vn/")
driver.maximize_window()

wait = WebDriverWait(driver, 10)

# ===== Load cookie =====
with open("cookies.pkl", "rb") as f:
    for cookie in pickle.load(f):
        driver.add_cookie(cookie)

driver.refresh()

# ===== Log =====
def log_step(msg):
    print("\n" + msg.center(60, "="))

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

# ===== Tắt popup =====
log_step("Tắt quảng cáo")
try:
    popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='gtm-popup_ads']//button")))
    popup.click()
    wait.until(EC.invisibility_of_element_located((By.ID, "gtm-popup_ads")))
    log("Đã tắt popup", "PASS")
except:
    log("Không có popup", "INFO")


def click_cart():
    log_step("Click giỏ hàng + chỉnh sửa")
    try:
        # ===== Click giỏ hàng =====
        cart_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='headerBoxInBaseContainer']/div/div[1]/div[5]/div/div[4]"))
        )

        cart_btn.click()

        # ===== Debug URL =====
        time.sleep(2)

        # ===== Click chỉnh sửa =====
        edit_btn = wait.until(EC.presence_of_element_located(( By.XPATH,"(//div[@data-cy='cart-product'])[1]//button[contains(., 'Chỉnh sửa')]")))

        driver.execute_script("arguments[0].scrollIntoView(true);", edit_btn)
        time.sleep(1)

        driver.execute_script("arguments[0].click();", edit_btn)

    except Exception as e:
        log(f"Lỗi: {e}", "ERROR")



def test_select_size():
    log_step("Test chọn size giày")

    try:
        # ===== Test size 40 (còn hàng) =====
        size_40 = driver.find_element(
            By.XPATH,
            "//*[@id='baseContainerMainTag']/div[2]/div/div[1]/div[3]/div/div[2]/div/div/div/div/div[2]/div[2]/dialog/div[2]/div/div[2]/div/div[2]/button"
        )

        class_40 = size_40.get_attribute("class")

        if "productSize_active" in class_40:
            size_40.click()
            log("Chọn size 40 thành công", "PASS")
        else:
            log("Size 40 không click được (unexpected)", "ERROR")

        # ===== Test size 46 (hết hàng) =====
        size_46 = driver.find_element(
            By.XPATH,
            "//button[text()='46']"
        )

        class_46 = size_46.get_attribute("class")

        if "productSize_outOfStock" in class_46:
            log("Không thể chọn size 46 vì đã hết hàng", "INFO")
        else:
            log("Size 46 vẫn click được (lỗi hệ thống)", "ERROR")

    except Exception as e:
        log(f"Lỗi khi test size: {e}", "ERROR")


def test_quantity_buttons():
    log_step("Test số lượng + / -")

    try:
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//dialog[@data-cy='cart-modal']")
        ))
        time.sleep(1)

        # ===== CASE 1: Test min = 1 =====
        log("Test min = 1", "INFO")

        for _ in range(5):
            btn_sub = driver.find_element(By.XPATH, "//button[@aria-label='subtract']")
            driver.execute_script("arguments[0].click();", btn_sub)
            time.sleep(0.2)

        value = driver.find_element(By.XPATH, '//*[@id="2901120"]').get_attribute("value")

        if value == "1":
            log("Không giảm dưới 1", "PASS")
        else:
            log(f"Lỗi min: {value}", "ERROR")

        # ===== CASE 2: Test tăng =====
        log("Test tăng", "INFO")

        btn_add = driver.find_element(By.XPATH, "//*[@id='baseContainerMainTag']/div[2]/div/div[1]/div[3]/div/div[2]/div/div/div/div/div[2]/div[2]/dialog/div[2]/div/div[3]/div/div/button[2]")
        driver.execute_script("arguments[0].click();", btn_add)
        time.sleep(0.3)

        value = driver.find_element(By.XPATH, '//*[@id="2901120"]').get_attribute("value")

        if value == "2":
            log("Tăng OK", "PASS")
        else:
            log(f"Lỗi tăng: {value}", "ERROR")

        # ===== CASE 3: Test max = 19 =====
        log("Test max = 19", "INFO")

        for _ in range(30):
            btn_add = driver.find_element(By.XPATH, "//*[@id='baseContainerMainTag']/div[2]/div/div[1]/div[3]/div/div[2]/div/div/div/div/div[2]/div[2]/dialog/div[2]/div/div[3]/div/div/button[2]")
            driver.execute_script("arguments[0].click();", btn_add)
            time.sleep(0.1)

        value = driver.find_element(By.XPATH, '//*[@id="2901120"]').get_attribute("value")

        if value == "19":
            log("Không vượt quá 19", "PASS")
        else:
            log(f"Lỗi max: {value}", "ERROR")

    except Exception as e:
        log(f"Lỗi test số lượng: {e}", "ERROR")


click_cart()
time.sleep(5)
test_select_size()
time.sleep(5)
test_quantity_buttons()
time.sleep(5)
confirm_btn = wait.until(
    EC.element_to_be_clickable((
        By.XPATH,
        "//dialog[@data-cy='cart-modal']//button[contains(., 'XÁC NHẬN')]"
    ))
)

driver.execute_script("arguments[0].click();", confirm_btn)
log("Sửa thành công", "PASS")
