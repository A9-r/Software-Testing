"""
优化后的网页自动化测试工具 - Pytest参数化版
主要改进：
1. 模块化设计 - 拆分成多个专职类
2. 配置管理 - 集中管理常量和配置
3. 减少重复代码 - 提取公共方法
4. 改进错误处理 - 统一的异常处理机制
5. Pytest参数化 - 使用@pytest.mark.parametrize装饰器，每个步骤独立执行
6. 独立浏览器 - 使用@pytest.fixture(scope="function")，每个步骤独立浏览器
7. 支持 'a' 命令 - 连续输入多个操作组成一个测试用例，输入'a'添加新测试用例
"""

import time
import os
import sys
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    WebDriverException, TimeoutException, 
    NoSuchElementException, StaleElementReferenceException
)


# ============ 配置类 ============
@dataclass
class Config:
    """集中管理所有配置项"""
    # 文件配置
    ELEMENT_LOG_FILE: str = 'clicked_elements.log'
    TEST_SCRIPT_FILE: str = 'TestCtripFlight.py'
    SCREENSHOTS_DIR: str = 'screenshots'
    
    # 超时配置
    DEFAULT_TIMEOUT: int = 10
    PAGE_LOAD_TIMEOUT: int = 30
    SCRIPT_TIMEOUT: int = 30
    
    # 高亮配置
    HIGHLIGHT_DURATION: float = 1.0
    HIGHLIGHT_STYLE: str = "border='3px solid red'; backgroundColor='yellow'"
    
    # CSS路径生成配置
    USE_SIMPLE_CSS_PATH: bool = True  # True=简洁模式（推荐），False=包含所有class
    MAX_CSS_PATH_DEPTH: int = 10  # CSS路径最大深度
    
    # 特殊命令
    INPUT_KEYWORDS: List[str] = None
    CUSTOM_ELEMENT_KEYWORDS: List[str] = None
    HOVER_KEYWORDS: List[str] = None
    WINDOW_KEYWORDS: List[str] = None
    EXIT_KEYWORDS: List[str] = None
    
    def __post_init__(self):
        """初始化列表类型的配置"""
        if self.INPUT_KEYWORDS is None:
            self.INPUT_KEYWORDS = ['输入框', '搜索框', '文本框']
        if self.CUSTOM_ELEMENT_KEYWORDS is None:
            self.CUSTOM_ELEMENT_KEYWORDS = ['添加', '自定义元素', 'custom']
        if self.HOVER_KEYWORDS is None:
            self.HOVER_KEYWORDS = ['悬浮', 'hover', '鼠标悬浮']
        if self.WINDOW_KEYWORDS is None:
            self.WINDOW_KEYWORDS = ['窗口', '切换窗口', 'windows']
        if self.EXIT_KEYWORDS is None:
            self.EXIT_KEYWORDS = ['quit', 'exit', '退出']


