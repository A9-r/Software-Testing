# 🚀 Web自动化测试工具 - 携程机票查询测试项目

## 📖 项目简介

这是一个专为Web自动化测试设计的智能录制和回放工具，特别针对携程网机票查询功能进行优化。该工具能够自动录制用户在网页上的操作，智能生成高质量的Pytest + Selenium测试脚本，并完全符合软件测试比赛的规范要求。

### ✨ 核心特性

- 🎯 **零代码录制** - 通过文本描述即可定位元素，无需手动编写代码
- 🧠 **智能定位** - 自动生成多种定位策略（XPath、CSS、ID等），并选择最优方案
- 🛡️ **容错机制** - 备选定位器自动切换，提高脚本稳定性
- 📦 **需求管理** - 按R001、R002等需求编号自动分组管理测试用例
- 🎨 **规范输出** - 生成的脚本完全符合比赛要求格式
- 📸 **自动截图** - 每个测试步骤自动截图并保存
- 🔄 **强力清空** - 特别针对携程等网站的自定义输入控件优化

---

## 🎯 适用场景

- ✅ 软件测试大赛自动化测试项目
- ✅ 携程网机票查询功能测试
- ✅ Web应用UI自动化测试
- ✅ 回归测试和冒烟测试
- ✅ 测试脚本快速原型开发

---

## 🛠️ 技术栈

- **Python** 3.7+
- **Selenium** 4.0+ - Web自动化框架
- **Pytest** 7.0+ - 测试框架
- **Chrome** + **ChromeDriver** - 浏览器驱动
- **openpyxl** - Excel文件处理

---

## 📋 环境要求

### 1. 必需软件

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.7+ | 推荐使用 3.8 或更高版本 |
| Google Chrome | 最新版 | 确保与ChromeDriver版本匹配 |
| ChromeDriver | 匹配Chrome版本 | 下载地址：https://chromedriver.chromium.org/ |

### 2. Python依赖包

```bash
pip install selenium>=4.0.0
pip install pytest>=7.0.0
pip install openpyxl>=3.0.0
```

或使用requirements.txt：

```bash
pip install -r requirements.txt
```

---

## 🚀 快速开始

### 第一步：克隆或下载项目

```bash
git clone <repository-url>
cd <project-directory>
```

### 第二步：安装依赖

```bash
pip install -r requirements.txt
```

### 第三步：配置ChromeDriver路径

编辑 `web_optimized.py`，修改ChromeDriver路径：

```python
# 找到这一行并修改为你的ChromeDriver路径
executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe"
```

### 第四步：启动录制工具

```bash
python web_optimized.py
```

### 第五步：按提示操作

1. 输入要测试的网址（默认：https://www.ctrip.com/）
2. 设置初始需求编号（如：R001）
3. 开始录制操作（输入元素文本或命令）
4. 输入 `quit` 完成录制并生成测试脚本

---

## 📚 详细使用指南

### 1️⃣ 录制测试操作

#### 点击元素

直接输入元素的可见文本：

```
【当前需求: R001】 请输入操作: 机票
```

工具会自动查找并点击包含"机票"文本的元素。

#### 输入文本

点击输入框后，工具会自动检测并提示输入内容：

```
【当前需求: R001】 请输入操作: 出发城市
检测到输入框，点击并等待输入...
请输入内容: 北京
```

输入框会被**自动清空**，然后输入新内容。

#### 鼠标悬浮

```
【当前需求: R001】 请输入操作: 悬浮

请选择定位方式:
  1. 使用CSS选择器
  2. 使用文本
请选择 (1 或 2): 2

请输入要悬浮的元素文本: 用户中心
```

#### 自定义CSS选择器

对于无法通过文本定位的元素：

```
【当前需求: R001】 请输入操作: 添加

请输入元素名称: 确认按钮
请输入CSS选择器: #confirm-btn
```

### 2️⃣ 需求管理

#### 设置需求编号

启动时设置初始需求：

```
请输入需求编号 (格式：R001, R002等): R001
✓ 当前需求编号已设置为: R001
```

#### 切换需求

```
【当前需求: R001】 请输入操作: req

请输入新的需求编号: R002
✓ 当前需求编号已设置为: R002
```

#### 查看所有步骤

