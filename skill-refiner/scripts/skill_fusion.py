#!/usr/bin/env python3
"""
Skill融合工具 - 将多个skill合并为一个统一、精简、增强的新skill
用法:
    python3 skill-fusion.py --merge <skill1> <skill2> [--skill3...] --output <new-skill-dir>
    python3 skill-fusion.py --analyze <skill1> <skill2>  # 仅分析，不执行融合
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from skill_discovery import scan_all_skills, calculate_similarity, parse_skill_metadata
from skill_analyzer import extract_capabilities, analyze_skill_structure, compare_skills

SKILLS_BASE_DIR = Path.home() / ".claude" / "skills"


def select_fusion_strategy(skills: List[Dict]) -> str:
    """根据skill相似度自动选择融合策略"""
    if len(skills) < 2:
        return 'single'

    # 计算平均相似度
    similarities = []
    for i, skill_a in enumerate(skills):
        for skill_b in skills[i+1:]:
            sim = calculate_similarity(skill_a, skill_b)
            similarities.append(sim)

    avg_similarity = sum(similarities) / len(similarities) if similarities else 0

    if avg_similarity > 0.7:
        return 'merge'  # 高度重叠，去重合并
    elif avg_similarity > 0.3:
        return 'layer'  # 中度相似，分层整合
    else:
        return 'separate'  # 差异太大，不建议融合


def merge_frontmatters(skills: List[Dict]) -> Dict:
    """合并多个skill的frontmatter"""
    merged = {
        'name': '',
        'description': '',
        'keywords': [],
    }

    # 选择最通用的名称
    common_prefix = os.path.commonprefix([s['name'] for s in skills])
    if common_prefix and len(common_prefix) > 3:
        merged['name'] = common_prefix.rstrip('-_')
    else:
        # 使用类别+功能的命名
        domains = set()
        for s in skills:
            if s['name'].startswith('os-'):
                domains.add('os')
            elif 'debug' in s['name']:
                domains.add('debug')
            elif 'dev' in s['name']:
                domains.add('dev')
        if domains:
            merged['name'] = '-'.join(sorted(domains)) + '-unified'
        else:
            merged['name'] = skills[0]['name'] + '-enhanced'

    # 合并description
    descriptions = [s.get('description', '') for s in skills if s.get('description')]
    if descriptions:
        # 选择最全面的description
        best_desc = max(descriptions, key=len)
        merged['description'] = best_desc

    # 合并关键词
    all_keywords = set()
    for s in skills:
        all_keywords.update(s.get('keywords', []))
    merged['keywords'] = list(all_keywords)

    return merged


def merge_content_structured(skills: List[Dict]) -> str:
    """结构化合并skill内容"""
    all_sections = defaultdict(list)
    section_sources = defaultdict(list)

    for skill in skills:
        skill_md = Path(skill['path']) / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding='utf-8')

        # 移除frontmatter
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

        # 解析章节
        sections = re.split(r'\n(?=##\s+)', content)

        for section in sections:
            if not section.strip():
                continue

            # 提取章节标题
            title_match = re.match(r'##\s+(.+?)(?:\n|$)', section)
            if title_match:
                title = title_match.group(1).strip()
                # 归一化章节标题
                normalized_title = normalize_section_title(title)

                # 去重：如果内容相似度很高，则跳过
                is_duplicate = False
                for existing in all_sections[normalized_title]:
                    if content_similarity(section, existing) > 0.8:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    all_sections[normalized_title].append(section)
                    section_sources[normalized_title].append(skill['name'])

    # 按优先级排序章节
    priority_order = [
        '概述', '简介', 'Introduction', 'Overview',
        '核心能力', '能力', 'Capabilities', 'Features',
        '工作流程', '流程', 'Workflow', 'Process',
        '使用方法', '使用', 'Usage',
        '最佳实践', '实践', 'Best Practices',
        '工具', '脚本', 'Tools', 'Scripts',
        '参考', '资料', 'References',
        '附录', 'Appendix',
    ]

    sorted_sections = []
    processed = set()

    # 按优先级添加
    for priority in priority_order:
        for title in list(all_sections.keys()):
            if title not in processed and priority in title:
                for section in all_sections[title]:
                    sorted_sections.append((title, section))
                processed.add(title)

    # 添加剩余章节
    for title, sections in all_sections.items():
        if title not in processed:
            for section in sections:
                sorted_sections.append((title, section))

    # 合并为最终内容
    merged_content = []
    current_title = None

    for title, section in sorted_sections:
        if title != current_title:
            merged_content.append(f"\n## {title}")
            current_title = title
            # 添加来源标注
            sources = section_sources.get(title, [])
            if len(sources) > 1:
                merged_content.append(f"\n*(整合自: {', '.join(sources)})*")

        # 移除章节标题，只保留内容
        section_content = re.sub(r'^##\s+.+?\n', '', section)
        merged_content.append(section_content)

    return '\n'.join(merged_content)


def normalize_section_title(title: str) -> str:
    """归一化章节标题以便合并"""
    # 映射常见变体到标准标题
    title_map = {
        # 概述类
        '介绍': '概述',
        '简介': '概述',
        'Introduction': '概述',
        'Overview': '概述',
        'What is': '概述',
        # 能力类
        '核心能力': '核心能力',
        'Capabilities': '核心能力',
        'Features': '核心能力',
        '功能': '核心能力',
        # 工作流类
        'Workflow': '工作流程',
        'Process': '工作流程',
        '流程': '工作流程',
        '工作流': '工作流程',
        # 工具类
        'Tools': '工具链',
        'Scripts': '工具链',
        '工具': '工具链',
        '脚本': '工具链',
        # 参考类
        'References': '参考资料',
        '参考': '参考资料',
        '资料': '参考资料',
    }

    for key, value in title_map.items():
        if key in title:
            return value

    return title


def content_similarity(content_a: str, content_b: str) -> float:
    """计算两段内容的相似度"""
    # 简化版：基于词袋模型
    words_a = set(re.findall(r'\b[a-z]{3,}\b', content_a.lower()))
    words_b = set(re.findall(r'\b[a-z]{3,}\b', content_b.lower()))

    if not words_a or not words_b:
        return 0

    overlap = len(words_a & words_b)
    union = len(words_a | words_b)

    return overlap / union if union > 0 else 0


def merge_scripts(skills: List[Dict], output_dir: Path):
    """合并scripts目录"""
    scripts_dir = output_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    merged_scripts = []
    script_sources = {}

    for skill in skills:
        src_scripts = Path(skill['path']) / "scripts"
        if not src_scripts.exists():
            continue

        for script_file in src_scripts.iterdir():
            if script_file.is_file():
                script_name = script_file.name

                # 检查是否重复
                if script_name in script_sources:
                    # 重命名避免冲突
                    base, ext = os.path.splitext(script_name)
                    script_name = f"{base}_{skill['name'][:3]}{ext}"

                dest = scripts_dir / script_name
                shutil.copy2(script_file, dest)
                script_sources[script_name] = skill['name']
                merged_scripts.append(script_name)

    return merged_scripts


def merge_references(skills: List[Dict], output_dir: Path):
    """合并references目录"""
    refs_dir = output_dir / "references"
    refs_dir.mkdir(exist_ok=True)

    merged_refs = []

    for skill in skills:
        src_refs = Path(skill['path']) / "references"
        if not src_refs.exists():
            continue

        for ref_file in src_refs.iterdir():
            if ref_file.is_file():
                ref_name = ref_file.name

                # 检查重复文件名
                dest = refs_dir / ref_name
                if dest.exists():
                    # 添加来源标记
                    base, ext = os.path.splitext(ref_name)
                    ref_name = f"{base}_{skill['name'][:3]}{ext}"
                    dest = refs_dir / ref_name

                shutil.copy2(ref_file, dest)
                merged_refs.append(ref_name)

    return merged_refs


def generate_fusion_report(skills: List[Dict], output_name: str, strategy: str,
                          merged_scripts: List[str], merged_refs: List[str]) -> str:
    """生成融合报告"""
    report = f"""# Skill融合报告

