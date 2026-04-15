from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
import time
from laymaotp import *
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://decathlon.vn/")
driver.maximize_window()

wait = WebDriverWait(driver, 8)

# ================== LOG ==================
def log_step(msg):
    print("\n" + msg.center(100, "="))

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

# ================== STEP 1 ==================
log_step("Tắt quảng cáo")
try:
    popup = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='gtm-popup_ads']//button"))
    )
    popup.click()
    log("Đã tắt popup", "PASS")
except:
    log("Không có popup", "INFO")

# ================== STEP 2 ==================
log_step("Click đăng nhập")
login_btn = driver.find_element(By.XPATH,"//*[@id='headerBoxInBaseContainer']/div/div[1]/div[5]/div/div[1]/div/div[1]/div")
login_btn.click()
log("Click login OK", "PASS")

# ================== STEP 3 ==================
def click_btn_create():
    log_step("Click tạo tài khoản")
    try:
        create_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "create-account"))
        )
        driver.execute_script("arguments[0].click();", create_btn)
        log("Click create account OK", "PASS")
    except Exception as e:
        log(f"Lỗi: {e}", "ERROR")




#email đã tồn tại
def validate2():
    log_step("Nhập email")

    try:
        # 🔥 B1: ĐỢI form email xuất hiện SAU khi click create
        email_input = wait.until(
            EC.presence_of_element_located((By.ID, "input-email"))
        )

        # 🔥 B2: đợi nó clickable (tránh stale)
        email_input = wait.until(
            EC.element_to_be_clickable((By.ID, "input-email"))
        )


        # 🔥 B3: KHÔNG click trước → nhập luôn (giảm re-render)
        email_input.clear()
        email_input.send_keys("test@gmail.com")

        log("Nhập email OK", "PASS")

        # 🔥 B4: đợi nút xác nhận
        log_step("Xác nhận")

        signup_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "lookup-btn-signup"))
        )

        driver.execute_script("arguments[0].click();", signup_btn)

        log("Click signup OK", "PASS")

        log("Tài khoản đã tồn tại", "PASS")
        
        try:
            error_msg = wait.until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    "//div[contains(text(),'Tài khoản này đã tồn tại') or contains(text(),'exist')]"
                ))
            )

            log("Hiển thị thông báo: Email đã tồn tại → PASS", "PASS")

        except:
            log("Không thấy thông báo email tồn tại → FAIL", "FAIL")

    except StaleElementReferenceException:
        log("Stale → thử lại", "ERROR")

    except Exception as e:
        log(f"Lỗi: {e}", "ERROR")



#test định dạng
def validate3():
    log_step("Test email sai định dạng")

    test_emails = [
        ("@gmail.com","Thiếu name"),
        ("abc@gmail","Thiếu miền .com"), 
        ("","Email rỗng"),    
        ("abcgmail.com","Thiếu @"),      
        ("nguyenhuudat337+1@gmail.com","Đúng định dạng"),
    ]

    for email,desc in test_emails:
        try:
            log_step(f"Test: {email}")

            email_input = wait.until(
                EC.element_to_be_clickable((By.ID, "input-email"))
            )

            # clear
            email_input.send_keys(Keys.COMMAND, "a")
            email_input.send_keys(Keys.DELETE)

            # nhập
            email_input.send_keys(email)

            signup_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "lookup-btn-signup"))
            )
            driver.execute_script("arguments[0].click();", signup_btn)

            log(f"{desc}", "PASS")

        except Exception as e:
            log(f"Lỗi: {e}", "ERROR")

        time.sleep(4)




#lấy otp và nhập tự động
def input_otp():
    time.sleep(10)
    otp = get_otp("nguyenhuudat337@gmail.com", "skvj ewue ebcl mufv")
    otp = str(otp)

    if len(otp) != 6:
        raise ValueError("OTP phải có đúng 6 ký tự")

    for i, digit in enumerate(otp):
        otp_input = wait.until(
            EC.element_to_be_clickable((By.ID, f"input-{i}"))
        )
        otp_input.send_keys(digit)
    signup_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='form-verification-code']/div/button[1]"))
    )
    driver.execute_script("arguments[0].click();", signup_btn)
    log("Click signup OK", "PASS")



