from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
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
    symbols = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️ ", "ERROR": "⚠️ "}
    symbol = symbols.get(status, "   ")
    print(f"  {symbol} [{status}] {msg}")

def log_result(desc, expected_blocked, actually_blocked):
    """
    desc             : mô tả case
    expected_blocked : True nếu đây là case KHÔNG hợp lệ (mong website chặn)
                       False nếu đây là case HỢP LỆ (mong website cho qua)
    actually_blocked : True nếu website thực sự hiện lỗi / không cho qua
    """
    if expected_blocked:
        # Case không hợp lệ → website chặn đúng → PASS, website cho qua → FAIL
        if actually_blocked:
            log(f"{desc} → Website chặn đúng ✓", "PASS")
        else:
            log(f"{desc} → Website KHÔNG chặn (lỗi không hiện)", "FAIL")
    else:
        # Case hợp lệ → website cho qua → PASS, website báo lỗi → FAIL
        if not actually_blocked:
            log(f"{desc} → Website cho qua đúng ✓", "PASS")
        else:
            log(f"{desc} → Website BÁO LỖI nhầm (case hợp lệ bị chặn)", "FAIL")


# ================== HELPER: kiểm tra có error message không ==================
def has_error_message(timeout=4):
    """
    Trả về True nếu tìm thấy bất kỳ thông báo lỗi nào trên form.
    Bạn có thể mở rộng XPath theo đúng selector của Decathlon.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//*[contains(@class,'error') or contains(@class,'invalid') "
                "or contains(@class,'alert') or contains(@class,'message--error')]"
                "[normalize-space(text()) != '']"
            ))
        )
        return True
    except TimeoutException:
        return False

def is_still_on_same_step(step_id, timeout=3):
    """Trả về True nếu vẫn còn ở bước hiện tại (không chuyển bước)."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, step_id))
        )
        return True
    except TimeoutException:
        return False


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
login_btn = driver.find_element(
    By.XPATH,
    "//*[@id='headerBoxInBaseContainer']/div/div[1]/div[5]/div/div[1]/div/div[1]/div"
)
login_btn.click()
log("Click login OK", "PASS")


# ================== STEP 3: Click tạo tài khoản ==================
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


# ================== VALIDATE 2: Email đã tồn tại ==================
def validate2():
    log_step("Test email đã tồn tại: test@gmail.com")
    try:
        email_input = wait.until(EC.presence_of_element_located((By.ID, "input-email")))
        email_input = wait.until(EC.element_to_be_clickable((By.ID, "input-email")))
        email_input.clear()
        email_input.send_keys("test@gmail.com")
        log("Nhập email: test@gmail.com", "INFO")

        signup_btn = wait.until(EC.element_to_be_clickable((By.ID, "lookup-btn-signup")))
        driver.execute_script("arguments[0].click();", signup_btn)
        log("Click signup", "INFO")

        # Mong đợi: website báo email đã tồn tại (hiện lỗi hoặc không chuyển sang OTP)
        blocked = has_error_message() or is_still_on_same_step("input-email")
        log_result("Email đã tồn tại", expected_blocked=True, actually_blocked=blocked)

    except StaleElementReferenceException:
        log("Stale element → thử lại", "ERROR")
    except Exception as e:
        log(f"Lỗi: {e}", "ERROR")

def clear_email_input():
    """Clear ô email bằng 3 lớp để đảm bảo sạch hoàn toàn."""
    email_input = wait.until(EC.element_to_be_clickable((By.ID, "input-email")))
    email_input.click()
    # Lớp 1: select all + delete (hoạt động trên cả Mac lẫn Windows/Linux)
    email_input.send_keys(Keys.COMMAND, "a")
    email_input.send_keys(Keys.DELETE)
    email_input.send_keys(Keys.CONTROL, "a")
    email_input.send_keys(Keys.DELETE)
    # Lớp 2: .clear() của Selenium
    email_input.clear()
    # Lớp 3: JS reset value để chắc chắn framework nhận biết field rỗng
    driver.execute_script("arguments[0].value = '';", email_input)
    return email_input