```
【当前需求: R002】 请输入操作: l

================================================================================
已添加的测试步骤 (共 8 步, 2 个需求)
================================================================================

【需求 R001】 - 5 个步骤
--------------------------------------------------------------------------------

  1. CtripFlight_R001_001
     操作: 机票
     类型: click
     定位: By.CSS_SELECTOR = "#flight-tab"

  2. CtripFlight_R001_002
     操作: 出发城市
     类型: input
     定位: By.CSS_SELECTOR = "#fromCity"
     输入: 北京
...
```

#### 删除错误步骤

```
【当前需求: R001】 请输入操作: r

请选择要删除的步骤 (1-8, 或输入 'c' 取消): 3

✓ 已删除步骤: CtripFlight_R001_003 - 搜索
✓ 已重新编号，当前共 7 个步骤
```

### 3️⃣ 命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| **元素文本** | 查找并点击元素 | `机票`、`搜索`、`登录` |
| **输入框** | 查找输入框 | `输入框`、`搜索框` |
| **悬浮** / **hover** | 鼠标悬浮到元素 | `悬浮` |
| **添加** / **custom** | 自定义CSS选择器 | `添加` |
| **窗口** / **windows** | 切换浏览器窗口 | `窗口` |
| **req** / **需求** | 切换需求编号 | `req` |
| **l** | 列出所有步骤 | `l` |
| **r** | 删除指定步骤 | `r` |
| **quit** / **exit** | 退出并生成脚本 | `quit` |

### 4️⃣ 完成录制

输入退出命令：

```
【当前需求: R002】 请输入操作: quit

程序结束
================================================================================
✓ 测试脚本生成完成: TestCtripFlight.py
================================================================================
  总步骤数: 8
  需求数量: 2
  生成函数:
    - test_CtripFlight_R001() [5 个步骤]
    - test_CtripFlight_R002() [3 个步骤]

运行测试命令:
  pytest TestCtripFlight.py -v
```

---

## 🧪 运行测试脚本

### 方式1：直接运行Python脚本

```bash
python TestCtripFlight.py
```

### 方式2：使用Pytest命令

```bash
# 运行所有测试
pytest TestCtripFlight.py -v -s

# 运行特定需求的测试
pytest TestCtripFlight.py::TestCtripFlight::test_CtripFlight_R001 -v

# 生成HTML测试报告
pytest TestCtripFlight.py -v --html=report.html
```

### 浏览器关闭说明

- **scope="class"**（默认）：所有测试执行完后关闭浏览器，速度快
- **scope="function"**：每个测试执行完就关闭，速度慢但更独立

修改 `TestCtripFlight.py` 中的 `@pytest.fixture(scope="class")` 可切换模式。

---

## 📁 项目结构

```
项目目录/
├── web_optimized.py              # 主程序 - 自动化录制工具
├── TestCtripFlight.py            # 生成的测试脚本（自动生成）
├── clicked_elements.log          # 元素操作日志（自动生成）
├── screenshots/                  # 截图文件夹（自动创建）
│   ├── 时间戳_CtripFlight_R001_001.png
│   ├── 时间戳_CtripFlight_R001_002.png
│   └── ...
├── 携程机票查询测试用例.xlsx    # 测试用例文档
├── 测试用例模版.xlsx            # 测试用例模板
├── 操作手册.md                   # 详细操作手册
├── README.md                     # 本文件
└── requirements.txt              # Python依赖包列表
```

### 文件说明

| 文件 | 说明 | 是否需要提交 |
|------|------|-------------|
| `web_optimized.py` | 录制工具主程序 | ✅ 是 |
| `TestCtripFlight.py` | 生成的测试脚本 | ✅ 是 |
| `screenshots/*.png` | 测试截图（压缩为ZIP） | ✅ 是 |
| `携程机票查询测试用例.xlsx` | 测试用例文档 | ✅ 是 |
| `clicked_elements.log` | 操作日志 | ❌ 否 |
| `__pycache__/` | Python缓存 | ❌ 否 |

---

## 📝 测试用例规范

### 测试用例编号格式

```
CtripFlight_R001_001
    │         │    │
    │         │    └─ 步骤编号（001-999）
    │         └────── 需求编号（R001-R999）
    └──────────────── 软件名称（固定：CtripFlight）
```

### 需求编号格式

