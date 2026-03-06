#!/bin/bash
#
# Quick Skill Update Script
# 快速更新 skill 的辅助工具
#

set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills"

show_help() {
    cat << 'EOF'
Quick Skill Updater

Usage: quick-update.sh <skill-name> <update-type> [options]

Update Types:
    fix         修复 bug 或问题
    add         添加功能
    update      更新内容
    adjust      调整行为

Examples:
    quick-update.sh os-net-dev fix "修复路由表查询错误"
    quick-update.sh os-fs-dev add "添加 Btrfs 支持"
    quick-update.sh os-debug-dev update "更新 ftrace 命令"

EOF
}

# 创建更新日志
create_update_log() {
    local skill_name="$1"
    local update_type="$2"
    local description="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    local log_file="${SKILL_DIR}/${skill_name}/UPDATE_LOG.md"

    if [[ ! -f "$log_file" ]]; then
        echo "# Update Log for ${skill_name}" > "$log_file"
        echo "" >> "$log_file"
    fi

    cat >> "$log_file" << EOF

## ${timestamp} [${update_type}]

${description}

### Files Modified
- [ ] SKILL.md
- [ ] scripts/
- [ ] references/
- [ ] assets/

### Checklist
- [ ] 更新已完成
- [ ] 功能已验证
- [ ] 文档已同步
EOF

    echo "Created update log: $log_file"
}

# 备份 skill
backup_skill() {
    local skill_name="$1"
    local backup_dir="${SKILL_DIR}/${skill_name}/.backup/$(date '+%Y%m%d_%H%M%S')"

    mkdir -p "$backup_dir"
    cp -r "${SKILL_DIR}/${skill_name}"/* "$backup_dir/" 2>/dev/null || true

    echo "Backup created: $backup_dir"
}

# 主函数
main() {
    local skill_name="${1:-}"
    local update_type="${2:-}"
    local description="${3:-}"

    if [[ -z "$skill_name" ]] || [[ "$skill_name" == "--help" ]]; then
        show_help
        exit 0
    fi

    local skill_path="${SKILL_DIR}/${skill_name}"
    if [[ ! -d "$skill_path" ]]; then
        echo "Error: Skill '${skill_name}' not found"
        exit 1
    fi

    echo "=== Skill Updater ==="
    echo "Target: ${skill_name}"
    echo "Type: ${update_type}"
    echo "Description: ${description}"
    echo ""

    # 创建备份
    backup_skill "$skill_name"

    # 创建更新日志
    create_update_log "$skill_name" "$update_type" "$description"

    echo ""
    echo "Ready to update. Edit files in: ${skill_path}"
}

main "$@"
