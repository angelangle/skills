#!/usr/bin/env python3
"""
skill-doctor.py - Skill全面诊断工具

自动分析skill的健康度，识别改进机会。
支持工程能力和科研能力的双重评估。

Usage:
    python3 skill-doctor.py <skill-path> [--output-format=json|md]
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class DiagnosisResult:
    """诊断结果数据结构"""
    skill_name: str
    overall_score: float  # 0-100
    engineering_score: float
    research_score: float
    trigger_score: float
    structure_score: float
    freshness_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]


class SkillDoctor:
    """Skill诊断器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.findings = []
        self.recommendations = []

    def diagnose(self) -> DiagnosisResult:
        """执行全面诊断"""
        print(f"🔍 诊断Skill: {self.skill_name}")
        print("=" * 50)

        # 各维度诊断
        structure = self._check_structure()
        description = self._analyze_description()
        references = self._check_references()
        scripts = self._analyze_scripts()
        freshness = self._check_freshness()

        # 计算分数
        engineering = self._calc_engineering_score(structure, scripts, freshness)
        research = self._calc_research_score(references, description)
        trigger = description['score']
        overall = (engineering + research + trigger) / 3

        return DiagnosisResult(
            skill_name=self.skill_name,
            overall_score=round(overall, 1),
            engineering_score=round(engineering, 1),
            research_score=round(research, 1),
            trigger_score=round(trigger, 1),
            structure_score=round(structure['score'], 1),
            freshness_score=round(freshness['score'], 1),
            issues=self.findings,
            recommendations=self.recommendations
        )

    def _check_structure(self) -> Dict:
        """检查目录结构"""
        print("\n📁 检查目录结构...")

        structure = {
            'has_skill_md': False,
            'has_references': False,
            'has_scripts': False,
            'has_assets': False,
            'reference_files': [],
            'script_files': [],
            'score': 0
        }

        # 检查SKILL.md
        skill_md = self.skill_path / 'SKILL.md'
        if skill_md.exists():
            structure['has_skill_md'] = True
            structure['skill_md_lines'] = len(skill_md.read_text().splitlines())
        else:
            self.findings.append({
                'severity': 'error',
                'category': 'structure',
                'message': '缺少SKILL.md文件'
            })

        # 检查references
        refs_dir = self.skill_path / 'references'
        if refs_dir.exists():
            structure['has_references'] = True
            structure['reference_files'] = [
                f.name for f in refs_dir.iterdir() if f.is_file()
            ]
            if len(structure['reference_files']) < 2:
                self.findings.append({
                    'severity': 'warning',
                    'category': 'structure',
                    'message': f'references/文件较少({len(structure["reference_files"])})，建议扩充资料'
                })
                self.recommendations.append("使用WebSearch检索领域最新资料，扩充references/")
        else:
            self.findings.append({
                'severity': 'warning',
                'category': 'structure',
                'message': '缺少references/目录，科研能力受限'
            })
            self.recommendations.append("创建references/目录，添加理论基础文档")

        # 检查scripts
        scripts_dir = self.skill_path / 'scripts'
        if scripts_dir.exists():
            structure['has_scripts'] = True
            structure['script_files'] = [
                f.name for f in scripts_dir.iterdir()
                if f.is_file() and f.suffix in ['.py', '.sh', '.js']
            ]
        else:
            self.findings.append({
                'severity': 'info',
                'category': 'structure',
                'message': '缺少scripts/目录，工程化程度可提升'
            })

        # 计算结构分
        score = 0
        if structure['has_skill_md']: score += 40
        if structure['has_references']: score += 30
        if structure['has_scripts']: score += 20
        if structure['has_assets']: score += 10

        structure['score'] = score
        print(f"   结构得分: {score}/100")

        return structure

    def _analyze_description(self) -> Dict:
        """分析description质量"""
        print("\n📝 分析Description...")

        result = {
            'has_description': False,
            'keywords_count': 0,
            'scenarios_count': 0,
            'length': 0,
            'score': 0
        }

        skill_md = self.skill_path / 'SKILL.md'
        if not skill_md.exists():
            return result

        content = skill_md.read_text()

        # 提取description部分
        desc_match = re.search(r'description:\s*\|?\s*(.*?)(?=\n\w+:|---|$)',
                               content, re.DOTALL)
        if desc_match:
            result['has_description'] = True
            desc = desc_match.group(1)
            result['length'] = len(desc)

            # 分析关键词覆盖
            keywords = re.findall(r'[\u4e00-\u9fa5a-zA-Z]{2,}', desc)
            result['keywords_count'] = len(set(keywords))

            # 分析场景示例
            scenarios = re.findall(r'适用场景|关键词|触发', desc)
            result['scenarios_count'] = len(scenarios)

            # 评估质量
            if result['length'] < 100:
                self.findings.append({
                    'severity': 'warning',
                    'category': 'description',
                    'message': f'Description过短({result["length"]}字符)，建议扩展到300+字符'
                })
                self.recommendations.append("扩充description，添加更多关键词和场景示例")

            if result['scenarios_count'] < 3:
                self.findings.append({
                    'severity': 'info',
                    'category': 'description',
                    'message': '场景描述不够丰富，建议添加"触发场景"、"关键词"小节'
                })

        # 计算description得分
        score = min(100, result['length'] / 5 + result['keywords_count'] * 2)
        result['score'] = score
        print(f"   Description得分: {score:.1f}/100")

        return result

    def _check_references(self) -> Dict:
        """检查参考资料"""
        print("\n📚 检查References...")

        result = {
            'file_count': 0,
            'total_lines': 0,
            'has_theory': False,
            'has_practice': False,
            'has_examples': False,
            'score': 0
        }

        refs_dir = self.skill_path / 'references'
        if not refs_dir.exists():
            return result

        for ref_file in refs_dir.iterdir():
            if ref_file.is_file() and ref_file.suffix == '.md':
                result['file_count'] += 1
                content = ref_file.read_text()
                result['total_lines'] += len(content.splitlines())

                # 内容分类
                content_lower = content.lower()
                if any(w in content_lower for w in ['theory', '理论', '原理', 'concept']):
                    result['has_theory'] = True
                if any(w in content_lower for w in ['practice', '实践', 'best practice', 'guide']):
                    result['has_practice'] = True
                if any(w in content_lower for w in ['example', '示例', 'case study', '案例']):
                    result['has_examples'] = True

        # 评估科研深度
        if result['file_count'] == 0:
            self.findings.append({
                'severity': 'warning',
                'category': 'research',
                'message': '无参考资料，科研能力不足'
            })
            self.recommendations.append("使用WebSearch检索领域学术资源，创建references/theory.md")
        elif not result['has_theory']:
            self.findings.append({
                'severity': 'info',
                'category': 'research',
                'message': '缺少理论基础文档，建议添加'
            })

        # 计算科研分
        score = min(100, result['file_count'] * 15 + result['total_lines'] / 10)
        result['score'] = score
        print(f"   References得分: {score:.1f}/100 ({result['file_count']}个文件)")

        return result

    def _analyze_scripts(self) -> Dict:
        """分析工具脚本"""
        print("\n🔧 分析Scripts...")

        result = {
            'file_count': 0,
            'total_lines': 0,
            'has_python': False,
            'has_shell': False,
            'score': 0
        }

        scripts_dir = self.skill_path / 'scripts'
        if not scripts_dir.exists():
            return result

        for script in scripts_dir.iterdir():
            if script.is_file():
                result['file_count'] += 1
                result['total_lines'] += len(script.read_text().splitlines())

                if script.suffix == '.py':
                    result['has_python'] = True
                elif script.suffix == '.sh':
                    result['has_shell'] = True

        # 计算工程分
        score = min(100, result['file_count'] * 20 + result['total_lines'] / 5)
        result['score'] = score
        print(f"   Scripts得分: {score:.1f}/100 ({result['file_count']}个脚本)")

        return result

    def _check_freshness(self) -> Dict:
        """检查内容时效性"""
        print("\n⏰ 检查内容时效性...")

        result = {
            'last_modified': None,
            'skill_md_size': 0,
            'score': 80  # 默认中等
        }

        skill_md = self.skill_path / 'SKILL.md'
        if skill_md.exists():
            import time
            mtime = skill_md.stat().st_mtime
            result['last_modified'] = time.strftime('%Y-%m-%d', time.localtime(mtime))
            result['skill_md_size'] = skill_md.stat().st_size

            # 检查是否需要更新（超过90天）
            days_old = (time.time() - mtime) / 86400
            if days_old > 90:
                self.findings.append({
                    'severity': 'info',
                    'category': 'freshness',
                    'message': f'SKILL.md已{int(days_old)}天未更新，建议检查时效性'
                })
                self.recommendations.append("使用WebSearch检索领域最新进展，更新过时内容")

        print(f"   时效性得分: {result['score']}/100")

        return result

    def _calc_engineering_score(self, structure, scripts, freshness) -> float:
        """计算工程能力得分"""
        return (
            structure['score'] * 0.3 +
            scripts['score'] * 0.4 +
            freshness['score'] * 0.3
        )

    def _calc_research_score(self, references, description) -> float:
        """计算科研能力得分"""
        return (
            references['score'] * 0.6 +
            min(100, description['keywords_count'] * 5) * 0.4
        )

    def print_report(self, result: DiagnosisResult, format: str = 'md'):
        """打印诊断报告"""
        if format == 'json':
            print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
        else:
            self._print_markdown_report(result)

    def _print_markdown_report(self, result: DiagnosisResult):
        """打印Markdown格式报告"""
        print("\n" + "=" * 50)
        print(f"# Skill诊断报告: {result.skill_name}")
        print("=" * 50)

        print(f"\n## 综合评分: {result.overall_score}/100")

        print("\n### 维度得分")
        print(f"- 工程能力: {result.engineering_score}")
        print(f"- 科研能力: {result.research_score}")
        print(f"- 触发能力: {result.trigger_score}")
        print(f"- 结构健康: {result.structure_score}")
        print(f"- 内容时效: {result.freshness_score}")

        if result.issues:
            print("\n### 发现问题")
            for issue in result.issues:
                emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(issue['severity'], '•')
                print(f"{emoji} [{issue['category']}] {issue['message']}")

        if result.recommendations:
            print("\n### 改进建议")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"{i}. {rec}")

        print("\n### 元进化建议")
        if result.research_score < 60:
            print("🔬 科研能力需增强: 使用WebSearch检索学术资源，添加理论深度")
        if result.engineering_score < 60:
            print("🔧 工程能力需增强: 添加自动化脚本，优化工作流程")
        if result.trigger_score < 70:
            print("🎯 触发率需优化: 扩展关键词，细化场景描述")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Skill全面诊断工具')
    parser.add_argument('skill_path', help='Skill目录路径')
    parser.add_argument('--output-format', choices=['json', 'md'], default='md',
                        help='输出格式')
    args = parser.parse_args()

    if not os.path.exists(args.skill_path):
        print(f"错误: 路径不存在 {args.skill_path}")
        sys.exit(1)

    doctor = SkillDoctor(args.skill_path)
    result = doctor.diagnose()
    doctor.print_report(result, args.output_format)


if __name__ == '__main__':
    main()
