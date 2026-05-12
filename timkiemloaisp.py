from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
    print("\n" + f" {msg} ".center(80, "="))

def log(msg, status="INFO"):
    icons = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️ ", "ERROR": "🔥"}
    icon = icons.get(status, "   ")
    print(f"  {icon} [{status}] {msg}")

def log_case(desc, passed, pass_msg="", fail_msg=""):
    """
    passed=True  → hệ thống phản ứng đúng mong đợi → PASS
    passed=False → hệ thống phản ứng sai mong đợi  → FAIL
    """
    if passed:
        log(f"{desc} — {pass_msg or 'Hệ thống xử lý đúng'}", "PASS")
    else:
        log(f"{desc} — {fail_msg or 'Hệ thống không xử lý đúng'}", "FAIL")

# ===== Tắt popup =====
log_step("Tắt quảng cáo")
try:
    popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='gtm-popup_ads']//button")))
    popup.click()
    wait.until(EC.invisibility_of_element_located((By.ID, "gtm-popup_ads")))
    log("Đã tắt popup", "PASS")
except:
    log("Không có popup", "INFO")


# ===== TC1: Tìm kiếm sản phẩm =====
def test_search_product(keyword="áo"):
    """
    Mong đợi: nhập từ khóa → hệ thống hiển thị kết quả tìm kiếm (URL thay đổi hoặc
    trang kết quả xuất hiện).
    """
    log_step(f'TC1 — Tìm kiếm sản phẩm với từ khóa "{keyword}"')

    try:
        search_box = wait.until(EC.presence_of_element_located((
            By.XPATH, "//input[contains(@placeholder,'Tìm') or contains(@placeholder,'Search')]"
        )))

        driver.execute_script("arguments[0].scrollIntoView();", search_box)
        driver.execute_script("arguments[0].click();", search_box)
        wait.until(lambda d: search_box.is_displayed() and search_box.is_enabled())

        search_box.clear()
        search_box.send_keys(keyword)
        log(f'Nhập từ khóa "{keyword}"', "INFO")

        search_box.send_keys(u'\ue007')  # ENTER
        time.sleep(3)

        # Kiểm tra: URL phải chứa từ khóa hoặc trang kết quả xuất hiện
        url_changed = keyword.lower() in driver.current_url.lower() or "search" in driver.current_url.lower()

        try:
            results_visible = wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(@class,'product') or contains(@class,'result') or contains(@class,'item')]"
            ))).is_displayed()
        except:
            results_visible = False

        passed = url_changed or results_visible
        log_case(
            f'Tìm kiếm "{keyword}"',
            passed=passed,
            pass_msg=f"Trang hiển thị kết quả tìm kiếm (URL: {driver.current_url})",
            fail_msg=f"Không có kết quả nào được hiển thị sau khi tìm kiếm"
        )

    except Exception as e:
        log(f"Lỗi khi tìm kiếm: {type(e).__name__} - {e}", "ERROR")


