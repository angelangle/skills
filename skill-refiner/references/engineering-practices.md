# 工程实践指南

## 1. 开发流程

### 1.1 敏捷迭代流程

```
需求收集
    ↓
快速设计（1-2小时）
    ↓
原型实现（半天-1天）
    ↓
即时验证
    ├─ 通过 → 完善文档
    └─ 失败 → 快速调整
              ↓
         回到设计
```

### 1.2 质量门禁

**代码/文档提交前检查**：
- [ ] 功能正确性验证
- [ ] 边界情况处理
- [ ] 文档同步更新
- [ ] 风格一致性检查
- [ ] 可维护性评估

---

## 2. 代码/文档规范

### 2.1 文件组织

```
skill-name/
├── SKILL.md              # 核心文档（必须）
├── README.md             # 项目说明（可选）
├── references/           # 参考资料
│   ├── theory.md         # 理论基础
│   ├── practices.md      # 实践指南
│   └── case-studies/     # 案例分析
├── scripts/              # 工具脚本
│   ├── tool1.py
│   └── tool2.sh
├── assets/               # 静态资源
│   ├── images/
│   └── templates/
└── evals/                # 评估测试
    └── evals.json
```

### 2.2 命名规范

| 类型 | 规范 | 示例 |
|-----|------|------|
| 文件名 | 小写，连字符分隔 | `skill-doctor.py` |
| 变量名 | snake_case | `skill_path` |
| 常量名 | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| 类名 | PascalCase | `SkillDoctor` |
| 函数名 | snake_case | `diagnose_skill` |

### 2.3 文档规范

**SKILL.md 结构**：
```yaml
---
name: skill-name
description: |
  多行描述，包含关键词和触发场景
---

# 标题

## 第一部分：快速开始

## 第二部分：核心能力

## 第三部分：详细指南

## 第四部分：参考

## 附录
```

---

## 3. 版本管理

### 3.1 语义化版本

```
版本格式：主版本号.次版本号.修订号（MAJOR.MINOR.PATCH）

MAJOR：不兼容的修改
MINOR：向下兼容的功能新增
PATCH：向下兼容的问题修正

示例：
v1.0.0 - 初始稳定版本
v1.1.0 - 新增功能
v1.1.1 - Bug修复
v2.0.0 - 重大重构
```

### 3.2 变更日志

```markdown
# Changelog

## [Unreleased]
### Added
- 新功能A
- 新功能B

### Changed
- 功能C的改进

### Fixed
- 问题D的修复

## [1.1.0] - 2024-01-15
### Added
- 新增诊断工具

### Fixed
- 修复触发率计算bug

## [1.0.0] - 2024-01-01
- 初始版本
```

---

## 4. 测试策略

### 4.1 测试金字塔

```
    /\
   /  \
  / E2E\          # 端到端测试（少量）
 /______\
/        \
/ 集成测试 \       # 集成测试（中等）
/__________\
/            \
/   单元测试   \    # 单元测试（大量）
/______________\
```

### 4.2 Skill特定测试

**触发率测试**：
```python
def test_trigger_rate():
    test_cases = [
        ("应该触发的查询", True),
        ("不应该触发的查询", False),
    ]

    for query, should_trigger in test_cases:
        result = check_trigger(skill, query)
        assert result == should_trigger
```

**内容准确性测试**：
```python
def test_content_accuracy():
    # 验证关键信息正确
    assert "关键词" in skill.description
    assert len(skill.references) >= 3
```

### 4.3 自动化测试

**持续集成检查**：
- 文档结构验证
- 链接有效性检查
- 代码语法检查
- 风格一致性检查

---

## 5. 性能优化

### 5.1 加载性能

**SKILL.md 优化**：
- 控制文件大小（< 500行）
- 使用渐进式披露
- 延迟加载参考资料

**结构优化**：
```
SKILL.md (核心内容，常驻内存)
    ↓ 按需加载
references/*.md (扩展内容)
    ↓ 按需加载
assets/* (资源文件)
```

