# 🚀 携程机票查询自动化测试框架

## 📖 项目简介

本项目是一个完整的Web自动化测试解决方案，包含智能录制工具(`web_optimized.py`)和生成的测试脚本(`TestCtripFlight.py`)。专门针对携程网机票查询功能进行设计和优化，实现了从测试用例录制、脚本生成到自动化执行的完整流程。

### ✨ 核心特性

- 🎯 **智能录制工具** - 交互式录制操作，自动生成Pytest测试脚本
- 🧪 **参数化测试** - 基于Pytest框架，每个步骤作为独立测试用例执行
- 🛡️ **容错机制** - 主定位器+多个备选定位器，自动重试提高稳定性
- 📦 **需求分组** - 前置步骤（PreCondition）与业务步骤分离，按R001-R004需求编号分组
- 🔄 **强力清空** - 多重清空机制（物理按键+JavaScript+标准方法）适配携程自定义控件
- 📸 **自动截图** - 每个测试步骤自动截图，时间戳+用例编号命名
- 🎨 **规范输出** - 符合软件测试规范的脚本格式和命名规则

---

## 🎯 适用场景

- ✅ 携程网机票查询功能自动化测试
- ✅ Web应用UI自动化测试
- ✅ 回归测试和冒烟测试
- ✅ 测试脚本快速生成和原型开发

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.7+ | 开发语言 |
| **Selenium** | 4.0+ | Web自动化框架 |
| **Pytest** | 7.0+ | 测试框架，支持参数化 |
| **Chrome** | 最新版 | 测试浏览器 |
| **ChromeDriver** | 匹配Chrome版本 | 浏览器驱动 |
| **openpyxl** | 3.0+ | Excel文件处理 |

---

## 📋 环境准备

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install selenium>=4.0.0
pip install pytest>=7.0.0
pip install openpyxl>=3.0.0
pip install pytest-html>=3.1.0
```

### 2. 配置ChromeDriver

下载与Chrome浏览器版本匹配的ChromeDriver：
- 下载地址：https://chromedriver.chromium.org/
- 将ChromeDriver路径配置到脚本中（详见下方说明）

---

## 📁 项目结构

```
Software-Testing/
├── web_optimized.py              # 智能录制工具（2170行）
├── TestCtripFlight.py            # 生成的测试脚本（271行）
├── 测试用例文档.py                # Excel测试用例生成工具
├── requirements.txt              # Python依赖包列表
├── README.md                     # 项目说明文档（本文件）
├── VERSION.md                    # 版本信息
├── LICENSE                       # MIT许可证
├── CHANGELOG.md                  # 版本更新日志
├── clicked_elements.log          # 操作日志（自动生成）
└── screenshots/                  # 截图目录（自动创建）
    ├── 时间戳_CtripFlight_R001_001.png
    ├── 时间戳_CtripFlight_R001_002.png
    └── ...
