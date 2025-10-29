import os
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


@pytest.fixture(scope="class")
def driver():
    service = Service(executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.ctrip.com")
    driver.maximize_window()
    yield driver
    try:
        driver.quit()
    except:
        pass


class BaseCtripFlight:
    """基础类，包含所有测试类共用的操作方法"""

    def execute_action(self, driver, by_type, locator, action_type, input_data=None, alternative_locators=None):
        """统一的操作执行方法（支持备选定位器容错）"""
        if action_type == 'click':
            element = self._find_element_with_fallback(driver, by_type, locator, alternative_locators)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            sleep(0.5)
            
            windows_before = set(driver.window_handles)
            
            try:
                element.click()
            except:
                driver.execute_script("arguments[0].click();", element)
            
            sleep(1)
            
            windows_after = set(driver.window_handles)
            if len(windows_after) > len(windows_before):
                new_window = list(windows_after - windows_before)[0]
                driver.switch_to.window(new_window)
            
        elif action_type == 'input':
            element = self._find_element_with_fallback(driver, by_type, locator, alternative_locators, timeout=20)
            element.click()
            sleep(0.3)
            
            try:
                element.clear()
                sleep(0.2)
            except:
                pass
            
            try:
                driver.execute_script("""
                    arguments[0].value = '';
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, element)
                sleep(0.2)
            except:
                pass
            
            try:
                element.send_keys(Keys.CONTROL + 'a')
                sleep(0.1)
                element.send_keys(Keys.BACKSPACE)
                sleep(0.1)
            except:
                pass
            
            element.send_keys(input_data)
            
        elif action_type == 'hover':
            element = self._find_element_with_fallback(driver, by_type, locator, alternative_locators)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            sleep(0.5)
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            sleep(1)
            
        elif action_type == 'window_switch':
            window_index = int(locator.split('_')[1]) - 1
            window_handles = driver.window_handles
            driver.switch_to.window(window_handles[window_index])
    
    def _find_element_with_fallback(self, driver, by_type, locator, alternative_locators=None, timeout=10):
        """使用主定位器查找元素，失败后尝试备选定位器"""
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        try:
            wait = WebDriverWait(driver, timeout)
            element = wait.until(EC.presence_of_element_located((by_type, locator)))
            return element
        except TimeoutException:
            pass
        
        if alternative_locators:
            for alt_by, alt_locator in alternative_locators:
                try:
                    wait = WebDriverWait(driver, 5)
                    element = wait.until(EC.presence_of_element_located((alt_by, alt_locator)))
                    return element
                except TimeoutException:
                    continue
        
        raise NoSuchElementException(f"无法找到元素: 主定位器和所有备选定位器均失败")

    @staticmethod
    def take_screenshot(driver, file_name):
        timestamp = datetime.now().strftime("%H%M%S%d%f")
        timestamped_file_name = f"{timestamp}_{file_name}"
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        screenshot_file_path = os.path.join(screenshots_dir, timestamped_file_name)
        driver.save_screenshot(screenshot_file_path)


class PreCondition:
    """所有需求共享的前置步骤数据"""
    PRECONDITION_DATA = [
        ("PreCondition_P001", By.CSS_SELECTOR, "#leftSideNavLayer > div > div > div.lsn_top_button_wrap_t3-TA.lsn_icon_center_uNT-6 > div > div", [], "hover", "菜单", None),
        ("PreCondition_P002", By.XPATH, "//span[text()='机票']", [], "hover", "机票", None),
        ("PreCondition_P003", By.XPATH, "//span[text()='国内/国际/中国港澳台']", [(By.CSS_SELECTOR, "span.lsn_font_data_rSNIK"), (By.CSS_SELECTOR, "#popup-2 > div:nth-child(2) > a:nth-child(1) > span")], "click", "国内/", None),
        ("PreCondition_P004", By.XPATH, "//span[text()='单程']", [(By.CSS_SELECTOR, "span.radio-label"), (By.CSS_SELECTOR, "#searchForm > div > div.modify-search-box > div > div:nth-child(1) > ul > li:nth-child(1) > span")], "click", "单程", None),
    ]


class TestCtripFlight_R001(BaseCtripFlight):
    _precondition_executed = False
    
    TEST_DATA_R001 = [
        ("CtripFlight_R001_001", By.NAME, "owDCity", [(By.CSS_SELECTOR, "input[name='owDCity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "北京"),
        ("CtripFlight_R001_002", By.NAME, "owACity", [(By.CSS_SELECTOR, "input[name='owACity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "广州"),
        ("CtripFlight_R001_003", By.CSS_SELECTOR, "#datePicker > div.form-item-v3.flt-date.flt-date-depart > span > div > div > div > input[type=text]", [], "click", "日期", None),
        ("CtripFlight_R001_004", By.CSS_SELECTOR, "body > div:nth-child(8) > div > div.date-multi.clearfix > div:nth-child(2) > div.date-calendar.animated.infinite.fadeInRight > div > div.date-week.date-week-2 > div:nth-child(3) > span.date-d", [], "click", "日期", None),
        ("CtripFlight_R001_005", By.XPATH, "//span[text()='不限舱等']", [], "click", "不限", None),
        ("CtripFlight_R001_006", By.XPATH, "//div[text()='经济舱']", [], "click", "经济", None),
        ("CtripFlight_R001_007", By.XPATH, "//span[text()='带儿童']", [(By.CSS_SELECTOR, "span.label-tool-tip-wrap"), (By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(3) > div > div > div > div > div > div > div:nth-child(1) > span")], "click", "带儿童", None),
        ("CtripFlight_R001_008", By.XPATH, "//button[text()='搜索']", [(By.CSS_SELECTOR, "button[type='submit']"), (By.CSS_SELECTOR, "button.search-btn"), (By.CSS_SELECTOR, "#searchForm > div > button")], "click", "搜索", None),
    ]

    @pytest.mark.parametrize(
        "test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data",
        TEST_DATA_R001,
        ids=[step[0] for step in TEST_DATA_R001]
    )
    def test_CtripFlight_R001(self, driver, test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data):
        # 只在第一个测试步骤时执行前置步骤
        if not TestCtripFlight_R001._precondition_executed:
            for precond_step in PreCondition.PRECONDITION_DATA:
                precond_id, precond_by, precond_loc, precond_alts, precond_action, precond_name, precond_input = precond_step
                self.execute_action(driver, precond_by, precond_loc, precond_action, precond_input, precond_alts)
                sleep(0.5)
            TestCtripFlight_R001._precondition_executed = True

        # 执行业务步骤
        self.execute_action(driver, by_type, locator, action_type, input_data, alternative_locators)
        self.take_screenshot(driver, f"{test_case_id}.png")
        sleep(1)


class TestCtripFlight_R002(BaseCtripFlight):
    _precondition_executed = False
    
    TEST_DATA_R002 = [
        ("CtripFlight_R002_009", By.NAME, "owDCity", [(By.CSS_SELECTOR, "input[name='owDCity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "北京"),
        ("CtripFlight_R002_010", By.NAME, "owACity", [(By.CSS_SELECTOR, "input[name='owACity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "成都"),
        ("CtripFlight_R002_011", By.CSS_SELECTOR, "#datePicker > div.form-item-v3.flt-date.flt-date-depart > span > div > div > div > input[type=text]", [], "click", "日期", None),
        ("CtripFlight_R002_012", By.CSS_SELECTOR, "body > div:nth-child(8) > div > div.date-multi.clearfix > div:nth-child(2) > div.date-calendar.animated.infinite.fadeInRight > div > div.date-week.date-week-2 > div:nth-child(3) > span.date-d", [], "click", "日期", None),
        ("CtripFlight_R002_013", By.XPATH, "//span[text()='不限舱等']", [], "click", "不限", None),
        ("CtripFlight_R002_014", By.XPATH, "//div[text()='经济舱']", [], "click", "经济", None),
        ("CtripFlight_R002_015", By.XPATH, "//span[text()='带儿童']", [(By.CSS_SELECTOR, "span.label-tool-tip-wrap"), (By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(3) > div > div > div > div > div > div > div:nth-child(1) > span")], "click", "带儿童", None),
        ("CtripFlight_R002_016", By.XPATH, "//button[text()='搜索']", [(By.CSS_SELECTOR, "button[type='submit']"), (By.CSS_SELECTOR, "button.search-btn"), (By.CSS_SELECTOR, "#searchForm > div > button")], "click", "搜索", None),
    ]

    @pytest.mark.parametrize(
        "test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data",
        TEST_DATA_R002,
        ids=[step[0] for step in TEST_DATA_R002]
    )
    def test_CtripFlight_R002(self, driver, test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data):
        # 只在第一个测试步骤时执行前置步骤
        if not TestCtripFlight_R002._precondition_executed:
            for precond_step in PreCondition.PRECONDITION_DATA:
                precond_id, precond_by, precond_loc, precond_alts, precond_action, precond_name, precond_input = precond_step
                self.execute_action(driver, precond_by, precond_loc, precond_action, precond_input, precond_alts)
                sleep(0.5)
            TestCtripFlight_R002._precondition_executed = True

        # 执行业务步骤
        self.execute_action(driver, by_type, locator, action_type, input_data, alternative_locators)
        self.take_screenshot(driver, f"{test_case_id}.png")
        sleep(1)


class TestCtripFlight_R003(BaseCtripFlight):
    _precondition_executed = False
    
    TEST_DATA_R003 = [
        ("CtripFlight_R003_017", By.NAME, "owDCity", [(By.CSS_SELECTOR, "input[name='owDCity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "上海"),
        ("CtripFlight_R003_018", By.NAME, "owACity", [(By.CSS_SELECTOR, "input[name='owACity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "广州"),
        ("CtripFlight_R003_019", By.CSS_SELECTOR, "#datePicker > div.form-item-v3.flt-date.flt-date-depart > span > div > div > div > input[type=text]", [], "click", "日期", None),
        ("CtripFlight_R003_020", By.CSS_SELECTOR, "body > div:nth-child(8) > div > div.date-multi.clearfix > div:nth-child(2) > div.date-calendar.animated.infinite.fadeInRight > div > div.date-week.date-week-2 > div:nth-child(3) > span.date-d", [], "click", "日期", None),
        ("CtripFlight_R003_021", By.XPATH, "//span[text()='不限舱等']", [], "click", "不限", None),
        ("CtripFlight_R003_022", By.XPATH, "//div[text()='经济舱']", [], "click", "经济", None),
        ("CtripFlight_R003_023", By.XPATH, "//span[text()='带儿童']", [(By.CSS_SELECTOR, "span.label-tool-tip-wrap"), (By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(3) > div > div > div > div > div > div > div:nth-child(1) > span")], "click", "带儿童", None),
        ("CtripFlight_R003_024", By.XPATH, "//button[text()='搜索']", [(By.CSS_SELECTOR, "button[type='submit']"), (By.CSS_SELECTOR, "button.search-btn"), (By.CSS_SELECTOR, "#searchForm > div > button")], "click", "搜索", None),
    ]

    @pytest.mark.parametrize(
        "test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data",
        TEST_DATA_R003,
        ids=[step[0] for step in TEST_DATA_R003]
    )
    def test_CtripFlight_R003(self, driver, test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data):
        # 只在第一个测试步骤时执行前置步骤
        if not TestCtripFlight_R003._precondition_executed:
            for precond_step in PreCondition.PRECONDITION_DATA:
                precond_id, precond_by, precond_loc, precond_alts, precond_action, precond_name, precond_input = precond_step
                self.execute_action(driver, precond_by, precond_loc, precond_action, precond_input, precond_alts)
                sleep(0.5)
            TestCtripFlight_R003._precondition_executed = True

        # 执行业务步骤
        self.execute_action(driver, by_type, locator, action_type, input_data, alternative_locators)
        self.take_screenshot(driver, f"{test_case_id}.png")
        sleep(1)


class TestCtripFlight_R004(BaseCtripFlight):
    _precondition_executed = False
    
    TEST_DATA_R004 = [
        ("CtripFlight_R004_025", By.NAME, "owDCity", [(By.CSS_SELECTOR, "input[name='owDCity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "上海"),
        ("CtripFlight_R004_026", By.NAME, "owACity", [(By.CSS_SELECTOR, "input[name='owACity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "成都"),
        ("CtripFlight_R004_027", By.CSS_SELECTOR, "#datePicker > div.form-item-v3.flt-date.flt-date-depart > span > div > div > div > input[type=text]", [], "click", "日期", None),
        ("CtripFlight_R004_028", By.CSS_SELECTOR, "body > div:nth-child(8) > div > div.date-multi.clearfix > div:nth-child(2) > div.date-calendar.animated.infinite.fadeInRight > div > div.date-week.date-week-2 > div:nth-child(3) > span.date-d", [], "click", "日期", None),
        ("CtripFlight_R004_029", By.XPATH, "//span[text()='不限舱等']", [], "click", "不限", None),
        ("CtripFlight_R004_030", By.XPATH, "//div[text()='经济舱']", [], "click", "经济", None),
        ("CtripFlight_R004_031", By.XPATH, "//span[text()='带儿童']", [(By.CSS_SELECTOR, "span.label-tool-tip-wrap"), (By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(3) > div > div > div > div > div > div > div:nth-child(1) > span")], "click", "带儿童", None),
        ("CtripFlight_R004_032", By.XPATH, "//button[text()='搜索']", [(By.CSS_SELECTOR, "button[type='submit']"), (By.CSS_SELECTOR, "button.search-btn"), (By.CSS_SELECTOR, "#searchForm > div > button")], "click", "搜索", None),
    ]

    @pytest.mark.parametrize(
        "test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data",
        TEST_DATA_R004,
        ids=[step[0] for step in TEST_DATA_R004]
    )
    def test_CtripFlight_R004(self, driver, test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data):
        # 只在第一个测试步骤时执行前置步骤
        if not TestCtripFlight_R004._precondition_executed:
            for precond_step in PreCondition.PRECONDITION_DATA:
                precond_id, precond_by, precond_loc, precond_alts, precond_action, precond_name, precond_input = precond_step
                self.execute_action(driver, precond_by, precond_loc, precond_action, precond_input, precond_alts)
                sleep(0.5)
            TestCtripFlight_R004._precondition_executed = True

        # 执行业务步骤
        self.execute_action(driver, by_type, locator, action_type, input_data, alternative_locators)
        self.take_screenshot(driver, f"{test_case_id}.png")
        sleep(1)