- ✅ 正确：`R001`, `R002`, `R010`, `R100`
- ❌ 错误：`r001`（小写）, `R01`（两位）, `ROO1`（字母O）

### 截图文件名格式

```
13061316084_CtripFlight_R001_001.png
     │              │
     │              └─ 测试用例编号
     └──────────────── 时间戳（HHMMSSddfffff）
```

---

## 🎯 核心功能详解

### 1. 智能元素定位

工具会为每个元素生成**多种定位器**，并自动选择最优方案：

**定位器优先级**：
1. 🥇 **LINK_TEXT** - 链接文本（最稳定）
2. 🥈 **XPATH精确文本** - `//button[text()='搜索']`
3. 🥉 **ID** - 元素ID属性
4. 🏅 **NAME** - 元素name属性
5. 🎖️ **CSS_SELECTOR** - CSS选择器

**特点**：
- ✅ 使用元素的**实际完整文本**，而非用户输入的搜索文本
- ✅ 自动处理单引号、双引号等特殊字符
- ✅ 避免动态ID和class（如包含随机字符串）
- ✅ 生成3-5个备选定位器作为容错

### 2. 强力清空输入框

针对携程等网站的自定义输入控件，使用**四重清空机制**：

```python
# 1. 三次Ctrl+A + Backspace（物理按键，最可靠）
for _ in range(3):
    element.send_keys(Keys.CONTROL + 'a')
    element.send_keys(Keys.BACKSPACE)

# 2. JavaScript清空并触发事件（绕过框架限制）
driver.execute_script("""
    arguments[0].value = '';
    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
""", element)

# 3. 标准clear()方法（兼容性）
element.clear()

# 4. 再次全选删除（确保清空）
element.send_keys(Keys.CONTROL + 'a')
element.send_keys(Keys.DELETE)
```

### 3. 容错机制

当主定位器失败时，自动尝试备选定位器：

```
[定位器] 主定位: By.CSS_SELECTOR = #oldSelector
[定位失败] 主定位器失败: By.CSS_SELECTOR
[定位尝试] 开始尝试 3 个备选定位器...
  [1/3] 尝试: By.XPATH = //button[text()='搜索']
  ✓ 备选定位器 [1] 成功！
```

---

## ⚙️ 高级配置

### 修改超时时间

编辑 `web_optimized.py` 中的 `Config` 类：

```python
@dataclass
class Config:
    DEFAULT_TIMEOUT: int = 10        # 默认等待时间（秒）
    PAGE_LOAD_TIMEOUT: int = 30      # 页面加载超时
    HIGHLIGHT_DURATION: float = 1.0  # 元素高亮时长
```

### 修改ChromeDriver路径

提交测试时，记得将路径改回官方路径：

```python
# 开发时使用
executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe"

# 提交时改为
executable_path="C:\\Users\\86153\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe"
```

### 修改CSS路径生成模式

```python
USE_SIMPLE_CSS_PATH: bool = True  # True=简洁模式（推荐），False=包含所有class
```

---

## 🐛 常见问题解决

### Q1: 找不到ChromeDriver

**问题**：`selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH`

**解决**：
1. 下载与Chrome版本匹配的ChromeDriver
2. 将ChromeDriver路径配置到脚本中
3. 或将ChromeDriver添加到系统PATH环境变量

### Q2: 元素定位失败

**问题**：无法找到页面元素

**解决**：
1. 确保页面已完全加载
2. 使用 `添加` 命令手动指定CSS选择器
3. 检查元素是否在iframe中
4. 增加等待时间

### Q3: 输入框没有清空

**问题**：输入框中仍保留旧值

**解决**：
- 工具已使用四重清空机制，如仍未清空请报告具体网站
- 可能需要针对特定网站额外优化

### Q4: 测试脚本执行失败

**问题**：生成的脚本运行时报错

**解决**：
1. 检查ChromeDriver路径是否正确
2. 确保网络连接正常
3. 检查页面结构是否已变化
4. 查看定位器是否仍然有效

### Q5: 浏览器没有关闭

**问题**：测试完成后浏览器仍然打开

**解决**：
- 工具已添加 `try-finally` 确保关闭
- 如果使用Ctrl+C强制中断，可能无法正常关闭
- 可以手动关闭浏览器或重新运行脚本

