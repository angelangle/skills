#!/bin/bash
#
# Reference Expander - 参考资料扩充工具
# 帮助快速扩充 skill 的参考资料
#

set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills"

show_help() {
    cat << 'EOF'
Reference Expander - 参考资料扩充工具

Usage: expand-references.sh <skill-name> <expansion-type>

Expansion Types:
    docs        添加官方文档模板
    examples    添加示例集合模板
    cheatsheet  添加速查表模板
    faq         添加常见问题模板
    all         添加所有类型

Examples:
    expand-references.sh os-net-dev docs
    expand-references.sh os-debug-dev examples
    expand-references.sh my-skill all

EOF
}

# 创建官方文档模板
create_docs_template() {
    local skill_path="$1"
    local output_file="${skill_path}/references/official-docs.md"

    cat > "$output_file" << 'EOF'
# 官方文档参考

## 核心规范

### 标准文档
- [标准名称](URL) - 标准描述
- [RFC XXXX](URL) - 协议规范

### 官方手册
- [官方文档名称](URL) - 文档描述
- [API Reference](URL) - API 详细说明

## 实现参考

### 开源实现
- [项目名](URL) - 实现特点说明
- [项目名](URL) - 实现特点说明

### 最佳实践
- [指南名称](URL) - 指南描述
- [设计模式](URL) - 模式描述
EOF

    echo "Created: $output_file"
}

# 创建示例模板
create_examples_template() {
    local skill_path="$1"
    local output_file="${skill_path}/references/examples.md"

    cat > "$output_file" << 'EOF'
# 示例集合

## 基础示例

### 示例 1: 基础用法
```
输入: XXX
输出: XXX
说明: 最基本的用法示例
```

### 示例 2: 常见场景
```
输入: XXX
输出: XXX
说明: 最常见的使用场景
```

## 进阶示例

### 示例 3: 复杂场景
```
输入: XXX
输出: XXX
说明: 多步骤复杂场景
```

### 示例 4: 组合用法
```
输入: XXX
输出: XXX
说明: 多个功能的组合使用
```

## 边界示例

### 示例 5: 异常处理
```
输入: XXX（异常情况）
处理: XXX
说明: 如何正确处理异常
```

### 示例 6: 极限情况
```
输入: XXX（极限输入）
输出: XXX
说明: 极限情况下的表现
```
EOF

    echo "Created: $output_file"
}

# 创建速查表模板
create_cheatsheet_template() {
    local skill_path="$1"
    local output_file="${skill_path}/references/cheatsheet.md"

    cat > "$output_file" << 'EOF'
# 速查表 (Cheatsheet)

## 快速命令

| 命令 | 说明 | 示例 |
|------|------|------|
| cmd1 | 说明1 | `示例` |
| cmd2 | 说明2 | `示例` |
| cmd3 | 说明3 | `示例` |

## 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| -a   | 参数A说明 | false |
| -b   | 参数B说明 | true |
| -c   | 参数C说明 | none |

## 配置选项

```yaml
key1: value1    # 说明
key2: value2    # 说明
key3: value3    # 说明
```

## 快速诊断

| 症状 | 可能原因 | 解决方案 |
|------|----------|----------|
| 问题1 | 原因1 | 解决方案1 |
| 问题2 | 原因2 | 解决方案2 |
EOF

    echo "Created: $output_file"
}

# 创建 FAQ 模板
create_faq_template() {
    local skill_path="$1"
    local output_file="${skill_path}/references/faq.md"

    cat > "$output_file" << 'EOF'
# 常见问题 (FAQ)

## Q1: 问题描述？

**场景**: 什么情况下会遇到这个问题

**原因**: 为什么会这样

**解决方案**:
```
具体解决步骤
```

---

## Q2: 问题描述？

**场景**: XXX

**原因**: XXX

**解决方案**: XXX

---

## Q3: 如何...？

**回答**: 详细说明

**示例**:
```
代码/命令示例
```
EOF

    echo "Created: $output_file"
}

# 主函数
main() {
    local skill_name="${1:-}"
    local exp_type="${2:-}"

    if [[ -z "$skill_name" ]] || [[ "$skill_name" == "--help" ]]; then
        show_help
        exit 0
    fi

    local skill_path="${SKILL_DIR}/${skill_name}"
    if [[ ! -d "$skill_path" ]]; then
        echo "Error: Skill '${skill_name}' not found at ${skill_path}"
        exit 1
    fi

    # 确保 references 目录存在
    mkdir -p "${skill_path}/references"

    case "$exp_type" in
        docs)
            create_docs_template "$skill_path"
            ;;
        examples)
            create_examples_template "$skill_path"
            ;;
        cheatsheet)
            create_cheatsheet_template "$skill_path"
            ;;
        faq)
            create_faq_template "$skill_path"
            ;;
        all)
            create_docs_template "$skill_path"
            create_examples_template "$skill_path"
            create_cheatsheet_template "$skill_path"
            create_faq_template "$skill_path"
            echo ""
            echo "All reference templates created!"
            ;;
        *)
            echo "Error: Unknown expansion type: $exp_type"
            echo "Valid types: docs, examples, cheatsheet, faq, all"
            exit 1
            ;;
    esac

    echo ""
    echo "Next steps:"
    echo "1. Edit the created files with actual content"
    echo "2. Update SKILL.md to reference new files"
    echo "3. Test the skill with new references"
}

main "$@"