# ============ 元素定位器类 ============
class ElementLocatorGenerator:
    """负责生成元素定位器"""
    
    @staticmethod
    def generate_locators(element: WebElement, search_text: str, use_simple_css: bool = True) -> List[Tuple[str, str]]:
        """
        生成元素的所有可能定位器（优先级：文本 > ID > 属性 > CSS路径）
        返回: [(selector_type, selector_value), ...]
        """
        locators = []
        
        try:
            # 预先获取所有属性，避免元素过期
            attributes = ElementLocatorGenerator._get_element_attributes(element)
            tag = attributes.get('tag_name', '')
            text = attributes.get('text', '')
            
            # 1. 【最优先】LINK_TEXT定位器（最稳定）
            if tag == 'a' and text == search_text and search_text.strip():
                locators.append(('By.LINK_TEXT', search_text))
            
            # 2. 【次优先】PARTIAL_LINK_TEXT定位器
            if tag == 'a' and search_text.strip() and search_text in text:
                locators.append(('By.PARTIAL_LINK_TEXT', search_text))
            
            # 3. 【高优先】精确文本的XPATH定位器（使用元素实际文本，而非搜索文本）
            if text and text.strip():
                # 转义单引号，避免XPath语法错误
                # XPath中单引号的转义：使用concat()函数或双引号
                clean_text = text.strip()
                if "'" in clean_text:
                    # 如果包含单引号，使用双引号包裹
                    xpath_text_exact = f'//{tag}[text()="{clean_text}"]'
                    xpath_text_contains = f'//{tag}[contains(text(), "{clean_text}")]'
                else:
                    # 没有单引号，使用单引号包裹
                    xpath_text_exact = f"//{tag}[text()='{clean_text}']"
                    xpath_text_contains = f"//{tag}[contains(text(), '{clean_text}')]"
                
                if text.strip() == search_text.strip():
                    # 完全匹配文本 - 使用精确匹配
                    locators.append(('By.XPATH', xpath_text_exact))
                elif search_text.strip() in text:
                    # 包含文本 - 但使用元素的完整文本进行精确匹配
                    # 这样比contains更精确，避免匹配到其他相似元素
                    locators.append(('By.XPATH', xpath_text_exact))
                    # 同时也添加contains版本作为备选
                    locators.append(('By.XPATH', xpath_text_contains))
            
            # 4. ID定位器
            if attributes.get('id'):
                element_id = attributes['id']
                # 检查ID是否包含随机字符串（避免动态ID）
                if not ElementLocatorGenerator._is_dynamic_value(element_id):
                    if element_id[0].isdigit():
                        locators.append(('By.CSS_SELECTOR', f"[id='{element_id}']"))
                    else:
                        locators.append(('By.CSS_SELECTOR', f"#{element_id}"))
            
            # 5. 稳定的属性定位器
            locators.extend(ElementLocatorGenerator._generate_attribute_locators(attributes, search_text))
            
            # 6. 稳定的Class定位器（过滤动态class）
            if attributes.get('class'):
                classes = attributes['class'].split()
                stable_classes = [c for c in classes if not ElementLocatorGenerator._is_dynamic_value(c)]
                if stable_classes:
                    first_stable = stable_classes[0]
                    locators.append(('By.CSS_SELECTOR', f"{tag}.{first_stable}"))
                    if len(stable_classes) >= 2:
                        # 多个class组合更精确
                        locators.append(('By.CSS_SELECTOR', f"{tag}.{'.'.join(stable_classes[:2])}"))
            
            # 7. 【最后】完整CSS路径定位器（容易失效，放最后）
            try:
                full_css_path = ElementLocatorGenerator._generate_full_css_path(element, use_simple=use_simple_css)
                if full_css_path and ' > ' in full_css_path:
                    # 只有完整路径才添加，避免单一标签选择器
                    locators.append(('By.CSS_SELECTOR', full_css_path))
            except Exception as e:
                logging.debug(f"生成完整CSS路径失败: {e}")
            
            # 去重
            return ElementLocatorGenerator._deduplicate_locators(locators)
            
        except Exception as e:
            logging.error(f"生成定位器时出错: {e}")
            return locators
    
    @staticmethod
    def _is_dynamic_value(value: str) -> bool:
        """
        判断是否是动态值（包含随机字符串、时间戳等）
        """
        if not value:
            return False
        
        # 检查是否包含随机哈希（通常是CSS Modules）
        if '__' in value or '_' in value:
            parts = value.split('_')
            for part in parts:
                # 检查是否有长度>6的字母数字混合字符串（可能是哈希）
                if len(part) > 6 and any(c.isdigit() for c in part) and any(c.isalpha() for c in part):
                    return True
        
        # 检查是否全是数字（可能是ID）
        if value.isdigit() and len(value) > 4:
            return True
        
        # 检查是否包含时间戳模式
        import re
        if re.search(r'\d{10,}', value):  # 时间戳通常10位以上
            return True
        
        return False
    
    @staticmethod
    def _get_element_attributes(element: WebElement) -> Dict[str, str]:
        """获取元素的所有相关属性（扩展版）"""
        try:
            attrs = {
                'tag_name': element.tag_name,
                'id': element.get_attribute('id'),
                'class': element.get_attribute('class'),
                'text': element.text.strip() if element.text else '',
                'href': element.get_attribute('href'),
                'name': element.get_attribute('name'),
                'type': element.get_attribute('type'),
                'placeholder': element.get_attribute('placeholder'),
                'title': element.get_attribute('title'),
                'aria-label': element.get_attribute('aria-label'),
                'value': element.get_attribute('value'),
                'alt': element.get_attribute('alt'),
                'role': element.get_attribute('role'),
            }
            
            # 获取所有data-*属性
            try:
                # 通过JavaScript获取所有属性
                driver = element.parent
                all_attrs = driver.execute_script(
                    'var items = {}; '
                    'for (var i = 0; i < arguments[0].attributes.length; i++) { '
                    '  var attr = arguments[0].attributes[i]; '
                    '  if (attr.name.startsWith("data-")) { '
                    '    items[attr.name] = attr.value; '
                    '  } '
                    '} '
                    'return items;',
                    element
                )
                attrs.update(all_attrs)
            except:
                pass
            
            return attrs
        except StaleElementReferenceException:
            return {}
    
    @staticmethod
    def _generate_full_css_path(element: WebElement, use_simple: bool = True) -> str:
        """
        生成完整的CSS路径选择器（精确模仿Chrome开发者工具）
        
        Chrome真正的策略：
        1. 遇到ID立即停止
        2. 只使用"容器级别"的class（-container, -wrapper, Module等）
        3. 跳过"内容级别"和"布局级别"的class（-item, -text, layout-等）
        4. 其他情况使用nth-child
        
        示例: #__next > div.headerModule.gs-header > div > div > div:nth-child(3) > a
        """
        try:
            # 容器级别的class特征（Chrome会使用这些）
            CONTAINER_SUFFIXES = ['container', 'wrapper', 'module', 'holder', 'box']
            CONTAINER_KEYWORDS = ['header', 'footer', 'main', 'sidebar', 'aside']
            
            # 跳过的class特征（Chrome不会使用这些）
            SKIP_SUFFIXES = ['item', 'text', 'content', 'inner', 'link', 'btn', 'button', 'icon', 'img', 'title', 'desc']
            SKIP_PREFIXES = ['layout', 'page', 'section']
            
            # 第一步：收集从元素到根的路径
            elements_path = []
            current = element
            depth = 0
            max_depth = 10
            
            while current and depth < max_depth:
                try:
                    elements_path.append(current)
                    element_id = current.get_attribute('id')
                    
                    if element_id:
                        break
                    
                    current = current.find_element(By.XPATH, '..')
                    depth += 1
                except:
                    break
            
            # 第二步：反向生成选择器（从ID到目标元素）
            path_parts = []
            
            for i in range(len(elements_path) - 1, -1, -1):
                elem = elements_path[i]
                tag_name = elem.tag_name.lower()
                element_id = elem.get_attribute('id')
                element_class = elem.get_attribute('class')
                
                selector_part = tag_name
                
                # 如果是ID元素
                if element_id:
                    if element_id[0].isdigit():
                        selector_part = f"[id='{element_id}']"
                    else:
                        selector_part = f"#{element_id}"
                    path_parts.append(selector_part)
                    continue
                
                # 决定是否使用class
                use_class_here = False
                
                if element_class:
                    classes = element_class.strip().split()
                    container_classes = []  # 容器级别的class
                    
                    for c in classes:
                        if not c:
                            continue
                        
                        c_lower = c.lower()
                        
                        # 1. 过滤CSS Modules（哈希值）
                        has_hash = '_' in c and any(ch.isupper() for ch in c.split('_')[-1])
                        too_many_underscores = c.count('_') >= 2
                        too_long = len(c) > 25
                        
                        if has_hash or too_many_underscores or too_long:
                            continue
                        
                        # 2. 跳过"内容级别"和"布局级别"的class
                        should_skip = False
                        
                        # 检查后缀（-item, -text等）
                        for suffix in SKIP_SUFFIXES:
                            if c_lower.endswith(suffix) or f'-{suffix}' in c_lower:
                                should_skip = True
                                break
                        
                        # 检查前缀（layout-, page-等）
                        for prefix in SKIP_PREFIXES:
                            if c_lower.startswith(prefix):
                                should_skip = True
                                break
                        
                        if should_skip:
                            continue
                        
                        # 3. 识别"容器级别"的class
                        is_container = False
                        
                        # 检查容器后缀（-container, -wrapper, Module等）
                        for suffix in CONTAINER_SUFFIXES:
                            if c_lower.endswith(suffix) or suffix in c_lower:
                                is_container = True
                                break
                        
                        # 检查容器关键词（header, footer, main等）
                        for keyword in CONTAINER_KEYWORDS:
                            if keyword in c_lower:
                                is_container = True
                                break
                        
                        if is_container:
                            container_classes.append(c)
                    
                    # 如果有容器级别的class，使用它们（所有的，最多3个）
                    if container_classes:
                        selector_part = f"{tag_name}.{'.'.join(container_classes[:3])}"
                        use_class_here = True
                
                # 如果没用class，尝试使用nth-child
                if not use_class_here:
                    try:
                        parent = elem.find_element(By.XPATH, '..')
                        siblings = [s for s in parent.find_elements(By.XPATH, f"./{tag_name}")]
                        
                        # 只有多个兄弟时才加nth-child
                        if len(siblings) > 1:
                            for index, sibling in enumerate(siblings, 1):
                                try:
                                    if sibling == elem:
                                        selector_part = f"{selector_part}:nth-child({index})"
                                        break
                                except:
                                    continue
                    except:
                        pass
                
                path_parts.append(selector_part)
            
            if path_parts:
                return ' > '.join(path_parts)
            return ''
            
        except Exception as e:
            logging.error(f"生成完整CSS路径时出错: {e}")
            return ''
    
    @staticmethod
    def _generate_attribute_locators(attributes: Dict[str, str], search_text: str = "") -> List[Tuple[str, str]]:
        """基于属性生成定位器（优化版）"""
        locators = []
        tag = attributes.get('tag_name', '')
        
        # name属性（检查是否稳定）
        if attributes.get('name') and tag:
            name_val = attributes['name']
            if not ElementLocatorGenerator._is_dynamic_value(name_val):
                locators.append(('By.CSS_SELECTOR', f"{tag}[name='{name_val}']"))
                locators.append(('By.NAME', name_val))
        
        # type属性
        if attributes.get('type') and tag:
            type_val = attributes['type']
            locators.append(('By.CSS_SELECTOR', f"{tag}[type='{type_val}']"))
        
        # placeholder属性
        if attributes.get('placeholder') and tag:
            placeholder = attributes['placeholder']
            locators.append(('By.CSS_SELECTOR', f"{tag}[placeholder='{placeholder}']"))
        
        # href属性（更精确的匹配）
        if attributes.get('href') and tag == 'a':
            href = attributes['href']
            if 'http' in href:
                try:
                    from urllib.parse import urlparse, unquote
                    parsed = urlparse(href)
                    path = unquote(parsed.path)
                    
                    # 完整href匹配（最精确）
                    if path and len(path) > 1:  # 避免只匹配 '/'
                        # 去掉首尾斜杠
                        clean_path = path.strip('/')
                        if clean_path:
                            # 使用路径的最后一段（通常是页面名称）
                            path_parts = clean_path.split('/')
                            last_part = path_parts[-1] if path_parts else clean_path
                            
                            if last_part and len(last_part) > 2:
                                locators.append(('By.CSS_SELECTOR', f"a[href*='{last_part}']"))
                            
                            # 如果路径足够长，使用完整路径
                            if len(clean_path) > 5:
                                locators.append(('By.CSS_SELECTOR', f"a[href*='{clean_path}']"))
                    
                    # 如果有查询参数，使用查询参数
                    if parsed.query and len(parsed.query) > 3:
                        locators.append(('By.CSS_SELECTOR', f"a[href*='{parsed.query[:20]}']"))
                        
                except Exception as e:
                    logging.debug(f"解析href失败: {e}")
        
        # title属性
        if attributes.get('title') and tag:
            title = attributes.get('title', '')
            if title and not ElementLocatorGenerator._is_dynamic_value(title):
                locators.append(('By.CSS_SELECTOR', f"{tag}[title='{title}']"))
        
        # aria-label属性
        if attributes.get('aria-label') and tag:
            aria_label = attributes.get('aria-label', '')
            if aria_label:
                locators.append(('By.CSS_SELECTOR', f"{tag}[aria-label='{aria_label}']"))
        
        # data-*属性（常用于测试）
        for attr_name, attr_value in attributes.items():
            if attr_name.startswith('data-') and attr_value:
                if not ElementLocatorGenerator._is_dynamic_value(attr_value):
                    locators.append(('By.CSS_SELECTOR', f"{tag}[{attr_name}='{attr_value}']"))
        
        return locators
    
    @staticmethod
    def _deduplicate_locators(locators: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """去除重复的定位器"""
        seen = set()
        unique = []
        for loc in locators:
            if loc not in seen:
                unique.append(loc)
                seen.add(loc)
        return unique
    
    @staticmethod
    def select_best_locator(locators: List[Tuple[str, str]]) -> Optional[Tuple[str, str]]:
        """
        选择最佳定位器
        优先级：LINK_TEXT > XPATH文本 > NAME > ID > 属性 > Class > CSS路径
        """
        if not locators:
            return None
        
        # 🥇 最高优先：LINK_TEXT（最稳定）
        for loc in locators:
            if loc[0] == 'By.LINK_TEXT':
                return loc
        
        # 🥈 第二优先：XPATH文本定位（精确文本）
        for loc in locators:
            if loc[0] == 'By.XPATH' and 'text()=' in loc[1]:
                return loc
        
        # 🥉 第三优先：XPATH包含文本
        for loc in locators:
            if loc[0] == 'By.XPATH' and 'contains(text()' in loc[1]:
                return loc
        
        # 🏅 第四优先：PARTIAL_LINK_TEXT
        for loc in locators:
            if loc[0] == 'By.PARTIAL_LINK_TEXT':
                return loc
        
        # 🏅 第五优先：NAME属性
        for loc in locators:
            if loc[0] == 'By.NAME':
                return loc
        
        # 🏅 第六优先：ID选择器（稳定的ID）
        for loc in locators:
            if loc[0] == 'By.CSS_SELECTOR' and ('#' in loc[1] or "[id='" in loc[1]):
                return loc
        
        # 🏅 第七优先：其他属性定位器（name, placeholder, title等）
        for loc in locators:
            if loc[0] == 'By.CSS_SELECTOR' and any(attr in loc[1] for attr in ['[name=', '[placeholder=', '[title=', '[href*=']):
                return loc
        
        # 🏅 第八优先：稳定的Class定位器（多个class组合）
        for loc in locators:
            if loc[0] == 'By.CSS_SELECTOR' and '.' in loc[1] and loc[1].count('.') >= 2:
                return loc
        
        # 🏅 第九优先：单个Class定位器
        for loc in locators:
            if loc[0] == 'By.CSS_SELECTOR' and '.' in loc[1] and ' > ' not in loc[1]:
                return loc
        
        # 🏅 最后：完整CSS路径（容易失效，最后选择）
        for loc in locators:
            if loc[0] == 'By.CSS_SELECTOR' and ' > ' in loc[1]:
                return loc
        
        # 返回第一个
        return locators[0]


# ============ 测试脚本生成器类 ============
class TestScriptGenerator:
    """负责生成测试脚本（按需求编号分组）"""
    
    def __init__(self, script_file: str, initial_url: str):
        self.script_file = script_file
        self.initial_url = initial_url
        self.test_step_count = 0
        self.test_steps_data = []  # 存储所有测试步骤数据
        self.precondition_steps_data = []  # 存储前置步骤数据（所有需求共享）
        self.requirements = {}  # 按需求编号存储步骤 {requirement_id: [step_indices]}
        self.current_requirement = None  # 当前正在收集的需求编号
        self.is_collecting_precondition = True  # 默认先收集前置步骤
        self.precondition_completed = False  # 前置步骤是否已完成
        self._init_script_file()
    
    def _init_script_file(self):
        """初始化测试脚本文件"""
        header = self._generate_script_header()
        with open(self.script_file, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def _generate_script_header(self) -> str:
        """生成脚本文件头部"""
        return f'''import os
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
    service = Service(executable_path="C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get("{self.initial_url}")
    driver.maximize_window()
    yield driver
    driver.quit()


class BaseCtripFlight:
    """基础类，包含所有测试类共用的操作方法"""

    def execute_action(self, driver, by_type, locator, action_type, input_data=None, alternative_locators=None):
        """统一的操作执行方法（支持备选定位器容错）"""
        if action_type == 'click':
            element = self._find_element_with_fallback(driver, by_type, locator, alternative_locators)
            driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
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
                    arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
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
            driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
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
        timestamped_file_name = f"{{timestamp}}_{{file_name}}"
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        screenshot_file_path = os.path.join(screenshots_dir, timestamped_file_name)
        driver.save_screenshot(screenshot_file_path)


'''
    
    def set_current_requirement(self, requirement_id: str) -> bool:
        """设置当前需求编号，返回是否设置成功"""
        # 验证需求编号格式（应为R001、R002等）
        if not requirement_id.startswith('R') or len(requirement_id) != 4:
            print(f"⚠ 警告：需求编号格式不规范（应为R001、R002等）")
            return False
        
        # 验证后3位是否为数字
        try:
            int(requirement_id[1:])
        except ValueError:
            print(f"⚠ 警告：需求编号格式不规范（应为R001、R002等）")
            return False
        
        # 检查需求编号是否已存在
        if requirement_id in self.requirements:
            print(f"⚠ 警告：需求编号 {requirement_id} 已存在！")
            print(f"   已有需求: {', '.join(sorted(self.requirements.keys()))}")
            
            # 询问用户是否继续使用该需求编号
            while True:
                choice = input(f"是否继续使用 {requirement_id}？(y-继续添加步骤/n-取消): ").strip().lower()
                if choice == 'y':
                    print(f"✓ 继续向需求 {requirement_id} 添加步骤")
                    self.current_requirement = requirement_id
                    return True
                elif choice == 'n':
                    print(f"✗ 已取消，请重新输入需求编号")
                    return False
                else:
                    print("请输入 y 或 n")
        
        # 新需求编号
        self.current_requirement = requirement_id
        self.requirements[requirement_id] = []
        
        print(f"✓ 当前需求编号已设置为: {requirement_id}（新需求）")
        print(f"📝 现在请添加需求 {requirement_id} 的具体业务步骤")
        return True
    
    def add_test_method(self, element_data: Dict[str, str]) -> str:
        """添加测试步骤数据（收集数据而不是立即生成方法）"""
        # 确定操作类型
        operation_type = element_data['operation_type']
        if operation_type == "输入":
            action_type = "input"
        elif operation_type == "悬浮":
            action_type = "hover"
        else:
            action_type = "click"
        
        # 提取By类型（如 By.CSS_SELECTOR -> CSS_SELECTOR）
        by_type_name = element_data['selector_type'].replace('By.', '')
        
        # 根据是否是前置步骤，添加到不同的列表
        if self.is_collecting_precondition:
            # 前置步骤（所有需求共享）
            step_count = len(self.precondition_steps_data) + 1
            step_num = f"P{step_count:03d}"  # P001, P002...
            test_case_id = f"PreCondition_{step_num}"
            
            step_data = {
                'step_num': step_num,
                'test_case_id': test_case_id,
                'by_type': by_type_name,
                'locator': element_data['selector'],
                'alternative_locators': element_data.get('alternative_locators', []),
                'action_type': action_type,
                'test_name': element_data['search_text'],
                'input_data': element_data.get('user_input', '')
            }
            
            self.precondition_steps_data.append(step_data)
            step_type_text = "前置步骤"
            req_text = "【共享】"
        else:
            # 业务步骤（需要需求编号）
            if self.current_requirement is None:
                print("\n⚠ 错误：请先输入 'b' 完成前置步骤并设置需求编号")
                return "错误：未设置需求编号"
            
            # 确保需求编号在字典中存在（可能被删除后重新添加）
            if self.current_requirement not in self.requirements:
                self.requirements[self.current_requirement] = []
            
            self.test_step_count += 1
            step_num = f"{self.test_step_count:03d}"  # 001, 002...
            test_case_id = f"CtripFlight_{self.current_requirement}_{step_num}"
            
            step_data = {
                'step_num': step_num,
                'test_case_id': test_case_id,
                'requirement_id': self.current_requirement,
                'by_type': by_type_name,
                'locator': element_data['selector'],
                'alternative_locators': element_data.get('alternative_locators', []),
                'action_type': action_type,
                'test_name': element_data['search_text'],
                'input_data': element_data.get('user_input', '')
            }
            
            self.test_steps_data.append(step_data)
            step_index = len(self.test_steps_data) - 1
            self.requirements[self.current_requirement].append(step_index)
            
            step_type_text = "业务步骤"
            req_text = f"【{self.current_requirement}】"
        
        # 显示收集的信息
        print(f"\n{'='*50}")
        print(f"已收集{step_type_text} {req_text}: {test_case_id}")
        print(f"  操作名称: {element_data['search_text']}")
        print(f"  定位方式: {element_data['selector_type']}")
        print(f"  定位器: {element_data['selector'][:80]}{'...' if len(element_data['selector']) > 80 else ''}")
        print(f"  操作类型: {action_type}")
        if action_type == "input":
            print(f"  输入内容: {element_data['user_input']}")
        print(f"{'='*50}")
        
        return f"步骤{step_num}: {element_data['search_text']}"
    
    def add_window_switch_method(self, window_index: int, window_title: str):
        """添加窗口切换步骤"""
        # 如果没有设置需求编号，询问用户
        if self.current_requirement is None:
            while True:
                req_input = input("请输入需求编号 (格式：R001, R002等): ").strip()
                if not req_input:
                    print("需求编号不能为空")
                    continue
                if self.set_current_requirement(req_input):
                    break
        
        self.test_step_count += 1
        step_num = f"{self.test_step_count:03d}"
        
        # 生成测试用例编号
        test_case_id = f"CtripFlight_{self.current_requirement}_{step_num}"
        
        # 确保需求编号在字典中存在（可能被删除后重新添加）
        if self.current_requirement not in self.requirements:
            self.requirements[self.current_requirement] = []
        
        # 窗口切换作为特殊的click操作
        step_data = {
            'step_num': step_num,
            'test_case_id': test_case_id,
            'requirement_id': self.current_requirement,
            'by_type': 'WINDOW_SWITCH',
            'locator': f'window_{window_index}',
            'alternative_locators': [],  # 窗口切换没有备选定位器
            'action_type': 'window_switch',
            'test_name': f'切换到窗口{window_index}',
            'input_data': window_title
        }
        
        self.test_steps_data.append(step_data)
        
        # 将步骤索引添加到需求映射中
        step_index = len(self.test_steps_data) - 1
        self.requirements[self.current_requirement].append(step_index)
        
        print(f"\n{'='*50}")
        print(f"已收集窗口切换步骤: {test_case_id}")
        print(f"{'='*50}")
    
    def list_all_steps(self):
        """显示所有已添加的测试步骤（按需求分组）"""
        if not self.test_steps_data:
            print("\n暂无已添加的测试步骤")
            return
        
        print(f"\n{'='*80}")
        print(f"已添加的测试步骤 (共 {len(self.test_steps_data)} 步, {len(self.requirements)} 个需求)")
        print(f"{'='*80}")
        
        # 按需求分组显示
        for req_id in sorted(self.requirements.keys()):
            step_indices = self.requirements[req_id]
            print(f"\n【需求 {req_id}】 - {len(step_indices)} 个步骤")
            print(f"-" * 80)
            
            for idx in step_indices:
                step = self.test_steps_data[idx]
                display_num = idx + 1  # 显示序号从1开始
                
                print(f"\n  {display_num}. {step['test_case_id']}")
                print(f"     操作: {step['test_name']}")
                print(f"     类型: {step['action_type']}")
                print(f"     定位: By.{step['by_type']} = \"{step['locator']}\"")
                
                if step['input_data']:
                    print(f"     输入: {step['input_data']}")
        
        print(f"\n{'='*80}")
    
    def remove_step(self, index: int) -> bool:
        """删除指定索引的测试步骤"""
        if not self.test_steps_data:
            print("暂无测试步骤可删除")
            return False
        
        if 0 <= index < len(self.test_steps_data):
            removed_step = self.test_steps_data[index]
            req_id = removed_step['requirement_id']
            
            print(f"\n✓ 已删除步骤: {removed_step['test_case_id']} - {removed_step['test_name']}")
            
            # 从test_steps_data中删除
            self.test_steps_data.pop(index)
            
            # 重建需求映射
            self.requirements = {}
            for i, step in enumerate(self.test_steps_data):
                req = step['requirement_id']
                if req not in self.requirements:
                    self.requirements[req] = []
                self.requirements[req].append(i)
            
            # 重新编号所有步骤
            step_counters = {}  # 每个需求的步骤计数器
            for i, step in enumerate(self.test_steps_data):
                req = step['requirement_id']
                if req not in step_counters:
                    step_counters[req] = 0
                step_counters[req] += 1
                step['step_num'] = f"{step_counters[req]:03d}"
                step['test_case_id'] = f"CtripFlight_{req}_{step['step_num']}"
            
            self.test_step_count = len(self.test_steps_data)
            print(f"✓ 已重新编号，当前共 {self.test_step_count} 个步骤")
            return True
        else:
            print(f"无效的步骤索引: {index + 1}")
            return False
    
    def _generate_test_data_for_requirement(self, req_id: str, step_indices: List[int]) -> str:
        """为单个需求生成测试数据（参数化，包含备选定位器）"""
        lines = []
        lines.append(f"    TEST_DATA_{req_id} = [")
        
        for idx in step_indices:
            step = self.test_steps_data[idx]
            test_case_id = step['test_case_id']
            by_type = step['by_type']
            locator = step['locator'].replace('\\', '\\\\').replace('"', '\\"')
            action_type = step['action_type']
            test_name = step['test_name'].replace('\\', '\\\\').replace('"', '\\"')
            input_data = step.get('input_data', '')
            
            # 获取备选定位器
            alternative_locators = step.get('alternative_locators', [])
            alt_locators_list = []
            for alt_by, alt_loc in alternative_locators:
                alt_by_name = alt_by.replace('By.', '')
                alt_loc_escaped = alt_loc.replace('\\', '\\\\').replace('"', '\\"')
                alt_locators_list.append(f'(By.{alt_by_name}, "{alt_loc_escaped}")')
            
            alt_locators_str = '[' + ', '.join(alt_locators_list) + ']' if alt_locators_list else '[]'
            
            if input_data:
                input_data = input_data.replace('\\', '\\\\').replace('"', '\\"')
                input_str = f'"{input_data}"'
            else:
                input_str = 'None'
            
            line = f'        ("{test_case_id}", By.{by_type}, "{locator}", {alt_locators_str}, "{action_type}", "{test_name}", {input_str}),'
            lines.append(line)
        
        lines.append("    ]")
        return '\n'.join(lines)
    
    def _generate_test_function_for_requirement(self, req_id: str, step_indices: List[int]) -> str:
        """为单个需求生成参数化测试函数（带备选定位器）"""
        function_name = f"test_CtripFlight_{req_id}"
        lines = []
        
        # 生成参数化装饰器
        lines.append(f"    @pytest.mark.parametrize(")
        lines.append(f'        "test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data",')
        lines.append(f'        TEST_DATA_{req_id},')
        lines.append(f'        ids=[step[0] for step in TEST_DATA_{req_id}]')
        lines.append(f"    )")
        lines.append(f"    def {function_name}(self, driver, test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data):")
        
        # 如果有前置步骤，只在第一个测试步骤时执行
        if self.precondition_steps_data:
            lines.append(f"        # 只在第一个测试步骤时执行前置步骤")
            lines.append(f"        if not TestCtripFlight_{req_id}._precondition_executed:")
            lines.append("            for precond_step in PreCondition.PRECONDITION_DATA:")
            lines.append("                precond_id, precond_by, precond_loc, precond_alts, precond_action, precond_name, precond_input = precond_step")
            lines.append("                self.execute_action(driver, precond_by, precond_loc, precond_action, precond_input, precond_alts)")
            lines.append("                sleep(0.5)")
            lines.append(f"            TestCtripFlight_{req_id}._precondition_executed = True")
            lines.append("")
            lines.append("        # 执行业务步骤")
        
        lines.append("        self.execute_action(driver, by_type, locator, action_type, input_data, alternative_locators)")
        lines.append("        self.take_screenshot(driver, f\"{test_case_id}.png\")")
        lines.append("        sleep(1)")
        
        return '\n'.join(lines)
    
    def _generate_precondition_class(self) -> str:
        """生成共享的前置步骤类（仅包含数据，不包含测试方法）"""
        if not self.precondition_steps_data:
            return ""
        
        lines = []
        lines.append("class PreCondition:")
        lines.append("    \"\"\"所有需求共享的前置步骤数据\"\"\"")
        lines.append("    PRECONDITION_DATA = [")
        
        for step in self.precondition_steps_data:
            test_case_id = step['test_case_id']
            by_type = step['by_type']
            locator = step['locator'].replace('\\', '\\\\').replace('"', '\\"')
            action_type = step['action_type']
            test_name = step['test_name'].replace('\\', '\\\\').replace('"', '\\"')
            input_data = step.get('input_data', '')
            
            alternative_locators = step.get('alternative_locators', [])
            alt_locators_list = []
            for alt_by, alt_loc in alternative_locators:
                alt_by_name = alt_by.replace('By.', '')
                alt_loc_escaped = alt_loc.replace('\\', '\\\\').replace('"', '\\"')
                alt_locators_list.append(f'(By.{alt_by_name}, "{alt_loc_escaped}")')
            
            alt_locators_str = '[' + ', '.join(alt_locators_list) + ']' if alt_locators_list else '[]'
            
            if input_data:
                input_data = input_data.replace('\\', '\\\\').replace('"', '\\"')
                input_str = f'"{input_data}"'
            else:
                input_str = 'None'
            
            line = f'        ("{test_case_id}", By.{by_type}, "{locator}", {alt_locators_str}, "{action_type}", "{test_name}", {input_str}),'
            lines.append(line)
        
        lines.append("    ]")
        
        return '\n'.join(lines)
    
    def complete_script(self):
        """完成脚本，生成共享前置步骤类和各个需求类"""
        if not self.test_steps_data and not self.precondition_steps_data:
            print("⚠ 警告：没有收集到任何测试步骤")
            return
        
        all_classes = []
        
        # 1. 生成共享的前置步骤类（只生成一次）
        precondition_class = self._generate_precondition_class()
        if precondition_class:
            all_classes.append(precondition_class)
        
        # 2. 生成所有需求的业务步骤类
        for req_id in sorted(self.requirements.keys()):
            if req_id in self.requirements and self.requirements[req_id]:
                step_indices = self.requirements[req_id]
                data_code = self._generate_test_data_for_requirement(req_id, step_indices)
                func_code = self._generate_test_function_for_requirement(req_id, step_indices)
                
                # 添加类变量（用于标记前置步骤是否已执行）
                class_var = "    _precondition_executed = False\n    " if self.precondition_steps_data else "    "
                
                class_code = f'''class TestCtripFlight_{req_id}(BaseCtripFlight):
{class_var}
{data_code}

{func_code}
'''
                all_classes.append(class_code)
        
        all_classes_str = '\n\n'.join(all_classes)
        
        # 追加到文件
        with open(self.script_file, 'a', encoding='utf-8') as f:
            f.write(all_classes_str)
        
        # 打印总结
        print(f"\n{'='*80}")
        print(f"✓ 测试脚本生成完成: {self.script_file}")
        print(f"{'='*80}")
        print(f"  前置步骤总数: {len(self.precondition_steps_data)}")
        print(f"  业务步骤总数: {len(self.test_steps_data)}")
        print(f"  需求数量: {len(self.requirements)}")
        print(f"\n生成内容:")
        if self.precondition_steps_data:
            print(f"    ✓ PreCondition - {len(self.precondition_steps_data)} 个前置步骤（所有需求共享）")
        for req_id in sorted(self.requirements.keys()):
            step_count = len(self.requirements.get(req_id, []))
            if step_count > 0:
                print(f"    ✓ TestCtripFlight_{req_id} - {step_count} 个业务步骤")
        print(f"\n运行流程:")
        if self.precondition_steps_data:
            print(f"  每个需求类的第一个测试步骤前会执行 PreCondition 中的前置步骤")
            print(f"  同一需求类的后续测试步骤不会重复执行前置步骤")
        print(f"\n运行测试命令:")
        print(f"  pytest {self.script_file} -v")
        print(f"  pytest {self.script_file} -v -s  (显示详细输出)")
        print(f"{'='*80}")




# ============ 窗口管理器类 ============
class WindowManager:
    """负责浏览器窗口管理"""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.original_window = driver.current_window_handle
        self.current_window = self.original_window
    
    def get_window_info(self) -> str:
        """获取当前窗口信息"""
        try:
            handles = self.driver.window_handles
            current_index = handles.index(self.current_window) + 1
            return f"窗口: {current_index}/{len(handles)}, 标题: {self.driver.title}"
        except Exception as e:
            return f"获取窗口信息失败: {e}"
    
    def print_window_info(self):
        """打印当前窗口信息"""
        print(self.get_window_info())
    
    def switch_to_new_window(self, previous_windows: Set[str]) -> bool:
        """切换到新窗口"""
        try:
            new_windows = set(self.driver.window_handles)
            if len(new_windows) > len(previous_windows):
                new_window = list(new_windows - previous_windows)[0]
                self.driver.switch_to.window(new_window)
                self.current_window = new_window
                return True
            return False
        except Exception as e:
            logging.error(f"切换窗口失败: {e}")
            return False
    
    def list_and_switch_windows(self, script_generator=None) -> Tuple[bool, int, str]:
        """
        列出所有窗口供用户选择
        
        Returns:
            (成功标志, 窗口索引, 窗口标题)
        """
        try:
            handles = self.driver.window_handles
            current = self.driver.current_window_handle
            
            print(f"\n当前共有 {len(handles)} 个窗口:")
            window_titles = []
            for i, handle in enumerate(handles, 1):
                self.driver.switch_to.window(handle)
                is_current = " (当前窗口)" if handle == current else ""
                title = self.driver.title
                window_titles.append(title)
                print(f"  {i}. 标题: {title}{is_current}")
            
            self.driver.switch_to.window(current)
            
            # 让用户选择
            while True:
                try:
                    choice = input(f"请选择要切换到的窗口 (1-{len(handles)}): ").strip()
                    if not choice:
                        continue
                    
                    idx = int(choice) - 1
                    if 0 <= idx < len(handles):
                        selected = handles[idx]
                        selected_index = idx + 1
                        selected_title = window_titles[idx]
                        
                        if selected != current:
                            self.driver.switch_to.window(selected)
                            self.current_window = selected
                            print(f"已切换到窗口 {selected_index}: {selected_title}")
                        
                        return True, selected_index, selected_title
                    else:
                        print(f"请输入 1-{len(handles)} 之间的数字")
                except ValueError:
                    print("请输入有效的数字")
                except KeyboardInterrupt:
                    print("\n用户取消选择")
                    self.driver.switch_to.window(current)
                    return False, -1, ""
        except Exception as e:
            logging.error(f"列出窗口失败: {e}")
            return False, -1, ""
    
    def switch_to_original(self) -> bool:
        """切换到原始窗口"""
        try:
            if self.current_window != self.original_window:
                self.driver.switch_to.window(self.original_window)
                self.current_window = self.original_window
                print("已切换到原始窗口")
                return True
            else:
                print("当前已在原始窗口")
                return False
        except Exception as e:
            logging.error(f"切换到原始窗口失败: {e}")
            return False
    
    def close_current_window(self) -> bool:
        """关闭当前窗口并切换到原始窗口"""
        try:
            if self.current_window != self.original_window:
                self.driver.close()
                self.driver.switch_to.window(self.original_window)
                self.current_window = self.original_window
                print("已关闭当前窗口并切换到原始窗口")
                return True
            else:
                print("当前是原始窗口，不能关闭")
                return False
        except Exception as e:
            logging.error(f"关闭窗口失败: {e}")
            return False


# ============ 元素操作类 ============
class ElementOperator:
    """负责元素的查找和操作"""
    
    def __init__(self, driver: webdriver.Chrome, config: Config):
        self.driver = driver
        self.config = config
    
    def wait_for_stable_page(self, timeout: int = 5):
        """等待页面稳定"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            pass
    
    def highlight_element(self, element: WebElement, duration: float = None):
        """高亮显示元素"""
        if duration is None:
            duration = self.config.HIGHLIGHT_DURATION
        
        try:
            original_style = element.get_attribute("style")
            self.driver.execute_script(
                f"arguments[0].style.{self.config.HIGHLIGHT_STYLE}", element
            )
            time.sleep(duration)
            self.driver.execute_script(f"arguments[0].style='{original_style}'", element)
        except Exception as e:
            logging.error(f"高亮元素失败: {e}")
    
    def click_element_safely(self, element: WebElement) -> bool:
        """安全地点击元素（先尝试常规点击，失败则用JS）"""
        try:
            # 滚动到可见位置
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.5)
            
            try:
                element.click()
            except:
                self.driver.execute_script("arguments[0].click();", element)
                print("使用JavaScript点击元素")
            
            return True
        except Exception as e:
            logging.error(f"点击元素失败: {e}")
            return False
    
    def hover_element_safely(self, element: WebElement) -> bool:
        """安全地悬浮到元素上"""
        try:
            # 滚动到可见位置
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.5)
            
            # 使用ActionChains执行鼠标悬浮
            from selenium.webdriver import ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            print("鼠标已悬浮到元素")
            
            return True
        except Exception as e:
            logging.error(f"鼠标悬浮失败: {e}")
            return False
    
    def find_elements_by_text(self, text: str, exact: bool = True) -> List[WebElement]:
        """根据文本查找元素"""
        try:
            if exact:
                xpath = f"//*[text()='{text.strip()}']"
            else:
                xpath = f"//*[contains(text(), '{text.strip()}')]"
            
            elements = self.driver.find_elements(By.XPATH, xpath)
            return [elem for elem in elements if elem.is_displayed()]
        except Exception as e:
            logging.error(f"查找元素失败: {e}")
            return []
    
    def find_input_elements(self) -> List[WebElement]:
        """查找所有可见的输入框元素"""
        try:
            input_elements = []
            input_elements.extend(self.driver.find_elements(By.TAG_NAME, "input"))
            input_elements.extend(self.driver.find_elements(By.TAG_NAME, "textarea"))
            
            # 过滤可见且非隐藏类型的输入框
            visible_inputs = []
            for elem in input_elements:
                if elem.is_displayed():
                    input_type = (elem.get_attribute("type") or "").lower()
                    if input_type not in ["hidden"]:
                        visible_inputs.append(elem)
            
            return visible_inputs
        except Exception as e:
            logging.error(f"查找输入框失败: {e}")
            return []
    
    def is_input_element(self, element: WebElement) -> bool:
        """判断元素是否是输入框"""
        try:
            tag = element.tag_name.lower()
            input_type = (element.get_attribute('type') or '').lower()
            
            return tag in ['input', 'textarea'] or input_type in [
                'text', 'search', 'email', 'password', 'tel', 'url'
            ]
        except:
            return False


# ============ 主控制类 ============
class WebAutomationTool:
    """Web自动化测试工具主类"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.driver = None
        self.window_manager = None
        self.element_operator = None
        self.script_generator = None
        self.element_counter = 0
        
        self._setup_logging()
        self._check_dependencies()
        self._init_browser()
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        # 清空元素日志文件
        with open(self.config.ELEMENT_LOG_FILE, 'w', encoding='utf-8') as f:
            f.write("")
    
    def _check_dependencies(self):
        """检查依赖"""
        try:
            import selenium
            print(f"Selenium版本: {selenium.__version__}")
        except ImportError:
            print("Selenium未安装，请运行: pip install selenium")
            sys.exit(1)
    
    def _init_browser(self):
        """初始化浏览器"""
        try:
            self.driver = webdriver.Chrome()
            self.window_manager = WindowManager(self.driver)
            self.element_operator = ElementOperator(self.driver, self.config)
            print("浏览器初始化成功!")
        except WebDriverException as e:
            print(f"ChromeDriver初始化失败: {e}")
            print("请确保Chrome浏览器和ChromeDriver已正确安装")
            sys.exit(1)
    
    def open_url(self, url: str) -> bool:
        """打开URL"""
        try:
            self.driver.get(url)
            self.driver.maximize_window()
            WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 初始化脚本生成器
            self.script_generator = TestScriptGenerator(
                self.config.TEST_SCRIPT_FILE, url
            )
            
            print(f"成功打开: {url}")
            self.window_manager.print_window_info()
            return True
        except Exception as e:
            logging.error(f"打开URL失败: {e}")
            return False
    
    def find_and_click_element(self, text: str, auto_mode: bool = False) -> bool:
        """查找并点击元素"""
        # 检查特殊命令
        if text in self.config.INPUT_KEYWORDS:
            return self._handle_input_field()
        elif text in self.config.CUSTOM_ELEMENT_KEYWORDS:
            return self._handle_custom_element()
        elif text in self.config.HOVER_KEYWORDS:
            return self._handle_hover_element()
        
        # 记录点击前的窗口
        previous_windows = set(self.driver.window_handles)
        
        # 查找元素（先精确匹配，再部分匹配）
        elements = self.element_operator.find_elements_by_text(text, exact=True)
        if not elements:
            print(f"未找到精确匹配'{text}'的元素，尝试部分匹配...")
            elements = self.element_operator.find_elements_by_text(text, exact=False)
        
        if not elements:
            print(f"未找到包含'{text}'的元素")
            return False
        
        # 选择元素
        element = self._select_element_from_list(elements, text, auto_mode)
        if not element:
            return False
        
        # 点击或输入
        return self._interact_with_element(element, text, previous_windows)
    
    def _select_element_from_list(self, elements: List[WebElement], 
                                   text: str, auto_mode: bool) -> Optional[WebElement]:
        """从元素列表中选择一个元素"""
        if len(elements) == 1:
            return elements[0]
        
        # 多个元素，让用户选择
        print(f"找到 {len(elements)} 个匹配的元素:")
        for i, elem in enumerate(elements, 1):
            try:
                tag = elem.tag_name
                elem_id = elem.get_attribute('id') or "无ID"
                classes = elem.get_attribute('class') or "无class"
                elem_text = elem.text.strip() if elem.text else "无文本"
                print(f"  {i}. <{tag}> 文本:{elem_text} ID:{elem_id} Class:{classes}")
                self.element_operator.highlight_element(elem, duration=0.5)
            except:
                continue
        
        if auto_mode:
            print("自动化模式：找到多个匹配元素，请选择...")
        
        while True:
            try:
                choice = input(f"请选择要操作的元素 (1-{len(elements)}, 或输入 'q' 退出): ").strip()
                if not choice:
                    continue
                
                # 检查是否退出
                if choice.lower() == 'q':
                    print("已取消本次搜索")
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(elements):
                    return elements[idx]
                else:
                    print(f"请输入 1-{len(elements)} 之间的数字")
            except ValueError:
                print("请输入有效的数字或 'q' 退出")
            except KeyboardInterrupt:
                print("\n用户取消选择")
                return None
    
    def _interact_with_element(self, element: WebElement, text: str, 
                               previous_windows: Set[str]) -> bool:
        """与元素交互（点击或输入）"""
        try:
            self.element_counter += 1
            
            # 高亮显示
            self.element_operator.highlight_element(element, duration=2)
            
            # 判断是否是输入框
            is_input = self.element_operator.is_input_element(element)
            
            if is_input:
                return self._handle_input_interaction(element, text)
            else:
                return self._handle_click_interaction(element, text, previous_windows)
        
        except Exception as e:
            logging.error(f"元素交互失败: {e}")
            return False
    
    def _handle_input_interaction(self, element: WebElement, text: str) -> bool:
        """处理输入框交互"""
        try:
            print("检测到输入框，点击并等待输入...")
            element.click()
            self.element_operator.wait_for_stable_page()
            
            user_input = input("请输入内容: ").strip()
            
            # 清空输入框（标准方法优先 - 速度快，适合大多数网站）
            from selenium.webdriver.common.keys import Keys
            
            # 方法1: 标准clear()方法（快速高效）
            try:
                element.clear()
                time.sleep(0.2)
            except:
                pass
            
            # 方法2: JavaScript清空并触发事件（处理特殊情况）
            try:
                self.driver.execute_script("""
                    arguments[0].value = '';
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, element)
                time.sleep(0.2)
            except:
                pass
            
            # 方法3: 物理按键清空（最后手段，适用于自定义控件）
            try:
                element.send_keys(Keys.CONTROL + 'a')
                time.sleep(0.1)
                element.send_keys(Keys.BACKSPACE)
                time.sleep(0.1)
            except:
                pass
            
            element.send_keys(user_input)
            
            # 生成测试代码
            self._save_element_to_script(element, text, "输入", user_input)
            
            print(f"输入完成: {user_input}")
            return True
        except Exception as e:
            logging.error(f"输入操作失败: {e}")
            return False
    
    def _handle_click_interaction(self, element: WebElement, text: str, 
                                  previous_windows: Set[str]) -> bool:
        """处理点击交互"""
        try:
            # 先生成测试代码
            self._save_element_to_script(element, text, "点击", "")
            
            # 点击元素
            if not self.element_operator.click_element_safely(element):
                return False
            
            # 等待页面稳定
            self.element_operator.wait_for_stable_page()
            
            # 检查并切换窗口
            if self.window_manager.switch_to_new_window(previous_windows):
                self.window_manager.print_window_info()
            else:
                print("页面已跳转")
                self.window_manager.print_window_info()
            
            return True
        except Exception as e:
            logging.error(f"点击操作失败: {e}")
            return False
    
    def _save_element_to_script(self, element: WebElement, text: str, 
                               operation: str, user_input: str = ""):
        """保存元素到测试脚本（包含备选定位器）"""
        try:
            # 生成定位器（使用配置中的简洁模式设置）
            locators = ElementLocatorGenerator.generate_locators(
                element, text, use_simple_css=self.config.USE_SIMPLE_CSS_PATH
            )
            best_locator = ElementLocatorGenerator.select_best_locator(locators)
            
            if best_locator:
                # 获取备选定位器（优先选择不同类型的定位器）
                alternative_locators = []
                
                # 优先级：选择与主定位器不同类型的定位器
                # 1. 如果主定位器是LINK_TEXT，备选使用XPATH、ID、属性
                # 2. 如果主定位器是XPATH，备选使用LINK_TEXT、ID、属性
                # 3. 避免使用不稳定的CSS路径作为备选
                
                used_types = {best_locator[0]}  # 已使用的定位器类型
                
                for loc in locators:
                    if loc == best_locator:
                        continue
                    
                    loc_type, loc_value = loc
                    
                    # 跳过已使用的类型（除非是CSS_SELECTOR，可以有多个不同的CSS选择器）
                    if loc_type in used_types and loc_type != 'By.CSS_SELECTOR':
                        continue
                    
                    # 跳过过长的CSS路径（大于100字符，通常太脆弱）
                    if loc_type == 'By.CSS_SELECTOR' and ' > ' in loc_value and len(loc_value) > 100:
                        continue
                    
                    # 跳过太宽泛的选择器（如 a[href*='/']）
                    if '[href*=' in loc_value and loc_value.count('/') <= 1:
                        continue
                    
                    alternative_locators.append(loc)
                    used_types.add(loc_type)
                    
                    if len(alternative_locators) >= 3:
                        break
                
                # 打印使用的定位器（让用户看到生成的定位器）
                print(f"\n📍 主定位器:")
                print(f"   类型: {best_locator[0]}")
                print(f"   选择器: {best_locator[1][:100]}{'...' if len(best_locator[1]) > 100 else ''}")
                
                if alternative_locators:
                    print(f"📍 备选定位器 ({len(alternative_locators)}个):")
                    for i, (alt_type, alt_sel) in enumerate(alternative_locators, 1):
                        display_sel = alt_sel[:80] + '...' if len(alt_sel) > 80 else alt_sel
                        print(f"   {i}. {alt_type}: {display_sel}")
                else:
                    print(f"⚠ 无合适的备选定位器（将仅使用主定位器）")
                
                element_data = {
                    'search_text': text,
                    'selector_type': best_locator[0],
                    'selector': best_locator[1],
                    'alternative_locators': alternative_locators,
                    'operation_type': operation,
                    'user_input': user_input
                }
                self.script_generator.add_test_method(element_data)
        except Exception as e:
            logging.error(f"保存测试脚本失败: {e}")
    
    def _handle_input_field(self) -> bool:
        """处理输入框特殊命令"""
        input_elements = self.element_operator.find_input_elements()
        
        if not input_elements:
            print("未找到可见的输入框")
            return False
        
        if len(input_elements) == 1:
            element = input_elements[0]
        else:
            element = self._select_element_from_list(input_elements, "输入框", False)
            if not element:
                return False
        
        previous_windows = set(self.driver.window_handles)
        return self._interact_with_element(element, "输入框", previous_windows)
    
    def _handle_custom_element(self) -> bool:
        """处理自定义元素命令"""
        try:
            element_name = input("请输入元素名称: ").strip()
            if not element_name:
                print("元素名称不能为空")
                return False
            
            css_selector = input("请输入CSS选择器: ").strip()
            if not css_selector:
                print("CSS选择器不能为空")
                return False
            
            # 保存到脚本（默认使用点击操作）
            element_data = {
                'search_text': element_name,
                'selector_type': 'By.CSS_SELECTOR',
                'selector': css_selector,
                'operation_type': '点击',
                'user_input': ''
            }
            self.script_generator.add_test_method(element_data)
            
            # 记录操作前的窗口（重要：用于检测新窗口）
            previous_windows = set(self.driver.window_handles)
            
            # 执行点击操作
            element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
            self.element_operator.click_element_safely(element)
            
            # 等待页面稳定
            self.element_operator.wait_for_stable_page()
            
            # 检查并切换到新窗口
            if self.window_manager.switch_to_new_window(previous_windows):
                print(f"检测到新窗口，已自动切换")
                self.window_manager.print_window_info()
            else:
                print("页面已更新")
                self.window_manager.print_window_info()
            
            print(f"已添加并执行自定义元素: {element_name}")
            return True
        except Exception as e:
            logging.error(f"处理自定义元素失败: {e}")
            print(f"错误: {e}")
            return False
    
    def _handle_hover_element(self) -> bool:
        """处理鼠标悬浮命令"""
        try:
            # 让用户选择定位方式
            print("\n请选择定位方式:")
            print("  1. 使用CSS选择器")
            print("  2. 使用文本")
            choice = input("请选择 (1 或 2): ").strip()
            
            if choice == '1':
                # 使用CSS选择器
                element_name = input("请输入元素名称: ").strip()
                if not element_name:
                    print("元素名称不能为空")
                    return False
                
                css_selector = input("请输入CSS选择器: ").strip()
                if not css_selector:
                    print("CSS选择器不能为空")
                    return False
                
                # 查找元素
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
                except Exception as e:
                    print(f"未找到元素: {e}")
                    return False
                
                # 高亮显示
                self.element_operator.highlight_element(element, duration=2)
                
                # 保存到脚本
                element_data = {
                    'search_text': element_name,
                    'selector_type': 'By.CSS_SELECTOR',
                    'selector': css_selector,
                    'operation_type': '悬浮',
                    'user_input': ''
                }
                self.script_generator.add_test_method(element_data)
                
                # 执行悬浮
                if self.element_operator.hover_element_safely(element):
                    self.element_operator.wait_for_stable_page()
                    print(f"已悬浮到元素: {element_name}")
                    return True
                else:
                    print(f"悬浮操作失败")
                    return False
                
            elif choice == '2':
                # 使用文本
                element_text = input("请输入要悬浮的元素文本: ").strip()
                if not element_text:
                    print("元素文本不能为空")
                    return False
                
                # 查找元素（先精确匹配，再部分匹配）
                elements = self.element_operator.find_elements_by_text(element_text, exact=True)
                if not elements:
                    print(f"未找到精确匹配'{element_text}'的元素，尝试部分匹配...")
                    elements = self.element_operator.find_elements_by_text(element_text, exact=False)
                
                if not elements:
                    print(f"未找到包含'{element_text}'的元素")
                    return False
                
                # 选择元素
                element = self._select_element_from_list(elements, element_text, False)
                if not element:
                    return False
                
                # 高亮显示
                self.element_operator.highlight_element(element, duration=2)
                
                # 生成定位器并保存
                locators = ElementLocatorGenerator.generate_locators(
                    element, element_text, use_simple_css=self.config.USE_SIMPLE_CSS_PATH
                )
                best_locator = ElementLocatorGenerator.select_best_locator(locators)
                
                if best_locator:
                    print(f"\n📍 使用的定位器:")
                    print(f"   类型: {best_locator[0]}")
                    print(f"   选择器: {best_locator[1]}")
                    
                    element_data = {
                        'search_text': element_text,
                        'selector_type': best_locator[0],
                        'selector': best_locator[1],
                        'operation_type': '悬浮',
                        'user_input': ''
                    }
                    self.script_generator.add_test_method(element_data)
                
                # 执行鼠标悬浮操作
                if self.element_operator.hover_element_safely(element):
                    # 等待页面稳定
                    self.element_operator.wait_for_stable_page()
                    print(f"已悬浮到元素: {element_text}")
                    return True
                else:
                    print(f"悬浮操作失败")
                    return False
            else:
                print("无效的选择，请输入 1 或 2")
                return False
                
        except Exception as e:
            logging.error(f"处理鼠标悬浮失败: {e}")
            print(f"错误: {e}")
            return False
    
    def automated_workflow(self, texts: List[str]):
        """自动化工作流"""
        print("=" * 50)
        print(f"自动化模式: 将依次处理 {len(texts)} 个元素")
        print(f"元素列表: {', '.join(texts)}")
        print("=" * 50)
        
        for i, text in enumerate(texts, 1):
            if not text.strip():
                continue
            
            # 支持重试机制
            retry_count = 1
            while True:
                print(f"\n[{i}/{len(texts)}] 正在处理: '{text}'" + (f" (第{retry_count}次尝试)" if retry_count > 1 else ""))
                
                success = self.find_and_click_element(text, auto_mode=True)
                
                if success:
                    break  # 成功则跳出重试循环
                
                # 失败时询问用户
                print(f"处理 '{text}' 失败")
                choice = input("请选择操作 (1-重试, 2-跳过, 3-停止): ").strip()
                
                if choice == '3':
                    print("停止自动化流程")
                    return  # 直接返回，结束整个流程
                elif choice == '2':
                    print(f"跳过 '{text}'")
                    break  # 跳出重试循环，继续下一个元素
                elif choice == '1':
                    retry_count += 1
                    continue  # 继续重试循环
                else:
                    print("无效选择，默认重试")
                    retry_count += 1
                    continue
            
            time.sleep(1)
        
        print("\n自动化流程完成")
    
    def interactive_workflow(self):
        """交互式工作流"""
        print("=" * 80)
        print("Web自动化测试工具 - 前置步骤+业务步骤模式")
        print("=" * 80)
        print("功能说明:")
        print("- 输入元素文本进行查找和点击")
        print("- 输入'输入框'查找输入框元素")
        print("- 输入'悬浮'执行鼠标悬浮操作")
        print("- 输入'添加'手动添加CSS选择器（只点击）")
        print("- 输入'窗口'切换浏览器窗口")
        print("- 输入'b'完成前置步骤，开始添加具体业务步骤")
        print("- 输入'a'添加新测试用例（完成当前测试用例，开始新的测试用例）")
        print("- 输入'l'显示所有已添加的操作")
        print("- 输入'r'删除某个已添加的操作")
        print("- 使用分号(；)分隔多个元素启动自动化模式")
        print("- 输入'quit'退出程序并生成参数化测试脚本")
        print("=" * 80)
        
        # 初始提示收集前置步骤
        if self.script_generator:
            print("\n" + "="*80)
            print("📝 第一步：请先添加所有需求共享的前置步骤（共同的操作）")
            print("   例如：悬浮菜单、点击机票、选择单程等")
            print("   完成后输入 'b' 开始添加具体需求")
            print("="*80)
        
        while True:
            try:
                # 显示窗口和当前状态信息
                self.window_manager.print_window_info()
                if self.script_generator:
                    if self.script_generator.is_collecting_precondition:
                        print(f"【前置步骤收集中】", end=" ")
                    elif self.script_generator.current_requirement:
                        print(f"【当前需求: {self.script_generator.current_requirement}】", end=" ")
                user_input = input("请输入操作 (或命令): ").strip()
                
                # 退出命令
                if user_input.lower() in self.config.EXIT_KEYWORDS:
                    print("程序结束")
                    break
                
                # 'b' 命令：完成前置步骤，开始业务步骤
                if user_input.lower() == 'b':
                    if not self.script_generator:
                        print("脚本生成器未初始化")
                        continue
                    
                    if not self.script_generator.is_collecting_precondition:
                        print("⚠ 当前已经在业务步骤收集模式")
                        continue
                    
                    precond_count = len(self.script_generator.precondition_steps_data)
                    
                    print(f"\n{'='*80}")
                    print(f"✓ 前置步骤收集完成: 共 {precond_count} 个步骤")
                    print(f"{'='*80}")
                    
                    # 切换到业务步骤收集模式
                    self.script_generator.is_collecting_precondition = False
                    self.script_generator.precondition_completed = True
                    
                    # 立即要求输入第一个需求编号
                    print(f"\n📝 请输入第一个需求编号:")
                    while True:
                        req_input = input("请输入需求编号 (格式：R001, R002等): ").strip()
                        if not req_input:
                            print("需求编号不能为空")
                            continue
                        if self.script_generator.set_current_requirement(req_input):
                            print(f"\n✓ 现在可以开始添加需求 {req_input} 的具体业务步骤")
                            break
                    continue
                
                # 添加新测试用例命令
                if user_input.lower() == 'a':
                    if not self.script_generator:
                        print("脚本生成器未初始化")
                        continue
                    
                    current_req = self.script_generator.current_requirement
                    current_steps = len(self.script_generator.requirements.get(current_req, []))
                    
                    print(f"\n{'='*80}")
                    print(f"✓ 测试用例 {current_req} 已完成，共收集 {current_steps} 个步骤")
                    print(f"{'='*80}")
                    
                    # 关闭当前浏览器
                    print("\n🔴 关闭当前浏览器...")
                    try:
                        self.driver.quit()
                    except:
                        pass
                    
                    # 重新打开新浏览器
                    print("🚀 启动新浏览器...")
                    try:
                        self._init_browser()
                        initial_url = self.script_generator.initial_url
                        self.driver.get(initial_url)
                        self.driver.maximize_window()
                        print(f"✓ 已打开: {initial_url}")
                    except Exception as e:
                        print(f"⚠ 重新打开浏览器失败: {e}")
                        print("程序将退出")
                        break
                    
                    existing_reqs = sorted(self.script_generator.requirements.keys())
                    if existing_reqs:
                        print(f"\n已有测试用例: {', '.join(existing_reqs)}")
                    print("\n请输入新测试用例的需求编号:")
                    print("💡 提示：请使用不同的需求编号，避免重复")
                    
                    new_req_id = None
                    while True:
                        req_input = input("请输入需求编号 (格式：R001, R002等, 或输入'c'取消): ").strip()
                        if req_input.lower() == 'c':
                            print("已取消添加新测试用例")
                            break
                        if not req_input:
                            print("需求编号不能为空")
                            continue
                        if self.script_generator.set_current_requirement(req_input):
                            new_req_id = req_input
                            print(f"\n✓ 开始收集测试用例 {req_input} 的操作步骤")
                            break
                    
                    if new_req_id is None:
                        continue
                    
                    # 执行共享的前置步骤（如果有的话）
                    if self.script_generator.precondition_steps_data:
                        print(f"\n🔄 正在执行前置步骤...")
                        for step in self.script_generator.precondition_steps_data:
                            print(f"  执行: {step['test_name']}")
                            
                            # 根据操作类型执行相应操作
                            from selenium.webdriver.common.by import By as ByClass
                            from selenium.webdriver.support.ui import WebDriverWait
                            from selenium.webdriver.support import expected_conditions as EC
                            
                            element = None
                            try:
                                # 尝试使用主定位器，带等待
                                by_type = getattr(ByClass, step['by_type'])
                                wait = WebDriverWait(self.driver, 10)
                                element = wait.until(EC.presence_of_element_located((by_type, step['locator'])))
                            except Exception as e1:
                                # 尝试备选定位器
                                alternative_locators = step.get('alternative_locators', [])
                                if alternative_locators:
                                    for alt_by, alt_locator in alternative_locators:
                                        try:
                                            alt_by_type = getattr(ByClass, alt_by.replace('By.', ''))
                                            wait = WebDriverWait(self.driver, 5)
                                            element = wait.until(EC.presence_of_element_located((alt_by_type, alt_locator)))
                                            break
                                        except:
                                            continue
                            
                            if element:
                                try:
                                    if step['action_type'] == 'click':
                                        self.element_operator.click_element_safely(element)
                                    elif step['action_type'] == 'input':
                                        element.clear()
                                        time.sleep(0.2)
                                        element.send_keys(step['input_data'])
                                    elif step['action_type'] == 'hover':
                                        self.element_operator.hover_element_safely(element)
                                    
                                    # 等待操作完成
                                    time.sleep(1)
                                except Exception as e:
                                    print(f"  ⚠ 执行操作失败: {e}")
                            else:
                                print(f"  ⚠ 未找到元素: {step['test_name']}")
                        
                        print(f"✓ 前置步骤执行完成")
                        time.sleep(1)  # 额外等待，确保页面稳定
                    
                    continue
                
                # 显示所有已添加的操作
                if user_input.lower() == 'l':
                    if self.script_generator:
                        self.script_generator.list_all_steps()
                    else:
                        print("脚本生成器未初始化")
                    continue
                
                # 删除某个已添加的操作
                if user_input.lower() == 'r':
                    if not self.script_generator:
                        print("脚本生成器未初始化")
                        continue
                    
                    # 先显示所有步骤
                    self.script_generator.list_all_steps()
                    
                    if not self.script_generator.test_steps_data:
                        continue
                    
                    # 让用户选择要删除的步骤
                    try:
                        total_steps = len(self.script_generator.test_steps_data)
                        choice = input(f"\n请选择要删除的步骤 (1-{total_steps}, 或输入 'c' 取消): ").strip()
                        
                        if choice.lower() == 'c':
                            print("已取消删除操作")
                            continue
                        
                        step_index = int(choice) - 1
                        self.script_generator.remove_step(step_index)
                    except ValueError:
                        print("请输入有效的数字")
                    except Exception as e:
                        print(f"删除失败: {e}")
                    continue
                
                # 窗口管理命令
                if user_input.lower() in self.config.WINDOW_KEYWORDS:
                    success, window_index, window_title = self.window_manager.list_and_switch_windows(self.script_generator)
                    
                    # 记录窗口切换操作到测试脚本
                    if success and window_index > 0 and self.script_generator:
                        self.script_generator.add_window_switch_method(window_index, window_title)
                    continue
                
                if user_input.lower() in ['back', '返回']:
                    self.window_manager.switch_to_original()
                    continue
                
                if user_input.lower() in ['close', '关闭']:
                    self.window_manager.close_current_window()
                    continue
                
                if not user_input:
                    print("请输入有效的内容")
                    continue
                
                # 自动化模式（分号分隔）
                if '；' in user_input or ',' in user_input:
                    separator = '；' if '；' in user_input else ','
                    texts = [t.strip() for t in user_input.split(separator) if t.strip()]
                    if len(texts) > 1:
                        self.automated_workflow(texts)
                        continue
                    elif len(texts) == 1:
                        user_input = texts[0]
                
                # 单步模式
                self.find_and_click_element(user_input)
                
            except KeyboardInterrupt:
                print("\n程序被用户中断")
                break
            except Exception as e:
                logging.error(f"操作过程中出错: {e}")
                print(f"发生错误: {e}")
    
    def close(self):
        """关闭浏览器并完成脚本"""
        if self.driver:
            if self.script_generator:
                self.script_generator.complete_script()
            self.driver.quit()
            print("浏览器已关闭")


# ============ 主程序 ============
def main():
    """主程序入口"""
    config = Config()
    tool = WebAutomationTool(config)
    
    try:
        print("=" * 50)
        print("网页元素自动提取工具 - 优化版")
        print("=" * 50)
        
        # 获取URL
        url = input("请输入要打开的网页URL (默认: https://www.ctrip.com): ").strip()
        if not url:
            url = "https://www.ctrip.com"
        
        if not url.startswith(('http://', 'https://')):
            print("请输入有效的URL")
            return
        
        print(f"正在打开: {url}")
        
        if tool.open_url(url):
            tool.interactive_workflow()
        else:
            print("无法打开网页，程序结束")
    
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        logging.error(f"程序运行出错: {e}")
        print(f"程序运行出错: {e}")
    finally:
        tool.close()


if __name__ == "__main__":
    main()

