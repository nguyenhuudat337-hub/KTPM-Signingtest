from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

# ===== Setup =====
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://decathlon.vn/")
driver.maximize_window()

wait = WebDriverWait(driver, 10)



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


# ===== Test case: Tìm kiếm sản phẩm =====
def test_search_product(keyword="áo"):
    log_step(f'Test tìm kiếm sản phẩm "{keyword}"')

    try:
        # 1. Tìm ô input search
        log("Tìm ô search...")
        search_box = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//input[contains(@placeholder,'Tìm') or contains(@placeholder,'Search')]"
            ))
        )

        # 2. Scroll + click vào ô input
        driver.execute_script("arguments[0].scrollIntoView();", search_box)
        driver.execute_script("arguments[0].click();", search_box)
        log("Đã click vào ô search", "PASS")

        # 3. Chờ input sẵn sàng để nhập
        wait.until(lambda d: search_box.is_displayed() and search_box.is_enabled())

        search_box.clear()
        search_box.send_keys(keyword)
        log(f'Đã nhập từ khóa "{keyword}"', "PASS")

        # 4. Enter để tìm kiếm
        search_box.send_keys(u'\ue007')   # ENTER
        log("Đã thực hiện tìm kiếm", "PASS")

    except Exception as e:
        log(f"Lỗi test tìm kiếm tại URL: {driver.current_url}", "ERROR")
        log(f"Chi tiết: {type(e).__name__} - {e}", "ERROR")
        return False
    


def test_filter_search_input():
    log_step("Test các trường hợp ô tìm kiếm bộ lọc")

    def clear_search_input(search_input):
        driver.execute_script("arguments[0].click();", search_input)

        current_value = search_input.get_attribute("value")
        while current_value:
            search_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
            current_value = search_input.get_attribute("value")

    try:
        # 1. Click icon tìm kiếm
        log("Tìm icon tìm kiếm...")
        search_icon = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "button[data-testid='filter-listbox-search-button']"
            ))
        )
        driver.execute_script("arguments[0].click();", search_icon)
        log("Đã click icon tìm kiếm", "PASS")

        # 2. Chờ ô input xuất hiện
        log("Tìm ô input tìm kiếm...")
        search_input = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "input[data-testid='filter-listbox-search-input-field']"
            ))
        )

        # 3. Click vào ô input
        driver.execute_script("arguments[0].click();", search_input)
        log("Đã click vào ô input", "PASS")

        # =========================
        # CASE 1: Ký tự đặc biệt
        # =========================
        log_step("CASE 1 - Nhập ký tự đặc biệt '@'")
        clear_search_input(search_input)
        search_input.send_keys("@")

        try:
            note = wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//div[contains(text(),'Không có kết quả cho')]"
                ))
            )
            if "Không có kết quả cho" in note.text:
                log(f'"{note.text}"', "FAIl")
        except:
            log("Không hiển thị note khi nhập ký tự đặc biệt", "FAIL")

        time.sleep(2)

        # =========================
        # CASE 2: Để trống
        # =========================
        log_step("CASE 2 - Để trống")
        clear_search_input(search_input)
        log("Để trống ô tìm kiếm", "FAIL")

        time.sleep(2)

        # =========================
        # CASE 3: Nhập số
        # =========================
        log_step("CASE 3 - Nhập số '123'")
        clear_search_input(search_input)
        search_input.send_keys("123")

        try:
            note = wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//div[contains(text(),'Không có kết quả cho')]"
                ))
            )
            if "Không có kết quả cho" in note.text:
                log(f'"{note.text}"', "FAIL")
            else:
                log("Hiển thị sai nội dung note", "FAIL")
        except:
            log("Không hiển thị note khi nhập số", "FAIL")

        time.sleep(2)

        # =========================
        # CASE 4: Nhập hợp lệ
        # =========================
        log_step('CASE 4 - Nhập hợp lệ "áo khoác"')
        clear_search_input(search_input)
        search_input.send_keys("áo khoác")
        log('Đã nhập "áo khoác" vào ô tìm kiếm', "PASS")

        try:
            checkbox_result = wait.until(
                EC.visibility_of_element_located((
                    By.CSS_SELECTOR,
                    "label[data-testid='checkbox-Áo khoác']"
                ))
            )

            if checkbox_result.is_displayed():
                log('Hiển thị checkbox "Áo khoác" đúng như mong đợi', "PASS")
            else:
                log('Không hiển thị checkbox "Áo khoác"', "FAIL")

        except:
            log('Không hiển thị checkbox kết quả cho "áo khoác"', "FAIL")

    except Exception as e:
        log(f"Lỗi test filter search: {type(e).__name__} - {e}", "ERROR")
        return False


test_search_product("áo")
test_filter_search_input()