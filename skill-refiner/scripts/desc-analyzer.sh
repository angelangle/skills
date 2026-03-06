#!/bin/bash
#
# Skill Description Analyzer
# 分析 skill description 质量
#

set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills"

show_help() {
    cat << 'EOF'
Skill Description Analyzer

Usage: desc-analyzer.sh <skill-name>

Analyzes description quality and provides optimization suggestions.

Examples:
    desc-analyzer.sh os-net-dev
    desc-analyzer.sh os-term-visual-dev

EOF
}

# 分析 description
analyze_description() {
    local skill_file="$1"

    echo "=== Description Analysis ==="
    echo ""

    # 提取 description
    local desc=$(sed -n '/^description:/,/^---$/p' "$skill_file" | sed '1d;$d' | sed 's/^  //')

    # 统计指标
    local char_count=$(echo "$desc" | wc -c)
    local word_count=$(echo "$desc" | wc -w)
    local line_count=$(echo "$desc" | wc -l)

    echo "📊 Basic Statistics"
    echo "  Characters: $char_count"
    echo "  Words: $word_count"
    echo "  Lines: $line_count"
    echo ""

    # 检查关键词
    echo "🔍 Keyword Check"
    local keywords=("when" "use" "for" "skill" "trigger")
    for kw in "${keywords[@]}"; do
        if echo "$desc" | grep -qi "$kw"; then
            echo "  ✓ Contains '$kw'"
        else
            echo "  ✗ Missing '$kw'"
        fi
    done
    echo ""

    # 检查场景示例
    echo "📝 Scenario Examples Check"
    if echo "$desc" | grep -qE '(scenario|scene|example|case|场景|示例)'; then
        echo "  ✓ Has scenario examples"
    else
        echo "  ✗ No scenario examples found"
    fi
    echo ""

    # 检查排除条件
    echo "🚫 Exclusion Check"
    if echo "$desc" | grep -qiE '(not|doesn|exclude|不涉及|不包括)'; then
        echo "  ✓ Has exclusion criteria"
    else
        echo "  ⚠ No exclusion criteria (recommended to add)"
    fi
    echo ""

    # 长度建议
    echo "💡 Suggestions"
    if [[ $char_count -lt 200 ]]; then
        echo "  ⚠ Description is too short (<200 chars). Consider adding more details."
    elif [[ $char_count -gt 1000 ]]; then
        echo "  ⚠ Description is very long (>1000 chars). Consider being more concise."
    else
        echo "  ✓ Description length is good"
    fi
}

# 生成优化建议
generate_suggestions() {
    local skill_file="$1"

    echo ""
    echo "=== Optimization Suggestions ==="
    echo ""

    cat << 'EOF'
1. KEYWORDS
   - Add synonyms for main concepts
   - Include common abbreviations
   - Consider different phrasings

2. SCENARIOS
   - Add 3-5 specific use cases
   - Include edge cases
   - Mention typical user queries

3. EXCLUSIONS
   - Clarify what the skill does NOT do
   - Mention adjacent domains
   - Prevent false triggers

4. STRUCTURE
   - Put key terms first
   - Use bullet points for clarity
   - Keep one main idea per sentence

EOF
}

main() {
    local skill_name="${1:-}"

    if [[ -z "$skill_name" ]] || [[ "$skill_name" == "--help" ]]; then
        show_help
        exit 0
    fi

    local skill_file="${SKILL_DIR}/${skill_name}/SKILL.md"
    if [[ ! -f "$skill_file" ]]; then
        echo "Error: Skill file not found: $skill_file"
        exit 1
    fi

    analyze_description "$skill_file"
    generate_suggestions "$skill_file"
}

main "$@"
