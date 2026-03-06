#!/usr/bin/env python3
"""
desc-optimizer.py - Skill Description优化器

自动分析并优化skill的description，提升触发率。
支持关键词扩展、场景细化和A/B测试。

Usage:
    python3 desc-optimizer.py <skill-path> [--target-precision=0.92]
"""

import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class DescriptionAnalysis:
    """Description分析结果"""
    original: str
    length: int
    keywords: Set[str]
    scenarios: List[str]
    has_trigger_words: bool
    has_negative_examples: bool
    score: float
    issues: List[str]
    suggestions: List[str]


class DescriptionOptimizer:
    """Description优化器"""

    # 高频触发词库
    TRIGGER_PATTERNS = {
        'action': ['分析', '优化', '设计', '实现', '诊断', '修复', '增强', '提升', '创建', '管理'],
        'domain': ['系统', '代码', '性能', '架构', '安全', '网络', '存储', '驱动', '内核'],
        'method': ['自动化', '最佳实践', '标准化', '工具链', '框架', '方法论'],
        'urgency': ['必须', '务必', '立即', '紧急', '重要']
    }

    # 建议的同义词扩展
    KEYWORD_EXPANSION = {
        '优化': ['调优', '改进', '提升', '加速', '性能优化', '效率提升'],
        '分析': ['诊断', '评估', '检查', '审查', '解析', '研究'],
        '设计': ['架构', '规划', '方案', '建模', '原型'],
        '实现': ['开发', '编写', '构建', '搭建', '落地'],
        '修复': ['解决', '调试', '排错', '纠正', '补丁'],
        '管理': ['治理', '管控', '调度', '编排', '协调']
    }

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.skill_md = self.skill_path / 'SKILL.md'

    def analyze(self) -> DescriptionAnalysis:
        """分析当前description"""
        print(f"🔍 分析Skill: {self.skill_name}")
        print("-" * 50)

        if not self.skill_md.exists():
            return DescriptionAnalysis(
                original="", length=0, keywords=set(),
                scenarios=[], has_trigger_words=False,
                has_negative_examples=False, score=0,
                issues=["缺少SKILL.md文件"], suggestions=["创建SKILL.md"]
            )

        content = self.skill_md.read_text()

        # 提取description
        desc = self._extract_description(content)
        if not desc:
            return DescriptionAnalysis(
                original="", length=0, keywords=set(),
                scenarios=[], has_trigger_words=False,
                has_negative_examples=False, score=0,
                issues=["未找到description字段"], suggestions=["添加YAML frontmatter description"]
            )

        # 分析各项指标
        length = len(desc)
        keywords = self._extract_keywords(desc)
        scenarios = self._extract_scenarios(desc)
        has_trigger = self._check_trigger_words(desc)
        has_negative = self._check_negative_examples(desc)

        # 计算分数
        score = self._calculate_score(length, keywords, scenarios, has_trigger, has_negative)

        # 识别问题
        issues = self._identify_issues(desc, length, keywords, scenarios, has_trigger, has_negative)

        # 生成建议
        suggestions = self._generate_suggestions(desc, keywords, scenarios, has_trigger, has_negative)

        return DescriptionAnalysis(
            original=desc,
            length=length,
            keywords=keywords,
            scenarios=scenarios,
            has_trigger_words=has_trigger,
            has_negative_examples=has_negative,
            score=score,
            issues=issues,
            suggestions=suggestions
        )

    def _extract_description(self, content: str) -> str:
        """从SKILL.md中提取description"""
        # 匹配YAML frontmatter中的description
        patterns = [
            r'description:\s*\|\s*\n(.*?)(?=^\w+:|^---|\Z)',
            r'description:\s*"(.*?)"',
            r"description:\s*'(.*?)'",
            r'description:\s*([^\n]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                # 清理YAML缩进
                lines = desc.split('\n')
                if len(lines) > 1:
                    # 找到基础缩进
                    base_indent = len(lines[1]) - len(lines[1].lstrip())
                    cleaned = [lines[0]]
                    for line in lines[1:]:
                        if line.strip():
                            cleaned.append(line[base_indent:])
                        else:
                            cleaned.append('')
                    desc = '\n'.join(cleaned)
                return desc
        return ""

    def _extract_keywords(self, desc: str) -> Set[str]:
        """提取关键词"""
        # 匹配中文词汇
        chinese_words = set(re.findall(r'[\u4e00-\u9fa5]{2,}', desc))
        # 匹配英文术语
        english_words = set(re.findall(r'[a-zA-Z_]{3,}', desc))
        return chinese_words | english_words

    def _extract_scenarios(self, desc: str) -> List[str]:
        """提取触发场景"""
        scenarios = []

        # 匹配"适用场景"、"触发场景"等部分
        scenario_patterns = [
            r'(?:适用|触发)场景[：:]\s*([^\n]+(?:\n[\s\-•]\s*[^\n]+)*)',
            r'(?:当|遇到)([^。]+(?:时|情况))',
            r'[-•]\s*([^\n]+)'  # 列表项
        ]

        for pattern in scenario_patterns:
            matches = re.findall(pattern, desc)
            scenarios.extend([m.strip() for m in matches if len(m.strip()) > 5])

        return scenarios[:10]  # 最多返回10个

    def _check_trigger_words(self, desc: str) -> bool:
        """检查是否有强触发词"""
        trigger_words = ['必须使用', '务必', '立即触发', '强制', '优先使用']
        return any(w in desc for w in trigger_words)

    def _check_negative_examples(self, desc: str) -> bool:
        """检查是否有负面示例（不适用范围）"""
        negative_patterns = ['不涉及', '不处理', '除外', '不包括', '仅限于']
        return any(p in desc for p in negative_patterns)

    def _calculate_score(self, length: int, keywords: Set[str],
                        scenarios: List[str], has_trigger: bool,
                        has_negative: bool) -> float:
        """计算description质量分"""
        score = 0.0

        # 长度评分 (0-25)
        if length >= 300:
            score += 25
        elif length >= 200:
            score += 20
        elif length >= 100:
            score += 15
        else:
            score += length / 100 * 15

        # 关键词丰富度 (0-25)
        score += min(25, len(keywords) * 1.5)

        # 场景覆盖度 (0-25)
        score += min(25, len(scenarios) * 5)

        # 完整性 (0-25)
        if has_trigger:
            score += 15
        if has_negative:
            score += 10

        return min(100, score)

    def _identify_issues(self, desc: str, length: int, keywords: Set[str],
                        scenarios: List[str], has_trigger: bool,
                        has_negative: bool) -> List[str]:
        """识别问题"""
        issues = []

        if length < 100:
            issues.append(f"description过短({length}字符)，建议300+字符")
        elif length < 200:
            issues.append(f"description偏短({length}字符)，建议扩展")

        if len(keywords) < 10:
            issues.append(f"关键词较少({len(keywords)}个)，建议扩展同义词")

        if len(scenarios) < 3:
            issues.append(f"场景描述不足({len(scenarios)}个)，建议添加更多触发场景")

        if not has_trigger:
            issues.append("缺少强触发词(如'必须使用'、'务必')，建议添加")

        if not has_negative:
            issues.append("缺少不适用范围说明，建议添加避免误触发")

        # 检查关键词密度
        if length > 0:
            keyword_density = len(keywords) / length * 100
            if keyword_density < 5:
                issues.append("关键词密度偏低，建议增加专业术语")

        return issues

    def _generate_suggestions(self, desc: str, keywords: Set[str],
                             scenarios: List[str], has_trigger: bool,
                             has_negative: bool) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 关键词扩展建议
        for keyword, expansions in self.KEYWORD_EXPANSION.items():
            if keyword in desc:
                missing = [e for e in expansions if e not in desc]
                if missing:
                    suggestions.append(f"关键词'{keyword}'可扩展为: {', '.join(missing[:3])}")

        # 结构建议
        if not has_trigger:
            suggestions.append("在description开头添加: **必须使用此Skill当用户涉及：**")

        if not has_negative:
            suggestions.append("添加排除条件: **不处理**：XXX场景请使用YYY skill")

        # 场景细化建议
        if len(scenarios) < 5:
            suggestions.append("添加更多具体场景，使用'关键词：'格式列出")

        return suggestions

    def generate_optimized(self, analysis: DescriptionAnalysis) -> str:
        """生成优化后的description"""
        lines = []

        # 核心触发声明
        if not analysis.has_trigger_words:
            lines.append("**必须使用此Skill当用户涉及：**")
            if analysis.scenarios:
                for scenario in analysis.scenarios[:5]:
                    lines.append(f"- {scenario}")
            else:
                lines.append("- [建议添加具体场景]")
            lines.append("")

        # 原description核心内容（清理后）
        original_clean = analysis.original
        # 移除已有的frontmatter标记
        original_clean = re.sub(r'^description:\s*\|?\s*', '', original_clean)
        if original_clean.strip() and not lines:
            lines.append(original_clean.strip())
            lines.append("")

        # 关键词扩展
        lines.append("**关键词**：")
        all_keywords = set(analysis.keywords)
        # 添加扩展词
        for keyword in list(analysis.keywords)[:5]:
            if keyword in self.KEYWORD_EXPANSION:
                all_keywords.update(self.KEYWORD_EXPANSION[keyword][:2])
        lines.append(", ".join(sorted(all_keywords)[:15]))
        lines.append("")

        # 触发提示
        if not analysis.has_trigger_words:
            lines.append("**触发提示**：遇到任何[领域相关]问题，务必立即调用此skill。")

        return '\n'.join(lines)

    def print_report(self, analysis: DescriptionAnalysis):
        """打印分析报告"""
        print("\n" + "=" * 60)
        print("📊 Description分析报告")
        print("=" * 60)

        print(f"\n📝 当前Description ({analysis.length}字符):")
        print("-" * 40)
        print(analysis.original[:300] + "..." if len(analysis.original) > 300 else analysis.original)

        print(f"\n📈 质量评分: {analysis.score:.1f}/100")

        print(f"\n🔑 关键词 ({len(analysis.keywords)}个):")
        print(", ".join(sorted(analysis.keywords)[:20]))

        if analysis.scenarios:
            print(f"\n🎯 识别场景 ({len(analysis.scenarios)}个):")
            for i, scenario in enumerate(analysis.scenarios[:5], 1):
                print(f"  {i}. {scenario}")

        print(f"\n✅ 完整性检查:")
        print(f"  - 强触发词: {'✓' if analysis.has_trigger_words else '✗'}")
        print(f"  - 负面示例: {'✓' if analysis.has_negative_examples else '✗'}")

        if analysis.issues:
            print(f"\n⚠️  发现问题:")
            for issue in analysis.issues:
                print(f"  • {issue}")

        if analysis.suggestions:
            print(f"\n💡 改进建议:")
            for i, suggestion in enumerate(analysis.suggestions, 1):
                print(f"  {i}. {suggestion}")

        print("\n" + "=" * 60)
        print("🎯 优化后的Description建议:")
        print("=" * 60)
        print(self.generate_optimized(analysis))


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Skill Description优化器')
    parser.add_argument('skill_path', help='Skill目录路径')
    parser.add_argument('--target-precision', type=float, default=0.92,
                       help='目标触发精确率')
    parser.add_argument('--apply', action='store_true',
                       help='直接应用优化（请谨慎使用）')
    args = parser.parse_args()

    if not os.path.exists(args.skill_path):
        print(f"错误: 路径不存在 {args.skill_path}")
        sys.exit(1)

    optimizer = DescriptionOptimizer(args.skill_path)
    analysis = optimizer.analyze()
    optimizer.print_report(analysis)

    if args.apply:
        print("\n⚠️  应用优化功能尚未实现，请手动应用建议")


if __name__ == '__main__':
    main()