---

## 📊 测试用例管理

### Excel测试用例文档

项目包含完整的测试用例Excel文档：`携程机票查询测试用例.xlsx`

**包含内容**：
- 26个测试用例，涵盖5个需求（R001-R005）
- 测试用例编号、模块名称、需求编号
- 详细的前置条件、执行步骤、预期结果
- 截图文件名对应关系

**列结构**：
| 列 | 内容 | 说明 |
|----|------|------|
| A | 测试用例编号 | CtripFlight_R001_001 |
| B | 模块名称 | 机票查询 |
| C | 需求编号 | R001 |
| D | 用例说明 | 验证点击机票Tab... |
| E | 前置条件 | 1. 浏览器已打开... |
| F | 执行步骤 | 1. 定位机票Tab... |
| G | 输入数据 | 出发城市：北京 |
| H | 预期结果 | 1. 页面成功跳转... |
| I | 实际结果 | 通过 |
| J | 截图文件名 | CtripFlight_R001_001.png |

---

## 🎓 最佳实践

### 1. 录制测试用例时

- ✅ 等待页面完全加载后再操作
- ✅ 使用清晰、唯一的元素文本进行定位
- ✅ 按需求逻辑分组，合理使用需求编号
- ✅ 及时删除错误的录制步骤
- ✅ 定期使用 `l` 命令查看已录制的步骤

### 2. 生成测试脚本后

- ✅ 先测试运行一次，确保所有步骤正常
- ✅ 删除调试过程中产生的多余截图
- ✅ 确保每个测试用例只有一张截图
- ✅ 检查ChromeDriver路径是否正确
- ✅ 提交前将路径改回官方路径

### 3. 提交前检查

- ✅ 测试脚本编码为UTF-8
- ✅ 测试用例编号格式正确
- ✅ 需求编号大写（R001不是r001）
- ✅ 截图文件名与用例编号对应
- ✅ 所有截图都在screenshots文件夹
- ✅ 使用ZIP格式打包（不是RAR）

---

## 🔄 更新日志

### v2.0 - 当前版本

**新增功能**：
- ✅ 按需求编号分组管理测试步骤
- ✅ 强力清空输入框（四重机制）
- ✅ 使用元素实际文本生成XPath
- ✅ 详细的定位器信息打印
- ✅ 确保浏览器退出的try-finally机制
- ✅ 智能单引号转义处理

**改进**：
- ✅ 优化备选定位器生成算法
- ✅ 改进容错机制和错误提示
- ✅ 完善测试用例编号规范
- ✅ 生成符合比赛要求的脚本格式

### v1.0 - 初始版本

- ✅ 基础元素定位和操作录制
- ✅ 参数化测试脚本生成
- ✅ 窗口管理和截图功能

---

## 📞 技术支持

### 相关文档

- **操作手册.md** - 详细的工具使用指南（415行）
- **测试用例说明.md** - 测试用例编写规范
- **携程机票查询需求文档.docx** - 详细需求说明
- **携程网机票查询功能说明手册.docx** - 功能说明

### 联系方式

- 项目仓库：[GitHub链接]
- 问题反馈：[Issues链接]
- 邮箱：[联系邮箱]

---

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和测试人员。

---

## 📌 快速参考卡

### 常用命令速查

```bash
# 启动录制工具
python web_optimized.py

# 运行测试脚本
python TestCtripFlight.py
pytest TestCtripFlight.py -v -s

# 运行特定需求测试
pytest TestCtripFlight.py::TestCtripFlight::test_CtripFlight_R001 -v

# 生成HTML报告
pytest TestCtripFlight.py --html=report.html
```

### 录制命令速查

| 输入 | 功能 |
|------|------|
| `机票` | 点击"机票"元素 |
| `输入框` | 查找输入框 |
| `悬浮` | 鼠标悬浮 |
| `添加` | 自定义CSS |
| `窗口` | 切换窗口 |
| `req` | 切换需求 |
| `l` | 查看步骤 |
| `r` | 删除步骤 |
| `quit` | 退出生成 |

---

**版本**: v2.0  
**更新日期**: 2025-10-26  
**适用于**: 软件测试大赛自动化测试项目

---

<div align="center">
  
**🎉 祝测试愉快！**

Made with ❤️ for Software Testing

</div>


