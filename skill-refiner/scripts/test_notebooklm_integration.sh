#!/bin/bash
# NotebookLM 集成测试脚本
# 演示 skill-refiner 如何与 notebooklm-skill 集成

set -e

SKILL_REFINER_DIR="$HOME/.claude/skills/skill-refiner"
NOTEBOOKLM_DIR="$HOME/.claude/skills/notebooklm-skill"
TARGET_SKILL="${1:-skill-refiner}"

echo "=========================================="
echo "NotebookLM 集成测试"
echo "=========================================="
echo ""
echo "目标 Skill: $TARGET_SKILL"
echo ""

# Step 1: 检查认证
echo "[Step 1] 检查 NotebookLM 认证状态..."
cd "$NOTEBOOKLM_DIR"
python scripts/run.py auth_manager.py status
echo ""

# Step 2: 如果没有认证，提示用户
echo "[Step 2] 认证检查..."
if [ ! -f data/auth_info.json ]; then
    echo "⚠️  未认证！需要执行以下命令进行认证："
    echo "    python scripts/run.py auth_manager.py setup"
    echo ""
    echo "注意：这会打开浏览器窗口，需要手动登录 Google 账号"
    echo ""
    read -p "是否现在进行认证？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python scripts/run.py auth_manager.py setup
    else
        echo "跳过认证，演示模拟流程..."
    fi
fi

echo ""
echo "=========================================="
echo "集成测试场景"
echo "=========================================="
echo ""

# 场景 1: Smart Add - 分析 skill 内容
echo "[场景 1] Smart Add - 分析 skill 文档内容"
echo "命令:"
echo "  python scripts/run.py ask_question.py \\"
echo "    --question \"分析这个skill的主要能力和结构\" \\"
echo "    --notebook-url \"file://$HOME/.claude/skills/$TARGET_SKILL/SKILL.md\""
echo ""

# 场景 2: 添加到 NotebookLM 库
echo "[场景 2] 添加到 NotebookLM 库"
echo "命令:"
echo "  python scripts/run.py notebook_manager.py add \\"
echo "    --url \"file://$HOME/.claude/skills/$TARGET_SKILL/SKILL.md\" \\"
echo "    --name \"$TARGET_SKILL\" \\"
echo "    --description \"Skill refiner meta-capability skill\" \\"
echo "    --topics \"skill-evolution,meta-skill,optimization\""
echo ""

# 场景 3: 深度分析
echo "[场景 3] 深度分析 skill 结构"
echo "问题示例:"
echo "  1. 这个skill的frontmatter描述是否清晰完整？"
echo "  2. 触发关键词覆盖度如何？有哪些遗漏？"
echo "  3. 与os-scheduler-dev相比，结构上有何差异？"
echo "  4. 这个skill的科研深度和工程实用性如何平衡？"
echo "  5. 有哪些可以改进的地方？"
echo ""

# 场景 4: 对比分析
echo "[场景 4] 对比多个skill"
echo "命令:"
echo "  python scripts/run.py ask_question.py \\"
echo "    --question \"对比skill-refiner和skill-creator的能力差异\" \\"
echo "    --notebook-id comparison-notebook"
echo ""

echo "=========================================="
echo "预期输出示例"
echo "=========================================="
echo ""
cat << 'EXPECTED_OUTPUT'
基于文档的分析结果：

1. **Frontmatter 评估**
   - ✅ 描述清晰，涵盖了8大核心元能力
   - ✅ 触发关键词丰富（skill进化, 自我提升等）
   - ⚠️  可以添加更多边缘场景关键词

2. **结构完整性**
   - ✅ 7个主要章节覆盖全面
   - ✅ 附录提供了快速参考
   - ⚠️  缺少具体的性能基准数据

3. **可改进点**
   - 添加更多实际使用案例
   - 补充自动化测试脚本
   - 增加与其他meta-skill的对比表格

来源引用：
- SKILL.md 第12行：核心元能力定义
- SKILL.md 第374-515行：外部工具集成
- SKILL.md 第1222-1276行：使用指南
EXPECTED_OUTPUT

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