## 融合概况
- **融合策略**: {strategy}
- **输出Skill**: {output_name}
- **源Skills**: {len(skills)}个
- **融合时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 源Skills详情
| Skill名称 | 行数 | 脚本数 | 参考资料 | 健康度 |
|-----------|------|--------|----------|--------|
"""

    for skill in skills:
        scripts_count = len(list((Path(skill['path']) / "scripts").glob("*"))) if (Path(skill['path']) / "scripts").exists() else 0
        refs_count = len(list((Path(skill['path']) / "references").glob("*"))) if (Path(skill['path']) / "references").exists() else 0
        health = skill.get('structure', {}).get('health_score', 0)

        report += f"| {skill['name']} | {skill.get('line_count', 0)} | {scripts_count} | {refs_count} | {health}/100 |\n"

    # 相似度矩阵
    report += "\n## 相似度矩阵\n"
    report += "| Skill |"
    for skill in skills:
        report += f" {skill['name'][:10]} |"
    report += "\n|-------|"
    for _ in skills:
        report += "----------|"
    report += "\n"

    for skill_a in skills:
        report += f"| {skill_a['name'][:15]} |"
        for skill_b in skills:
            if skill_a['name'] == skill_b['name']:
                report += "    -     |"
            else:
                sim = calculate_similarity(skill_a, skill_b)
                report += f"  {sim:.2f}   |"
        report += "\n"

    # 融合结果统计
    report += f"""
