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
    service = Service(
        # 提交最终代码脚本时，请将驱动路径换回官方路径"C:\\Users\\86153\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe"
        executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.ctrip.com")
    driver.maximize_window()
    yield driver
    driver.quit()


class TestCtripFlight:
   
   
   
    # test-code-start


    # 请在此处插入python+selenium代码


    # 需求 R001 的测试数据
    TEST_DATA_R001 = [
        ("CtripFlight_R001_001", By.CSS_SELECTOR, "#leftSideNavLayer > div > div > div.lsn_top_button_wrap_t3-TA.lsn_icon_center_uNT-6 > div > div", [], "hover", "菜单", None),
        ("CtripFlight_R001_002", By.XPATH, "//span[text()='机票']", [], "hover", "机票", None),
        ("CtripFlight_R001_003", By.XPATH, "//span[text()='国内/国际/中国港澳台']", [(By.CSS_SELECTOR, "span.lsn_font_data_rSNIK"), (By.CSS_SELECTOR, "#popup-2 > div:nth-child(2) > a:nth-child(1) > span")], "click", "国内/", None),
        ("CtripFlight_R001_004", By.XPATH, "//span[text()='单程']", [(By.CSS_SELECTOR, "span.radio-label"), (By.CSS_SELECTOR, "#searchForm > div > div.modify-search-box > div > div:nth-child(1) > ul > li:nth-child(1) > span")], "click", "单程", None),
        ("CtripFlight_R001_005", By.NAME, "owDCity", [(By.CSS_SELECTOR, "input[name='owDCity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "北京"),
        ("CtripFlight_R001_006", By.NAME, "owACity", [(By.CSS_SELECTOR, "input[name='owACity']"), (By.CSS_SELECTOR, "input[type='text']"), (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")], "input", "输入框", "上海"),
        ("CtripFlight_R001_007", By.CSS_SELECTOR, "#datePicker > div.form-item-v3.flt-date.flt-date-depart > span > div > div > div > input[type=text]", [], "click", "日期", None),
        ("CtripFlight_R001_008", By.CSS_SELECTOR, "body > div:nth-child(8) > div > div.date-multi.clearfix > div:nth-child(2) > div.date-calendar.animated.infinite.fadeInRight > div > div.date-week.date-week-2 > div:nth-child(3) > span.date-d", [], "click", "日期", None),
        ("CtripFlight_R001_009", By.XPATH, "//span[text()='乘客类型']", [(By.CSS_SELECTOR, "span.form-label-v3")], "click", "乘客类", None),
        ("CtripFlight_R001_010", By.XPATH, "//span[text()='带儿童']", [(By.CSS_SELECTOR, "span.label-tool-tip-wrap"), (By.CSS_SELECTOR, "div:nth-child(2) > div:nth-child(3) > div > div > div > div > div > div > div:nth-child(1) > span")], "click", "带儿童", None),
        ("CtripFlight_R001_011", By.XPATH, "//span[text()='不限舱等']", [], "click", "不限", None),
        ("CtripFlight_R001_012", By.XPATH, "//div[text()='经济舱']", [], "click", "经济", None),
        ("CtripFlight_R001_013", By.XPATH, "//button[text()='搜索']", [(By.CSS_SELECTOR, "button[type='submit']"), (By.CSS_SELECTOR, "button.search-btn"), (By.CSS_SELECTOR, "#searchForm > div > button")], "click", "搜索", None),
    ]

    @pytest.mark.parametrize(
        "test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data",
        TEST_DATA_R001,
        ids=[step[0] for step in TEST_DATA_R001]
    )
    def test_CtripFlight_R001(self, driver, test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data):
        """测试需求 R001"""
        # 调用统一的操作执行方法（支持备选定位器）
        self.execute_action(driver, by_type, locator, action_type, input_data, alternative_locators)
        # 截图
        self.take_screenshot(driver, f"{test_case_id}.png")
        sleep(1)

    # test-code-end

    def execute_action(self, driver, by_type, locator, action_type, input_data=None, alternative_locators=None):
        """
        统一的操作执行方法（支持备选定位器容错）
        
        Args:
            driver: WebDriver实例
            by_type: 主定位方式（By.CSS_SELECTOR等）
            locator: 主定位器表达式
            action_type: 操作类型（click/input/hover/window_switch）
            input_data: 输入数据（可选）
            alternative_locators: 备选定位器列表 [(By.XX, "locator"), ...]
        """
        # 打印正在使用的定位器信息
        print(f"\n[定位器] 主定位: {by_type} = {locator[:100]}{'...' if len(locator) > 100 else ''}")
        if alternative_locators:
            print(f"[定位器] 备选定位器数量: {len(alternative_locators)}")
        
        if action_type == 'click':
            # 点击操作（支持备选定位器）
            element = self._find_element_with_fallback(driver, by_type, locator, alternative_locators)
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            sleep(0.5)
            
            # 记录点击前的窗口
            windows_before = set(driver.window_handles)
            
            try:
                element.click()
            except:
                driver.execute_script("arguments[0].click();", element)
            
            sleep(1)
            
            # 检查是否有新窗口
            windows_after = set(driver.window_handles)
            if len(windows_after) > len(windows_before):
                new_window = list(windows_after - windows_before)[0]
                driver.switch_to.window(new_window)
            
        elif action_type == 'input':
            # 输入操作（支持备选定位器）
            element = self._find_element_with_fallback(driver, by_type, locator, alternative_locators, timeout=20)
            element.click()
            sleep(0.5)
            
            # 强力清空输入框（针对携程等自定义控件）
            # 方法1: 三次Ctrl+A删除（最可靠的物理操作）
            for _ in range(3):
                try:
                    element.send_keys(Keys.CONTROL + 'a')
                    sleep(0.1)
                    element.send_keys(Keys.BACKSPACE)
                    sleep(0.1)
                except:
                    pass
            
            # 方法2: JavaScript强制清空并触发事件
            try:
                driver.execute_script("""
                    arguments[0].value = '';
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, element)
                sleep(0.2)
            except:
                pass
            
            # 方法3: 再次尝试标准clear()
            try:
                element.clear()
                sleep(0.2)
            except:
                pass
            
            # 最后一次确认清空：再次全选删除
            try:
                element.send_keys(Keys.CONTROL + 'a')
                element.send_keys(Keys.DELETE)
                sleep(0.2)
            except:
                pass
            
            element.send_keys(input_data)
            
        elif action_type == 'hover':
            # 鼠标悬浮操作（支持备选定位器）
            element = self._find_element_with_fallback(driver, by_type, locator, alternative_locators)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            sleep(0.5)
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            sleep(1)
            
        elif action_type == 'window_switch':
            # 窗口切换操作
            window_index = int(locator.split('_')[1]) - 1
            window_handles = driver.window_handles
            driver.switch_to.window(window_handles[window_index])
    
    def _find_element_with_fallback(self, driver, by_type, locator, alternative_locators=None, timeout=10):
        """
        使用主定位器查找元素，失败后尝试备选定位器
        
        Args:
            driver: WebDriver实例
            by_type: 主定位方式
            locator: 主定位器
            alternative_locators: 备选定位器列表
            timeout: 超时时间
            
        Returns:
            找到的WebElement
            
        Raises:
            NoSuchElementException: 所有定位器都失败时抛出
        """
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        # 尝试主定位器
        try:
            wait = WebDriverWait(driver, timeout)
            element = wait.until(EC.presence_of_element_located((by_type, locator)))
            print(f"[定位成功] 使用主定位器")
            return element
        except TimeoutException:
            print(f"[定位失败] 主定位器失败: {by_type}")
        
        # 尝试备选定位器
        if alternative_locators:
            print(f"[定位尝试] 开始尝试 {len(alternative_locators)} 个备选定位器...")
            for i, (alt_by, alt_locator) in enumerate(alternative_locators, 1):
                try:
                    print(f"  [{i}/{len(alternative_locators)}] 尝试: {alt_by} = {alt_locator[:80]}{'...' if len(alt_locator) > 80 else ''}")
                    wait = WebDriverWait(driver, 5)
                    element = wait.until(EC.presence_of_element_located((alt_by, alt_locator)))
                    print(f"  ✓ 备选定位器 [{i}] 成功！")
                    return element
                except TimeoutException:
                    print(f"  ✗ 备选定位器 [{i}] 失败")
                    continue
        
        # 所有定位器都失败
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


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