```

---

## 🚀 快速开始

### 方式一：使用已生成的测试脚本

#### 1. 配置ChromeDriver路径

编辑 `TestCtripFlight.py` 第15行：

```python
service = Service(executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe")
```

修改为你的ChromeDriver实际路径。

#### 2. 运行测试

```bash
# 运行所有测试
pytest TestCtripFlight.py -v

# 运行特定需求的测试
pytest TestCtripFlight.py::TestCtripFlight_R001 -v

# 显示详细输出
pytest TestCtripFlight.py -v -s

# 生成HTML报告
pytest TestCtripFlight.py -v --html=report.html
```

#### 3. 查看结果

- 控制台输出：测试执行结果
- screenshots目录：每个步骤的截图
- report.html：HTML测试报告（如使用--html参数）

### 方式二：使用录制工具生成新脚本

#### 1. 配置ChromeDriver路径

编辑 `web_optimized.py` 第571行：

```python
executable_path="C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chromedriver.exe"
```

#### 2. 启动录制工具

```bash
python web_optimized.py
```

#### 3. 录制测试操作

```
请输入要打开的网页URL (默认: https://www.ctrip.com): 
[按Enter使用默认]

成功打开: https://www.ctrip.com

==================================================
📝 第一步：请先添加所有需求共享的前置步骤（共同的操作）
   例如：悬浮菜单、点击机票、选择单程等
   完成后输入 'b' 开始添加具体需求
==================================================

【前置步骤收集中】 请输入操作: 悬浮
```

#### 4. 基本操作命令

| 命令 | 功能 | 示例 |
|------|------|------|
| **元素文本** | 查找并点击/输入元素 | `机票` `搜索` |
| **输入框** | 查找输入框元素 | `输入框` |
| **悬浮** | 鼠标悬浮操作 | `悬浮` |
| **添加** | 自定义CSS选择器 | `添加` |
| **窗口** | 切换浏览器窗口 | `窗口` |
| **b** | 完成前置步骤，开始业务步骤 | `b` |
| **a** | 添加新测试用例（重启浏览器） | `a` |
| **l** | 列出所有已添加的步骤 | `l` |
| **r** | 删除指定步骤 | `r` |
| **quit** | 退出并生成测试脚本 | `quit` |

#### 5. 录制流程示例

```
# 步骤1：录制前置步骤
【前置步骤收集中】 请输入操作: 悬浮
请选择定位方式:
  1. 使用CSS选择器
  2. 使用文本
请选择 (1 或 2): 2
请输入要悬浮的元素文本: 机票

【前置步骤收集中】 请输入操作: 国内/国际/中国港澳台

【前置步骤收集中】 请输入操作: 单程

# 步骤2：完成前置步骤，开始业务步骤
【前置步骤收集中】 请输入操作: b

✓ 前置步骤收集完成: 共 3 个步骤

📝 请输入第一个需求编号:
请输入需求编号 (格式：R001, R002等): R001

# 步骤3：录制业务步骤
【当前需求: R001】 请输入操作: 北京
检测到输入框，点击并等待输入...
请输入内容: 北京

【当前需求: R001】 请输入操作: 广州
请输入内容: 广州

【当前需求: R001】 请输入操作: 不限舱等

【当前需求: R001】 请输入操作: 经济舱

【当前需求: R001】 请输入操作: 带儿童

【当前需求: R001】 请输入操作: 搜索

# 步骤4：添加新测试用例
【当前需求: R001】 请输入操作: a

✓ 测试用例 R001 已完成，共收集 6 个步骤

🔴 关闭当前浏览器...
🚀 启动新浏览器...

请输入需求编号 (格式：R001, R002等): R002

# 步骤5：退出并生成脚本
【当前需求: R002】 请输入操作: quit

================================================================================
✓ 测试脚本生成完成: TestCtripFlight.py
================================================================================
  前置步骤总数: 3
  业务步骤总数: 10
  需求数量: 2
```

---

## 📚 测试脚本详解

### 脚本结构

生成的 `TestCtripFlight.py` 包含以下部分：

```python
# 1. Pytest fixture - 浏览器驱动管理
@pytest.fixture(scope="class")
def driver():
    # 初始化Chrome浏览器
    # 打开携程网
    # 测试结束后关闭浏览器
    
# 2. 基础类 - 通用操作方法
class BaseCtripFlight:
    def execute_action(self, driver, by_type, locator, action_type, 
                      input_data=None, alternative_locators=None):
        # 统一的操作执行方法
        # 支持click、input、hover、window_switch
        # 支持备选定位器自动重试
        
    def _find_element_with_fallback(self, driver, by_type, locator, 
                                    alternative_locators=None, timeout=10):
        # 查找元素，失败后尝试备选定位器
        
    @staticmethod
    def take_screenshot(driver, file_name):
        # 截图并保存
        
# 3. 前置步骤类 - 所有需求共享
class PreCondition:
    PRECONDITION_DATA = [
        # 前置步骤数据列表
        ("PreCondition_P001", By.CSS_SELECTOR, "...", [...], "hover", "菜单", None),
        ("PreCondition_P002", By.XPATH, "...", [...], "click", "机票", None),
        # ...
    ]
    
# 4. 测试类 - 按需求编号分组
class TestCtripFlight_R001(BaseCtripFlight):
    _precondition_executed = False
    
    TEST_DATA_R001 = [
        # 测试步骤数据（参数化）
        ("CtripFlight_R001_001", By.NAME, "owDCity", [...], "input", "输入框", "北京"),
        ("CtripFlight_R001_002", By.NAME, "owACity", [...], "input", "输入框", "广州"),
        # ...
    ]
    
    @pytest.mark.parametrize(
        "test_case_id, by_type, locator, alternative_locators, action_type, test_name, input_data",
        TEST_DATA_R001,
        ids=[step[0] for step in TEST_DATA_R001]
    )
    def test_CtripFlight_R001(self, driver, test_case_id, by_type, locator, ...):
        # 第一个步骤执行前置步骤
        if not TestCtripFlight_R001._precondition_executed:
            for precond_step in PreCondition.PRECONDITION_DATA:
                self.execute_action(driver, ...)
            TestCtripFlight_R001._precondition_executed = True
        
        # 执行业务步骤
        self.execute_action(driver, by_type, locator, action_type, input_data, alternative_locators)
        self.take_screenshot(driver, f"{test_case_id}.png")
        sleep(1)

# 5. 其他测试类（R002、R003、R004...）
class TestCtripFlight_R002(BaseCtripFlight):
    # 同样的结构
```

### 关键特性

#### 1. 前置步骤与业务步骤分离

```python
# 前置步骤 - 所有需求共享（只执行一次）
PreCondition.PRECONDITION_DATA = [
    ("PreCondition_P001", ..., "hover", "菜单", None),
    ("PreCondition_P002", ..., "click", "机票", None),
    ("PreCondition_P003", ..., "click", "单程", None),
]

# 业务步骤 - 每个需求独立
TEST_DATA_R001 = [
    ("CtripFlight_R001_001", ..., "input", "输入框", "北京"),
    ("CtripFlight_R001_002", ..., "input", "输入框", "广州"),
    # ...
]
```

#### 2. 备选定位器容错机制

```python
# 主定位器 + 备选定位器列表
("CtripFlight_R001_001", 
 By.NAME,                          # 主定位器类型
 "owDCity",                        # 主定位器值
 [                                 # 备选定位器列表
     (By.CSS_SELECTOR, "input[name='owDCity']"),
     (By.CSS_SELECTOR, "input[type='text']"),
     (By.CSS_SELECTOR, "input[placeholder='可输入城市或机场']")
 ],
 "input",                          # 操作类型
 "输入框",                         # 操作名称
 "北京")                           # 输入数据
```

运行时，如果主定位器失败，会自动尝试备选定位器。

#### 3. 强力清空输入框

```python
# execute_action方法中的input操作
elif action_type == 'input':
    element = self._find_element_with_fallback(driver, by_type, locator, 
                                               alternative_locators, timeout=20)
    element.click()
    sleep(0.3)
    
    # 方法1: 标准clear()
    try:
        element.clear()
        sleep(0.2)
    except:
        pass
    
    # 方法2: JavaScript清空并触发事件
    try:
        driver.execute_script("""
            arguments[0].value = '';
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """, element)
        sleep(0.2)
    except:
        pass
    
    # 方法3: 物理按键清空（最可靠）
    try:
        element.send_keys(Keys.CONTROL + 'a')
        sleep(0.1)
        element.send_keys(Keys.BACKSPACE)
        sleep(0.1)
    except:
        pass
    
    # 最后输入新内容
    element.send_keys(input_data)
```

#### 4. Pytest参数化测试

每个步骤作为独立的测试用例执行：

```bash
pytest TestCtripFlight.py -v

# 输出示例
TestCtripFlight.py::TestCtripFlight_R001::test_CtripFlight_R001[CtripFlight_R001_001] PASSED
TestCtripFlight.py::TestCtripFlight_R001::test_CtripFlight_R001[CtripFlight_R001_002] PASSED
TestCtripFlight.py::TestCtripFlight_R001::test_CtripFlight_R001[CtripFlight_R001_003] PASSED
...
```

---

## 🔧 配置说明

### ChromeDriver路径配置

#### 开发环境路径
```python
executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe"
```

#### 生产环境路径（根据实际情况修改）
```python
executable_path="C:\\Users\\YourUsername\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe"
```

### Fixture作用域

```python
@pytest.fixture(scope="class")  # 每个测试类执行一次
# 或
@pytest.fixture(scope="function")  # 每个测试方法执行一次
```

- `scope="class"`: 所有测试执行完后关闭浏览器（速度快，推荐）
- `scope="function"`: 每个测试执行完就关闭浏览器（独立性强但慢）

---

## 📸 截图命名规则

```
时间戳_测试用例编号.png

示例：
130613160848_CtripFlight_R001_001.png
  │             │         │    │
  │             │         │    └─ 步骤编号
  │             │         └────── 需求编号
  │             └──────────────── 项目名称
  └──────────────────────────── 时间戳（HHMMSSddfffff）
```

---

## 🐛 常见问题

### Q1: 找不到ChromeDriver

**错误信息**：
```
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

**解决方法**：
1. 下载与Chrome版本匹配的ChromeDriver
2. 配置脚本中的ChromeDriver路径
3. 或将ChromeDriver添加到系统PATH环境变量

### Q2: 元素定位失败

**错误信息**：
```
selenium.common.exceptions.TimeoutException: Message: 
NoSuchElementException: 无法找到元素: 主定位器和所有备选定位器均失败
```

**解决方法**：
1. 检查页面是否已完全加载
2. 增加等待时间（修改timeout参数）
3. 检查元素是否在iframe中
4. 使用录制工具重新生成定位器

### Q3: 输入框没有清空

**解决方法**：
- 脚本已使用四重清空机制（标准clear + JavaScript + 物理按键）
- 如仍未清空，检查是否为特殊控件，可能需要额外处理

### Q4: 测试执行速度慢

**优化方法**：
1. 减少sleep时间（需要确保稳定性）
2. 使用`scope="class"`而非`scope="function"`
3. 合并相关测试用例

---

## 📊 测试报告

### 生成HTML报告

```bash
pytest TestCtripFlight.py -v --html=report.html --self-contained-html
```

报告包含：
- ✅ 测试用例执行结果
- ⏱️ 执行时间统计
- 📸 截图链接
- 📝 错误信息和堆栈跟踪

---

## 📝 测试用例规范

### 测试用例编号格式

```
CtripFlight_R001_001
    │         │    │
    │         │    └─ 步骤编号（001-999）
    │         └────── 需求编号（R001-R999）
    └──────────────── 项目名称（CtripFlight）
```

### 需求编号格式

- ✅ 正确：`R001`, `R002`, `R010`, `R100`
- ❌ 错误：`r001`（小写）, `R01`（两位）, `ROO1`（字母O）

---

## 🎯 最佳实践

### 录制测试用例时

- ✅ 等待页面完全加载后再操作
- ✅ 使用清晰、唯一的元素文本
- ✅ 按业务逻辑分组需求
- ✅ 及时删除错误的录制步骤
- ✅ 使用`l`命令查看已录制步骤

### 运行测试时

- ✅ 先测试运行一次，确保正常
- ✅ 删除调试过程产生的多余截图
- ✅ 确保ChromeDriver路径正确
- ✅ 检查网络连接稳定性

### 提交前检查

- ✅ 脚本编码为UTF-8
- ✅ 测试用例编号格式正确
- ✅ 需求编号大写（R001不是r001）
- ✅ 截图文件名与用例编号对应
- ✅ 所有截图在screenshots文件夹

---

## 📞 技术支持

### 项目信息

- **版本**: v2.0
- **更新日期**: 2025-10-29
- **Python版本**: 3.7+
- **许可证**: MIT

### 相关文档

- `VERSION.md` - 版本详细信息
- `CHANGELOG.md` - 版本更新日志
- `LICENSE` - 许可证文件

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和测试人员！

---

<div align="center">

**🎉 祝测试愉快！**

Made with ❤️ for Software Testing

</div>