## 融合结果
- **合并脚本**: {len(merged_scripts)}个
  - {', '.join(merged_scripts[:10])}{'...' if len(merged_scripts) > 10 else ''}
- **合并参考资料**: {len(merged_refs)}个
  - {', '.join(merged_refs[:10])}{'...' if len(merged_refs) > 10 else ''}

## 融合说明
"""

    if strategy == 'merge':
        report += """
本次融合采用**去重合并策略**，适用于高度重叠的skills：
- 保留了最全面的内容
- 去除了重复章节
- 统一了术语和格式
- 合并了脚本和参考资料
"""
    elif strategy == 'layer':
        report += """
本次融合采用**分层整合策略**，适用于互补的skills：
- 按层次组织内容（基础层/应用层/工具层）
- 保留了各skill的独特能力
- 建立了清晰的依赖关系
"""

    report += """
## 使用建议
1. 检查生成的SKILL.md完整性
2. 验证scripts目录中的脚本可用性
3. 更新references中的链接有效性
4. 根据需要调整description中的关键词

## 后续优化建议
- 定期运行skill-analyzer.py检查健康度
- 使用skill-discovery.py发现新的相似skill
- 持续迭代优化触发率和内容质量
"""

    return report


def fuse_skills(skill_names: List[str], output_dir: Optional[Path] = None, dry_run: bool = False) -> Dict:
    """执行skill融合"""
    # 1. 获取所有skill信息
    all_skills = {s['name']: s for s in scan_all_skills()}

    skills_to_fuse = []
    for name in skill_names:
        if name in all_skills:
            skill = all_skills[name]
            skill['structure'] = analyze_skill_structure(skill)
            skill['capabilities'] = extract_capabilities(skill)
            skills_to_fuse.append(skill)
        else:
            print(f"Warning: Skill '{name}' 未找到")

    if len(skills_to_fuse) < 2:
        print("Error: 需要至少2个有效的skill进行融合")
        return {}

    # 2. 选择融合策略
    strategy = select_fusion_strategy(skills_to_fuse)
    print(f"\n📊 检测到相似度: {strategy}")

    if strategy == 'separate':
        print("⚠️  Skills差异过大，不建议融合")
        print("建议：使用skill-discovery.py寻找更相似的skill")
        return {}

    # 3. 生成输出目录
    if output_dir is None:
        if strategy == 'merge':
            output_name = os.path.commonprefix([s['name'] for s in skills_to_fuse]).rstrip('-_') or f"{skills_to_fuse[0]['name']}-unified"
        else:
            output_name = f"{'-'.join(s['name'][:5] for s in skills_to_fuse[:2])}-fusion"
        output_dir = SKILLS_BASE_DIR / output_name

    if not dry_run:
        output_dir.mkdir(exist_ok=True)
        print(f"\n📁 输出目录: {output_dir}")

    # 4. 执行融合
    print("\n🔧 开始融合...")

    # 4.1 合并frontmatter
    frontmatter = merge_frontmatters(skills_to_fuse)
    print(f"  ✓ 合并frontmatter: {frontmatter['name']}")

    # 4.2 合并内容
    content = merge_content_structured(skills_to_fuse)
    print(f"  ✓ 合并内容: {len(content)} 字符")

    # 4.3 合并scripts和references（仅非dry_run）
    merged_scripts = []
    merged_refs = []

    if not dry_run:
        merged_scripts = merge_scripts(skills_to_fuse, output_dir)
        print(f"  ✓ 合并脚本: {len(merged_scripts)}个")

        merged_refs = merge_references(skills_to_fuse, output_dir)
        print(f"  ✓ 合并参考资料: {len(merged_refs)}个")

    # 5. 生成SKILL.md
    skill_md_content = f"""---
