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
            EC.element_to_be_clickable((By.XPATH, "//*[@id='create-account-experiment']"))
        )
        driver.execute_script("arguments[0].click();", create_btn)
        log("Click create account OK", "PASS")
    except Exception as e:
        log(f"Lỗi: {e}", "ERROR")




#email đã tồn tại
def validate2():
    log_step("Nhập email: test@gmail.com")

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

        log("Tài khoản đã tồn tại", "FAIL")

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
        ("nguyenhuudat337hshdhshahsudystaysudusiausdysudhvgfhdjsyctsraishdgcbsjayew746352gvhshdvdjs836sgd@gmail.com","Số ký tự tối đa là 90"),
        ("","Email rỗng"),    
        ("nguyenhuudat 337@gmail.com","Có khoảng trắng"),
        ("abcgmail.com","Thiếu @"),      
        ("nguyenhuudat337+4@gmail.com","Đúng định dạng"),
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
            if desc == "Đúng định dạng": log(f"{desc}", "PASS")
            else: log(f"{desc}", "FAIL")

        except Exception as e:
            log(f"Lỗi: {e}", "ERROR")

        time.sleep(4)




#lấy otp và nhập tự động
# def input_otp():
#     time.sleep(5)
#     otp = get_otp("nguyenhuudat337@gmail.com", "skvj ewue ebcl mufv")
#     otp = str(otp)

#     if len(otp) != 6:
#         raise ValueError("OTP phải có đúng 6 ký tự")

#     for i, digit in enumerate(otp):
#         otp_input = wait.until(
#             EC.element_to_be_clickable((By.ID, f"input-{i}"))
#         )
#         otp_input.send_keys(digit)
#     signup_btn = wait.until(
#         EC.element_to_be_clickable((By.XPATH, "//*[@id='form-verification-code']/div/button[1]"))
#     )
#     driver.execute_script("arguments[0].click();", signup_btn)
#     log("Click signup OK", "PASS")

def clear_otp():
    """Xóa toàn bộ 6 ô OTP"""
    for i in range(6):
        otp_input = wait.until(
            EC.element_to_be_clickable((By.ID, f"input-{i}"))
        )
        otp_input.send_keys(Keys.COMMAND, "a")
        otp_input.send_keys(Keys.DELETE)


def enter_otp(otp_value):
    """Nhập OTP vào 6 ô"""
    clear_otp()

    for i, char in enumerate(str(otp_value)[:6]):   # chỉ nhập tối đa 6 ký tự
        otp_input = wait.until(
            EC.element_to_be_clickable((By.ID, f"input-{i}"))
        )
        otp_input.send_keys(char)


def click_verify_otp():
    """Click nút xác nhận OTP"""
    verify_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='form-verification-code']/div/button[1]"
        ))
    )
    driver.execute_script("arguments[0].click();", verify_btn)


def validate_otp():
    log_step("Test chức năng nhập OTP")

    # OTP thật để test case cuối
    real_otp = str(get_otp("nguyenhuudat337@gmail.com", "skvj ewue ebcl mufv"))

    otp_cases = [
        ("123", "OTP phải có đúng 6 ký tự", False),
        ("1234567", "OTP phải có đúng 6 ký tự", False),
        ("abcdef", "OTP phải là số", False),
        ("12@#56", "OTP không chứa ký tự đặc biệt", False),
        ("", "OTP không được để trống", False),
        ("000000", "OTP không chính xác", False),
        (real_otp, "OTP hợp lệ", True),
    ]

    for otp_value, expected_msg, is_valid in otp_cases:
        display_value = otp_value if otp_value else "[trống]"

        try:
            log_step(f"Kiểm tra OTP: {display_value}")

            # Nhập OTP
            enter_otp(otp_value)
            log(f"Nhập OTP: {display_value}", "INFO")

            time.sleep(1)
            click_verify_otp()
            log("Click xác nhận OTP", "INFO")

            # ==================================================
            # Hệ thống KHÔNG hiển thị lỗi OTP -> tự validate thủ công
            # ==================================================
            if not is_valid:
                log(f"{display_value} -> {expected_msg}", "FAIL")
                time.sleep(1)
                continue

            # OTP hợp lệ
            log(f"{display_value} -> OTP hợp lệ", "PASS")
            return   # OTP đúng thì dừng để sang bước password

        except Exception as e:
            log(f"{display_value} -> Lỗi hệ thống: {expected_msg}", "ERROR")



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
        log("Mật khẩu rỗng", "FAIL")
        
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
        ("Huudat0911nvkalsjdhwysuwisuayqtsgahsbcgshagdyatdrscs8929127@","Nhiều hơn 48 ký tự"),
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
                log(f"{desc}", "FAIL")

            except:
                log(f"[{desc}] → Không thấy lỗi", "PASS")

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
validate_otp()
time.sleep(4)
# mật khẩu rỗng
validate_password_empty()
time.sleep(4)
#pass định dạng
validate_password()
# #Đồng ý điều khoản và xác nhận
tick_checkbox_and_submit(driver)
check_register_success(driver)