### 5.2 执行性能

**脚本优化**：
- 避免重复计算
- 缓存中间结果
- 异步并行处理

**示例**：
```python
# 使用缓存
@functools.lru_cache(maxsize=128)
def expensive_operation(key):
    return compute(key)

# 并行处理
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(process, items)
```

---

## 6. 可维护性实践

### 6.1 模块化设计

**高内聚低耦合**：
- 每个模块有明确职责
- 模块间接口清晰
- 减少相互依赖

**示例结构**：
```python
# 分析模块
class Analyzer:
    def analyze(self): ...

# 生成模块
class Generator:
    def generate(self): ...

# 协调模块
class Coordinator:
    def __init__(self):
        self.analyzer = Analyzer()
        self.generator = Generator()

    def run(self):
        data = self.analyzer.analyze()
        return self.generator.generate(data)
```

### 6.2 文档化

**代码文档**：
```python
def complex_function(param1: str, param2: int) -> dict:
    """
    函数简短描述。

    详细说明函数的功能、使用场景和注意事项。

    Args:
        param1: 参数1的说明
        param2: 参数2的说明

    Returns:
        返回值的说明

    Raises:
        ValueError: 什么情况下抛出

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
    """
    pass
```

**架构决策记录（ADR）**：
```markdown
# ADR 001: 选择XXX架构

## 状态
已接受

## 背景
问题描述...

## 决策
采用XXX方案

## 理由
- 理由1
- 理由2

## 后果
正面：...
负面：...
```

### 6.3 重构策略

**何时重构**：
- 代码/文档重复
- 逻辑难以理解
- 添加新功能困难
- 性能下降

**重构步骤**：
1. 确保有测试覆盖
2. 小步前进
3. 频繁验证
4. 保留历史记录

---

## 7. 工具链

### 7.1 推荐工具

**编辑**：
- VSCode with extensions
- Vim/Neovim

**版本控制**：
- Git
- GitHub/GitLab

**文档**：
- Markdown
- Draw.io（图表）
- PlantUML（流程图）

**测试**：
- pytest（Python）
- shellcheck（Shell）

**质量**：
- pylint/mypy（Python静态检查）
- markdownlint（Markdown检查）

### 7.2 自动化脚本

```bash
#!/bin/bash
# 质量检查脚本

echo "运行代码检查..."
pylint scripts/*.py

echo "运行文档检查..."
markdownlint references/*.md

echo "运行链接检查..."
# 检查死链接

echo "运行测试..."
pytest tests/
```

---

## 8. 协作规范

### 8.1 代码审查

**审查清单**：
- [ ] 功能正确性
- [ ] 边界情况处理
- [ ] 文档完整性
- [ ] 风格一致性
- [ ] 性能影响
- [ ] 安全性

**审查原则**：
- 对事不对人
- 解释"为什么"
- 提出具体建议
- 认可好的实践

### 8.2 沟通规范

**提交信息**：
```
<type>(<scope>): <subject>

<body>

<footer>

示例：
feat(desc): 添加description优化功能

实现自动关键词扩展和触发率分析。

Closes #123
```

**类型定义**：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 杂项

---

## 9. 故障排查

### 9.1 调试策略

**分而治之**：
1. 定位问题范围
2. 隔离最小复现
3. 逐步排查

**日志记录**：
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def function():
    logger.debug("进入函数")
    # ...
    logger.info("关键步骤完成")
    # ...
    logger.error("发生错误: %s", error)
```

### 9.2 常见问题

| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| 触发率低 | 关键词不足 | 扩展同义词 |
| 误触发高 | 边界模糊 | 明确排除条件 |
| 执行缓慢 | 算法复杂度高 | 优化或缓存 |
| 内存占用大 | 数据未释放 | 及时清理 |
| 文档不同步 | 忘记更新 | 建立检查清单 |

---

*工程的本质是在约束条件下找到最优解。*