# ===== TC2: Bộ lọc tìm kiếm loại sản phẩm =====
def test_filter_search_input():
    """
    Test ô tìm kiếm trong bộ lọc loại sản phẩm.
    """
    log_step("TC2 — Tìm kiếm trong bộ lọc loại sản phẩm")

    def clear_search_input(search_input):
        driver.execute_script("arguments[0].click();", search_input)
        current_value = search_input.get_attribute("value")
        while current_value:
            search_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
            current_value = search_input.get_attribute("value")

    def has_no_result_note():
        """Trả về True nếu trang hiện thông báo 'Không có kết quả'."""
        try:
            note = wait.until(EC.visibility_of_element_located((
                By.XPATH, "//div[contains(text(),'Không có kết quả cho')]"
            )))
            return "Không có kết quả cho" in note.text
        except TimeoutException:
            return False

    def has_checkbox(label_text):
        """Trả về True nếu checkbox có label khớp xuất hiện."""
        try:
            cb = wait.until(EC.visibility_of_element_located((
                By.CSS_SELECTOR, f"label[data-testid='checkbox-{label_text}']"
            )))
            return cb.is_displayed()
        except TimeoutException:
            return False

    try:
        # --- Mở icon bộ lọc tìm kiếm ---
        log("Tìm icon tìm kiếm trong bộ lọc...", "INFO")
        search_icon = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "button[data-testid='filter-listbox-search-button']"
        )))
        driver.execute_script("arguments[0].click();", search_icon)

        search_input = wait.until(EC.visibility_of_element_located((
            By.CSS_SELECTOR, "input[data-testid='filter-listbox-search-input-field']"
        )))
        driver.execute_script("arguments[0].click();", search_input)
        log("Đã mở ô tìm kiếm bộ lọc", "PASS")

        # =========================
        # CASE 1: Ký tự đặc biệt "@"
        # Mong đợi: hệ thống hiện thông báo "Không có kết quả"
        # =========================
        log_step("CASE 1 — Nhập ký tự đặc biệt '@'")
        clear_search_input(search_input)
        search_input.send_keys("@")
        time.sleep(2)

        showed_no_result = has_no_result_note()
        log_case(
            "Nhập ký tự đặc biệt '@'",
            passed=showed_no_result,
            pass_msg="Hệ thống hiển thị thông báo 'Không có kết quả' đúng mong đợi",
            fail_msg="Hệ thống không hiển thị thông báo 'Không có kết quả' khi nhập ký tự đặc biệt"
        )
        time.sleep(2)

        # =========================
        # CASE 2: Để trống
        # Mong đợi: hệ thống hiển thị toàn bộ danh sách loại sản phẩm (không lọc gì)
        # =========================
        log_step("CASE 2 — Để trống ô tìm kiếm")
        clear_search_input(search_input)
        time.sleep(2)

        try:
            any_checkbox = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "label[data-testid^='checkbox-']"
            )))
            has_items = any_checkbox.is_displayed()
        except TimeoutException:
            has_items = False

        log_case(
            "Ô tìm kiếm để trống",
            passed=has_items,
            pass_msg="Hệ thống hiển thị danh sách đầy đủ khi không nhập gì",
            fail_msg="Hệ thống không hiển thị danh sách khi ô tìm kiếm trống"
        )
        time.sleep(2)

        # =========================
        # CASE 3: Nhập số "123"
        # Mong đợi: hệ thống hiển thị "Không có kết quả" (không có loại SP nào là số)
        # =========================
        log_step("CASE 3 — Nhập số '123'")
        clear_search_input(search_input)
        search_input.send_keys("123")
        time.sleep(2)

        showed_no_result = has_no_result_note()
        log_case(
            "Nhập số '123'",
            passed=showed_no_result,
            pass_msg="Hệ thống hiển thị thông báo 'Không có kết quả' đúng mong đợi",
            fail_msg="Hệ thống không hiển thị thông báo 'Không có kết quả' khi nhập số"
        )
        time.sleep(2)

        # =========================
        # CASE 4: Nhập hợp lệ "áo khoác"
        # Mong đợi: hệ thống hiển thị checkbox "Áo khoác"
        # =========================
        log_step('CASE 4 — Nhập hợp lệ "áo khoác"')
        clear_search_input(search_input)
        search_input.send_keys("áo khoác")
        time.sleep(2)

        found_checkbox = has_checkbox("Áo khoác")
        log_case(
            'Tìm kiếm "áo khoác" trong bộ lọc',
            passed=found_checkbox,
            pass_msg='Hệ thống hiển thị checkbox "Áo khoác" đúng như mong đợi',
            fail_msg='Hệ thống không hiển thị checkbox "Áo khoác"'
        )

    except Exception as e:
        log(f"Lỗi TC2: {type(e).__name__} - {e}", "ERROR")


# ===== Chạy test =====
test_search_product("áo")
test_filter_search_input()