# ================== VALIDATE 3: Định dạng email ==================
def validate3():
    log_step("Test định dạng email")
 
    # (email, mô tả, is_valid)
    # is_valid=False → case không hợp lệ, mong website chặn
    # is_valid=True  → case hợp lệ, mong website cho qua
    test_emails = [
        ("@gmail.com",                                                                           "Thiếu tên trước @",       False),
        ("abc@gmail",                                                                            "Thiếu đuôi miền (.com…)", False),
        ("nguyenhuudat337hshdhshahsudyystaysudusiausdysudhvgfhdjsyctsraishdgcbsjayew74635staysudusiausdysudhvgfhdjsyctsraishdgcbsjayew746352gvhshdvdjs836sgd@gmail.com",
                                                                                                 "Vượt 90 ký tự",          False),
        ("",                                                                                     "Email rỗng",              False),
        ("nguyenhuudat 337@gmail.com",                                                           "Có khoảng trắng",         False),
        ("abcgmail.com",                                                                         "Thiếu @",                 False),
        ("nguyenhuudat337+6@gmail.com",                                                          "Email hợp lệ",            True),
    ]
 
    for email, desc, is_valid in test_emails:
        try:
            log_step(f"Test: [{desc}]  →  '{email}'")
 
            # Clear sạch trước khi nhập case mới
            email_input = clear_email_input()
 
            # Chỉ send_keys nếu email không rỗng (case rỗng thì để trống luôn)
            if email:
                email_input.send_keys(email)
 
            # Verify thực tế trong ô sau khi nhập
            actual_value = email_input.get_attribute("value")
            log(f"Giá trị trong ô: '{actual_value}'", "INFO")
 
            signup_btn = wait.until(EC.element_to_be_clickable((By.ID, "lookup-btn-signup")))
            driver.execute_script("arguments[0].click();", signup_btn)
 
            time.sleep(2)  # đợi UI phản hồi
 
            # Phát hiện bị chặn: có lỗi HOẶC vẫn còn ở bước email
            blocked = has_error_message() or is_still_on_same_step("input-email")
            log_result(desc, expected_blocked=not is_valid, actually_blocked=blocked)
 
        except Exception as e:
            log(f"Lỗi: {e}", "ERROR")
 
        time.sleep(2)


# ================== OTP helpers ==================
def clear_otp():
    for i in range(6):
        otp_input = wait.until(EC.element_to_be_clickable((By.ID, f"input-{i}")))
        otp_input.send_keys(Keys.CONTROL, "a")
        otp_input.send_keys(Keys.DELETE)

def enter_otp(otp_value):
    clear_otp()
    for i, char in enumerate(str(otp_value)[:6]):
        otp_input = wait.until(EC.element_to_be_clickable((By.ID, f"input-{i}")))
        otp_input.send_keys(char)

def click_verify_otp():
    verify_btn = wait.until(
        EC.element_to_be_clickable((
            By.XPATH, "//*[@id='form-verification-code']/div/button[1]"
        ))
    )
    driver.execute_script("arguments[0].click();", verify_btn)

def otp_step_still_visible(timeout=3):
    """Trả về True nếu form OTP vẫn còn (chưa qua bước password)."""
    return is_still_on_same_step("form-verification-code", timeout)