def validate_password_empty():
    log_step("Test mật khẩu rỗng")

    try:
        confirm_btn = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[@id='form-password']/button[1]"
            ))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)
        log("Click xác nhận", "PASS")
        log("Mật khẩu rỗng", "PASS")
        
    except Exception as e:
        log(f"Lỗi: {e}", "ERROR")


def validate_password():
    log_step("Test chức năng nhập mật khẩu")

    password_cases = [
        ("abcdefg1!", "Không có chữ hoa"),
        ("ABCDEFG1!", "Không có chữ thường"),
        ("Abcdefgh!", "Không có số"),
        ("Abc1!", "Ít hơn 8 ký tự"),
        ("Abc def1!", "Có dấu cách"),
        ("Abcdefg1", "Không có ký tự đặc biệt"),
        ("Huudat0911@","Mật khẩu hợp lý"),
    ]

    for pwd, desc in password_cases:
        try:
            log_step(f"Case: {desc}")

            # 🔥 1. Đợi input password
            password_input = wait.until(
                EC.element_to_be_clickable((By.ID, "input-password"))
            )

            # 🔥 2. Bật mắt (show password)
            try:
                eye_btn = wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//*[@id='form-password']//button"
                    ))
                )

                # Nếu chưa bật thì click
                if eye_btn.get_attribute("aria-checked") == "false":
                    driver.execute_script("arguments[0].click();", eye_btn)
                    log("Đã bật hiển thị mật khẩu", "PASS")
            except:
                log("Không tìm thấy nút mắt", "ERROR")

            # 🔥 3. Clear password cũ
            password_input.send_keys(Keys.COMMAND, "a")
            password_input.send_keys(Keys.DELETE)

            # 🔥 4. Nhập password test
            password_input.send_keys(pwd)
            log(f"Nhập password: {pwd}", "INFO")

            time.sleep(2)

            # 🔥 5. Click xác nhận
            confirm_btn = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[@type='submit']"
                ))
            )

            driver.execute_script("arguments[0].click();", confirm_btn)
            log("Click xác nhận", "PASS")

            # 🔥 6. Check lỗi
            try:
                error_msg = wait.until(
                    EC.visibility_of_element_located((
                        By.XPATH,
                        "//div[contains(@class,'error') or contains(text(),'Mật khẩu chưa hợp lệ') or contains(text(),'password')]"
                    ))
                )
                log(f"[{desc}] → Báo lỗi đúng → PASS", "PASS")
                log(f"Message: {error_msg.text}", "INFO")

            except:
                log(f"[{desc}] → Không thấy lỗi → FAIL", "FAIL")

            # ⏱️ Delay để quan sát
            time.sleep(5)

        except Exception as e:
            log(f"[{desc}] → Lỗi: {e}", "ERROR")



def tick_checkbox_and_submit(driver):
    wait = WebDriverWait(driver, 10)

    print("\n==================== Tick checkbox ====================")

    # Checkbox 1
    checkbox1 = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//label[@for='datashare-D7q2MjWi']")
    ))
    driver.execute_script("arguments[0].click();", checkbox1)
    print("[PASS] Checkbox 1")

    # Checkbox 2
    checkbox2 = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//label[@for='mysports-RmzeVX4K']")
    ))
    driver.execute_script("arguments[0].click();", checkbox2)
    print("[PASS] Checkbox 2")

    print("\n==================== Click submit ====================")

    # Chờ button hết disabled
    submit_btn = wait.until(EC.element_to_be_clickable(
        (By.ID, "consents-button-submit")
    ))

    driver.execute_script("arguments[0].click();", submit_btn)
    print("[PASS] Click submit")


def check_register_success(driver):
    print("\n==================== Check đăng ký ====================")

    try:
        # Chờ URL thay đổi về trang chủ
        WebDriverWait(driver, 10).until(
            lambda d: "decathlon.vn" in d.current_url and "login" not in d.current_url
        )

        print(f"[SUCCESS] Tạo tài khoản thành công")

    except:
        print("[FAIL] Tạo tài khoản không thành công")

#nhấn tạo tài khoản
click_btn_create()
time.sleep(2)
#email đã tồn tại
validate2()
time.sleep(4)
#email định dạng
validate3()
time.sleep(4)
#lấy mã và điền mã
input_otp()
time.sleep(4)
#mật khẩu rỗng
validate_password_empty()
time.sleep(4)
#pass định dạng
validate_password()
#Đồng ý điều khoản
tick_checkbox_and_submit(driver)
check_register_success(driver)

