#!/usr/bin/env python3
"""
Skill分析工具 - 对比分析多个skill，生成能力矩阵和差距分析
用法:
    python3 skill-analyzer.py --compare <skill1> <skill2> [<skill3>...]
    python3 skill-analyzer.py --health-check <skill-path>
    python3 skill-analyzer.py --gap-analysis <target> <reference>
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict
import json

sys.path.insert(0, str(Path(__file__).parent))
from skill_discovery import scan_all_skills, calculate_similarity, parse_skill_metadata

# Also update the reference in skill-fusion.py

SKILLS_BASE_DIR = Path.home() / ".claude" / "skills"


def extract_capabilities(skill: Dict) -> List[str]:
    """从skill内容中提取能力标签"""
    capabilities = []
    skill_md = Path(skill['path']) / "SKILL.md"

    if not skill_md.exists():
        return capabilities

    content = skill_md.read_text(encoding='utf-8')

    # 从标题中提取能力标签
    cap_patterns = [
        r'##\s*(.+?)(?:能力|专家|系统|框架)',
        r'(?:核心能力|支持场景|涵盖)[：:]\s*(.+?)(?:\n|$)',
        r'(?:能力|功能)[：:]\s*(.+?)(?:\n|$)',
    ]

    for pattern in cap_patterns:
        matches = re.findall(pattern, content)
        capabilities.extend(matches)

    # 去重并清理
    capabilities = list(set(c.strip() for c in capabilities if len(c.strip()) > 2))
    return capabilities[:10]


def analyze_skill_structure(skill: Dict) -> Dict:
    """分析skill的结构完整性"""
    skill_md = Path(skill['path']) / "SKILL.md"
    if not skill_md.exists():
        return {}

    content = skill_md.read_text(encoding='utf-8')

    structure = {
        'has_frontmatter': bool(re.search(r'^---\s*\n', content)),
        'has_description': 'description' in content.lower(),
        'section_count': len(re.findall(r'^##\s+', content, re.MULTILINE)),
        'code_block_count': len(re.findall(r'```', content)) // 2,
        'table_count': len(re.findall(r'\|[-:]+\|', content)),
        'list_item_count': len(re.findall(r'^[\s]*[-*]\s+', content, re.MULTILINE)),
        'has_scripts': skill.get('has_scripts', False),
        'has_references': skill.get('has_references', False),
    }

    # 计算健康度得分
    score = 0
    if structure['has_frontmatter']: score += 15
    if structure['has_description']: score += 15
    score += min(structure['section_count'] * 5, 20)
    score += min(structure['code_block_count'] * 3, 15)
    score += min(structure['table_count'] * 5, 15)
    score += min(structure['list_item_count'] * 0.5, 10)
    if structure['has_scripts']: score += 5
    if structure['has_references']: score += 5

    structure['health_score'] = min(score, 100)
    return structure


def compare_skills(skill_names: List[str]) -> Dict:
    """对比多个skill，生成能力矩阵"""
    all_skills = {s['name']: s for s in scan_all_skills()}

    skills_to_compare = []
    for name in skill_names:
        if name in all_skills:
            skill = all_skills[name]
            skill['capabilities'] = extract_capabilities(skill)
            skill['structure'] = analyze_skill_structure(skill)
            skills_to_compare.append(skill)
        else:
            print(f"Warning: Skill '{name}' 未找到")

    if len(skills_to_compare) < 2:
        print("Error: 需要至少2个有效的skill进行对比")
        return {}

    # 构建能力矩阵
    all_capabilities = set()
    for skill in skills_to_compare:
        all_capabilities.update(skill.get('capabilities', []))

    capability_matrix = {}
    for cap in sorted(all_capabilities):
        capability_matrix[cap] = {}
        for skill in skills_to_compare:
            has_cap = cap in skill.get('capabilities', [])
            capability_matrix[cap][skill['name']] = '✓' if has_cap else ''

    # 计算相似度矩阵
    similarity_matrix = {}
    for i, skill_a in enumerate(skills_to_compare):
        similarity_matrix[skill_a['name']] = {}
        for skill_b in skills_to_compare:
            if skill_a['name'] == skill_b['name']:
                similarity_matrix[skill_a['name']][skill_b['name']] = 1.0
            else:
                sim = calculate_similarity(skill_a, skill_b)
                similarity_matrix[skill_a['name']][skill_b['name']] = round(sim, 2)

    # 结构对比
    structure_comparison = {}
    for metric in ['has_frontmatter', 'has_description', 'section_count',
                   'code_block_count', 'table_count', 'has_scripts', 'has_references']:
        structure_comparison[metric] = {}
        for skill in skills_to_compare:
            structure_comparison[metric][skill['name']] = skill['structure'].get(metric, 0)

    return {
        'skills': [s['name'] for s in skills_to_compare],
        'capability_matrix': capability_matrix,
        'similarity_matrix': similarity_matrix,
        'structure_comparison': structure_comparison,
        'health_scores': {s['name']: s['structure'].get('health_score', 0) for s in skills_to_compare},
    }


def gap_analysis(target_name: str, reference_names: List[str]) -> Dict:
    """分析目标skill与参考skills之间的差距"""
    all_skills = {s['name']: s for s in scan_all_skills()}

    if target_name not in all_skills:
        print(f"Error: Target skill '{target_name}' 未找到")
        return {}

    target = all_skills[target_name]
    target['capabilities'] = extract_capabilities(target)
    target['structure'] = analyze_skill_structure(target)

    gaps = {
        'missing_capabilities': [],
        'improvable_areas': [],
        'content_gaps': [],
        'reference_best_practices': [],
    }

    all_ref_capabilities = set()
    best_structures = {}

    for ref_name in reference_names:
        if ref_name not in all_skills:
            print(f"Warning: Reference skill '{ref_name}' 未找到")
            continue

        ref = all_skills[ref_name]
        ref['capabilities'] = extract_capabilities(ref)
        ref['structure'] = analyze_skill_structure(ref)

        # 收集参考capabilities
        all_ref_capabilities.update(ref['capabilities'])

        # 找出目标skill缺失的capabilities
        for cap in ref['capabilities']:
            if cap not in target['capabilities']:
                gaps['missing_capabilities'].append({
                    'capability': cap,
                    'from': ref_name,
                })

        # 记录最佳结构实践
        for metric in ['section_count', 'code_block_count', 'table_count']:
            if metric not in best_structures or \
               ref['structure'].get(metric, 0) > best_structures[metric]['value']:
                best_structures[metric] = {
                    'value': ref['structure'].get(metric, 0),
                    'from': ref_name,
                }

    # 结构改进建议
    for metric, best in best_structures.items():
        current = target['structure'].get(metric, 0)
        if current < best['value']:
            gaps['improvable_areas'].append({
                'area': metric,
                'current': current,
                'target': best['value'],
                'reference': best['from'],
            })

    # 内容完整性差距
    if not target.get('has_scripts'):
        has_script_refs = [r for r in reference_names if all_skills.get(r, {}).get('has_scripts')]
        if has_script_refs:
            gaps['content_gaps'].append({
                'gap': '缺少scripts目录',
                'suggestion': f'可参考 {", ".join(has_script_refs[:2])}',
            })

    if not target.get('has_references'):
        has_ref_refs = [r for r in reference_names if all_skills.get(r, {}).get('has_references')]
        if has_ref_refs:
            gaps['content_gaps'].append({
                'gap': '缺少references目录',
                'suggestion': f'可参考 {", ".join(has_ref_refs[:2])}',
            })

    gaps['target'] = target_name
    gaps['references'] = reference_names

    return gaps


def health_check(skill_path: str) -> Dict:
    """对单个skill进行健康度检查"""
    path = Path(skill_path)
    if not path.exists():
        # 尝试在skills目录中查找
        path = SKILLS_BASE_DIR / skill_path

    if not path.exists():
        print(f"Error: Skill path not found: {skill_path}")
        return {}

    skill = parse_skill_metadata(path)
    skill['capabilities'] = extract_capabilities(skill)
    skill['structure'] = analyze_skill_structure(skill)

    # 生成改进建议
    suggestions = []

    if not skill['structure'].get('has_frontmatter'):
        suggestions.append({
            'priority': 'high',
            'area': 'frontmatter',
            'issue': '缺少frontmatter',
            'suggestion': '添加YAML frontmatter，包含name和description',
        })

    if skill['structure'].get('section_count', 0) < 3:
        suggestions.append({
            'priority': 'medium',
            'area': 'structure',
            'issue': '章节过少',
            'suggestion': f"当前{skill['structure']['section_count']}个章节，建议至少5个",
        })

    if not skill.get('has_scripts'):
        suggestions.append({
            'priority': 'low',
            'area': 'tools',
            'issue': '缺少scripts目录',
            'suggestion': '可添加辅助脚本增强实用性',
        })

    # 找出相似skill作为参考
    all_skills = scan_all_skills()
    similar = []
    for other in all_skills:
        if other['name'] != skill['name']:
            sim = calculate_similarity(skill, other)
            if sim > 0.3:
                similar.append((other['name'], sim))

    similar = sorted(similar, key=lambda x: x[1], reverse=True)[:3]

    return {
        'skill_name': skill['name'],
        'health_score': skill['structure'].get('health_score', 0),
        'structure': skill['structure'],
        'capabilities': skill['capabilities'],
        'suggestions': suggestions,
        'similar_skills': similar,
    }


def print_comparison_report(report: Dict):
    """打印对比报告"""
    print(f"\n{'='*70}")
    print("Skill对比分析报告")
    print(f"{'='*70}")

    print(f"\n对比Skills: {', '.join(report['skills'])}")

    # 健康度得分
    print("\n📊 健康度评分:")
    for name, score in sorted(report['health_scores'].items(), key=lambda x: -x[1]):
        bar = "█" * int(score / 5)
        print(f"  {name:30s} {score:3d}/100 {bar}")

    # 能力矩阵
    if report['capability_matrix']:
        print("\n🔧 能力矩阵:")
        caps = list(report['capability_matrix'].keys())[:10]  # 最多显示10个
        col_width = max(len(c) for c in report['skills']) + 2

        header = "能力".ljust(20)
        for skill_name in report['skills']:
            header += skill_name[:col_width-2].ljust(col_width)
        print("  " + header)
        print("  " + "-" * (20 + col_width * len(report['skills'])))

        for cap in caps:
            line = f"  {cap[:18].ljust(20)}"
            for skill_name in report['skills']:
                mark = report['capability_matrix'][cap].get(skill_name, '')
                line += mark.ljust(col_width)
            print(line)

    # 相似度矩阵
    print("\n🔗 相似度矩阵:")
    for skill_a in report['skills']:
        line = f"  {skill_a[:20].ljust(22)}"
        for skill_b in report['skills']:
            sim = report['similarity_matrix'][skill_a][skill_b]
            if skill_a == skill_b:
                line += "  -  "
            else:
                line += f"{sim:.2f} "
        print(line)


def print_gap_analysis(gaps: Dict):
    """打印差距分析报告"""
    print(f"\n{'='*70}")
    print(f"Skill差距分析报告: {gaps.get('target', 'Unknown')}")
    print(f"{'='*70}")

    print(f"\n参考Skills: {', '.join(gaps.get('references', []))}")

    # 缺失的能力
    if gaps.get('missing_capabilities'):
        print("\n⚠️  缺失的能力:")
        for item in gaps['missing_capabilities'][:10]:
            print(f"  - {item['capability']} (来自: {item['from']})")
        if len(gaps['missing_capabilities']) > 10:
            print(f"  ... 还有 {len(gaps['missing_capabilities']) - 10} 项")

    # 可改进领域
    if gaps.get('improvable_areas'):
        print("\n📈 可改进领域:")
        for item in gaps['improvable_areas']:
            print(f"  - {item['area']}: {item['current']} → {item['target']} (参考: {item['reference']})")

    # 内容缺口
    if gaps.get('content_gaps'):
        print("\n📝 内容缺口:")
        for item in gaps['content_gaps']:
            print(f"  - {item['gap']}")
            print(f"    建议: {item['suggestion']}")


def print_health_report(report: Dict):
    """打印健康度报告"""
    print(f"\n{'='*70}")
    print(f"Skill健康度检查: {report['skill_name']}")
    print(f"{'='*70}")

    score = report['health_score']
    grade = 'A' if score >= 90 else 'B' if score >= 75 else 'C' if score >= 60 else 'D'
    bar = "█" * int(score / 5)

    print(f"\n🏥 健康度评分: {score}/100 (等级: {grade})")
    print(f"    {bar}")

    print("\n📋 结构详情:")
    for key, value in report['structure'].items():
        if key != 'health_score':
            print(f"  - {key}: {value}")

    if report.get('capabilities'):
        print("\n🔧 识别到的能力:")
        for cap in report['capabilities'][:8]:
            print(f"  - {cap}")

    if report.get('suggestions'):
        print("\n💡 改进建议:")
        for sug in sorted(report['suggestions'], key=lambda x: x['priority']):
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(sug['priority'], '⚪')
            print(f"  {priority_emoji} [{sug['area']}] {sug['issue']}")
            print(f"      → {sug['suggestion']}")

    if report.get('similar_skills'):
        print("\n👥 相似Skills (可借鉴):")
        for name, sim in report['similar_skills']:
            print(f"  - {name}: {sim:.2f} 相似度")


def main():
    parser = argparse.ArgumentParser(description='Skill分析工具')
    parser.add_argument('--compare', nargs='+', help='对比多个skill')
    parser.add_argument('--health-check', type=str, help='检查skill健康度')
    parser.add_argument('--gap-analysis', type=str, help='目标skill名称')
    parser.add_argument('--references', nargs='+', help='参考skill名称列表')
    parser.add_argument('--output', type=str, help='输出JSON文件')

    args = parser.parse_args()

    if args.compare:
        report = compare_skills(args.compare)
        if report:
            print_comparison_report(report)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)

    elif args.health_check:
        report = health_check(args.health_check)
        if report:
            print_health_report(report)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)

    elif args.gap_analysis and args.references:
        gaps = gap_analysis(args.gap_analysis, args.references)
        if gaps:
            print_gap_analysis(gaps)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(gaps, f, ensure_ascii=False, indent=2)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