# ================== VALIDATE OTP ==================
def validate_otp():
    log_step("Test chức năng nhập OTP")

    real_otp = str(get_otp(
        "nguyenhuudat337@gmail.com",
        "ztis xbfk dqqw whan"
    ))

    # (otp_value, mô tả, đúng format?)
    otp_cases = [
        ("123",       "OTP ít hơn 6 ký tự",           False),
        ("abcdef",    "OTP chứa chữ cái",             False),
        ("12@#56",    "OTP chứa ký tự đặc biệt",      False),
        ("",          "OTP rỗng",                     False),

        # đúng format nhưng sai mã OTP
        ("000000",    "OTP sai (không đúng mã thật)", True),

        # OTP thật
        (real_otp,    "OTP hợp lệ (mã thật)",         True),
    ]

    for otp_value, desc, valid_format in otp_cases:

        display = otp_value if otp_value else "[rỗng]"

        try:
            log_step(f"OTP: [{desc}] → '{display}'")

            # Nhập OTP
            enter_otp(otp_value)
            log(f"Nhập OTP: {display}", "INFO")

            time.sleep(1)

            # =========================================
            # Tìm nút Tiếp tục
            # =========================================
            verify_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "button.otp-template__form__button"
                    )
                )
            )

            # =========================================
            # Kiểm tra trạng thái disabled
            # =========================================
            disabled_attr = verify_btn.get_attribute("disabled")

            is_disabled = disabled_attr is not None

            log(
                f"Nút Tiếp tục: "
                f"{'DISABLED' if is_disabled else 'ENABLED'}",
                "INFO"
            )

            # =================================================
            # CASE 1: OTP sai format
            # =================================================
            if not valid_format:

                if is_disabled:
                    log(
                        "PASS - OTP sai format, nút bị khóa đúng",
                        "SUCCESS"
                    )
                else:
                    log(
                        "FAIL - OTP sai format nhưng nút vẫn click được",
                        "ERROR"
                    )

                log_result(
                    desc,
                    expected_blocked=True,
                    actually_blocked=is_disabled
                )

                continue

            # =================================================
            # CASE 2: OTP đúng format
            # =================================================
            if is_disabled:

                log(
                    "FAIL - OTP đúng format nhưng nút vẫn bị khóa",
                    "ERROR"
                )

                log_result(
                    desc,
                    expected_blocked=False,
                    actually_blocked=True
                )

                continue

            # =========================================
            # Click nút Tiếp tục
            # =========================================
            click_verify_otp()
            log("Click nút Tiếp tục", "INFO")

            time.sleep(2)

            # =========================================
            # Kiểm tra còn ở bước OTP không
            # =========================================
            blocked = (
                otp_step_still_visible()
                or has_error_message(timeout=2)
            )

            expected_blocked = (otp_value != real_otp)

            log_result(
                desc,
                expected_blocked=expected_blocked,
                actually_blocked=blocked
            )

            # =========================================
            # OTP đúng thật
            # =========================================
            if otp_value == real_otp and not blocked:

                log(
                    "PASS - OTP hợp lệ, chuyển sang bước tiếp theo",
                    "SUCCESS"
                )

                return

        except Exception as e:
            log(f"Lỗi hệ thống: {e}", "ERROR")


# ================== VALIDATE PASSWORD (rỗng) ==================
def validate_password_empty():
    log_step("Test mật khẩu rỗng")
    try:
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='form-password']/button[1]"))
        )
        driver.execute_script("arguments[0].click();", confirm_btn)
        log("Click xác nhận (mật khẩu để trống)", "INFO")
        time.sleep(2)

        # Mong đợi: website chặn → vẫn còn form password hoặc hiện lỗi
        blocked = has_error_message() or is_still_on_same_step("form-password")
        log_result("Mật khẩu rỗng", expected_blocked=True, actually_blocked=blocked)

    except Exception as e:
        log(f"Lỗi: {e}", "ERROR")