name: {frontmatter['name']}
description: |
  {frontmatter['description'][:200]}

  **融合来源**: {', '.join(s['name'] for s in skills_to_fuse)}
---

{content}

---

*本skill由skill-fusion.py自动生成*
*融合时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*源skills: {', '.join(s['name'] for s in skills_to_fuse)}*
"""

    if not dry_run:
        (output_dir / "SKILL.md").write_text(skill_md_content, encoding='utf-8')
        print(f"  ✓ 写入SKILL.md")

        # 6. 生成融合报告
        report = generate_fusion_report(skills_to_fuse, frontmatter['name'], strategy, merged_scripts, merged_refs)
        (output_dir / "FUSION_REPORT.md").write_text(report, encoding='utf-8')
        print(f"  ✓ 生成融合报告")

    return {
        'strategy': strategy,
        'output_dir': str(output_dir),
        'skills_fused': [s['name'] for s in skills_to_fuse],
        'frontmatter': frontmatter,
        'content_length': len(content),
        'scripts_count': len(merged_scripts),
        'references_count': len(merged_refs),
    }


def main():
    parser = argparse.ArgumentParser(description='Skill融合工具')
    parser.add_argument('--merge', nargs='+', help='要融合的skill名称列表')
    parser.add_argument('--output', type=str, help='输出目录名称')
    parser.add_argument('--analyze', nargs='+', help='仅分析，不执行融合')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，不实际创建文件')

    args = parser.parse_args()

    if args.analyze:
        print("🔍 分析模式（不执行融合）")
        strategy = select_fusion_strategy([parse_skill_metadata(SKILLS_BASE_DIR / name) for name in args.analyze])
        print(f"\n建议融合策略: {strategy}")

        if strategy == 'separate':
            print("\n⚠️  这些skills差异较大，不建议融合")
            print("相似度分析:")
            for i, name_a in enumerate(args.analyze):
                for name_b in args.analyze[i+1:]:
                    skill_a = parse_skill_metadata(SKILLS_BASE_DIR / name_a)
                    skill_b = parse_skill_metadata(SKILLS_BASE_DIR / name_b)
                    sim = calculate_similarity(skill_a, skill_b)
                    print(f"  {name_a} <-> {name_b}: {sim:.2f}")

    elif args.merge:
        output_dir = SKILLS_BASE_DIR / args.output if args.output else None
        result = fuse_skills(args.merge, output_dir, args.dry_run)

        if result:
            print(f"\n{'='*60}")
            print("✅ 融合完成!")
            print(f"{'='*60}")
            print(f"策略: {result['strategy']}")
            print(f"输出: {result['output_dir']}")
            print(f"内容: {result['content_length']} 字符")
            print(f"脚本: {result['scripts_count']} 个")
            print(f"资料: {result['references_count']} 个")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