# ================== VALIDATE PASSWORD ==================
def validate_password():

    log_step("Test các trường hợp mật khẩu")

    ERROR_TEXT1 = (
        "Mật khẩu chưa hợp lệ. "
        "Đảm bảo đáp ứng các yêu cầu cho mật khẩu."
    )

    ERROR_TEXT2 = (
        "The password you typed is too long, please limit it to 48 symbols"
    )

    

    # (password, mô tả, is_valid)
    password_cases = [
        ("abcdefg1!",    "Không có chữ hoa",         False),
        ("ABCDEFG1!",    "Không có chữ thường",      False),
        ("Abcdefgh!",    "Không có số",              False),
        ("Abc1!",        "Ít hơn 8 ký tự",           False),
        ("Abc def1!",    "Có dấu cách",              False),
        ("Abcdefg1",     "Không có ký tự đặc biệt",  False),

        (
            "Huudat0911nvkalsjdhwysuwisuayqtsgahsbcgshagdyatdrscs8929127@",
            "Nhiều hơn 48 ký tự",
            False
        ),

        ("Huudat0911@",  "Mật khẩu hợp lệ",          True),
    ]

    for pwd, desc, is_valid in password_cases:

        try:
            log_step(f"Password: [{desc}]")

            # =========================================
            # Input password
            # =========================================
            password_input = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "input-password")
                )
            )

            # =========================================
            # Hiện password nếu có nút eye
            # =========================================
            try:
                eye_btn = driver.find_element(
                    By.XPATH,
                    "//*[@id='form-password']//button[@aria-checked]"
                )

                if eye_btn.get_attribute("aria-checked") == "false":
                    driver.execute_script(
                        "arguments[0].click();",
                        eye_btn
                    )

            except:
                pass

            # =========================================
            # Clear password cũ
            # =========================================
            # Focus vào input
            driver.execute_script(
                "arguments[0].focus();",
                password_input
            )

            # Clear bằng JS
            driver.execute_script(
                "arguments[0].value = '';",
                password_input
            )

            # Trigger input event cho Vue/React
            driver.execute_script("""
                arguments[0].dispatchEvent(
                    new Event('input', { bubbles: true })
                );
            """, password_input)


            time.sleep(0.5)

            # =========================================
            # Nhập password mới
            # =========================================
            password_input.send_keys(pwd)

            log(f"Nhập password: {pwd}", "INFO")

            time.sleep(1)

            # =========================================
            # Click nút xác nhận
            # =========================================
            confirm_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@type='submit']")
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                confirm_btn
            )

            log("Click xác nhận", "INFO")

            time.sleep(2)

            # =========================================
            # Kiểm tra lỗi password
            # =========================================
            page_source = driver.page_source

            has_password_error1 = ERROR_TEXT1 in page_source
            has_password_error2 = ERROR_TEXT2 in page_source

            # =========================================
            # CASE PASSWORD INVALID
            # =========================================
            if not is_valid:

                blocked = (
                    has_password_error1 or has_password_error2
                    or is_still_on_same_step("input-password")
                )

                if has_password_error1 or has_password_error2:
                    log(
                        "Hiển thị đúng thông báo lỗi mật khẩu",
                        "SUCCESS"
                    )
                else:
                    log(
                        "Không tìm thấy thông báo lỗi mật khẩu",
                        "ERROR"
                    )

                log_result(
                    desc,
                    expected_blocked=True,
                    actually_blocked=blocked
                )

            # =========================================
            # CASE PASSWORD VALID
            # =========================================
            else:

                blocked = (
                    has_password_error1 or has_password_error2
                    or is_still_on_same_step("input-password")
                )

                log_result(
                    desc,
                    expected_blocked=False,
                    actually_blocked=blocked
                )

                if not blocked:
                    log(
                        "PASS - Mật khẩu hợp lệ",
                        "SUCCESS"
                    )
                else:
                    log(
                        "FAIL - Mật khẩu hợp lệ nhưng bị chặn",
                        "ERROR"
                    )

            time.sleep(2)

        except Exception as e:
            log(f"Lỗi hệ thống: {e}", "ERROR")


# ================== TICK CHECKBOX & SUBMIT ==================
def tick_checkbox_and_submit(driver):
    log_step("Tick checkbox điều khoản")

    checkbox1 = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//label[@for='datashare-D7q2MjWi']")
    ))
    driver.execute_script("arguments[0].click();", checkbox1)
    log("Checkbox 1 đã chọn", "PASS")

    checkbox2 = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//label[@for='mysports-RmzeVX4K']")
    ))
    driver.execute_script("arguments[0].click();", checkbox2)
    log("Checkbox 2 đã chọn", "PASS")

    log_step("Click submit hoàn tất đăng ký")
    submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "consents-button-submit")))
    driver.execute_script("arguments[0].click();", submit_btn)
    log("Click submit OK", "PASS")


# ================== KIỂM TRA ĐĂNG KÝ THÀNH CÔNG ==================
def check_register_success(driver):
    log_step("Kiểm tra kết quả đăng ký")
    try:
        WebDriverWait(driver, 10).until(
            lambda d: "decathlon.vn" in d.current_url and "login" not in d.current_url
        )
        log("Tạo tài khoản thành công → Redirect về trang chủ", "PASS")
    except:
        log("Tạo tài khoản thất bại / không redirect", "FAIL")


# ======================== MAIN FLOW ========================
click_btn_create()
time.sleep(2)

validate2()        # Email đã tồn tại
time.sleep(4)

validate3()        # Định dạng email
time.sleep(4)

validate_otp()     # Mã OTP
time.sleep(4)

validate_password_empty()   # Mật khẩu rỗng
time.sleep(4)

validate_password()         # Các trường hợp mật khẩu
time.sleep(4)
# tick_checkbox_and_submit(driver)
# check_register_success(driver)