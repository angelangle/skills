#!/usr/bin/env python3
"""
Skill发现工具 - 扫描技能库，发现相似技能
用法:
    python3 skill-discovery.py --scan-all
    python3 skill-discovery.py --target <skill-name> --find-similar
    python3 skill-discovery.py --build-graph
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import Counter
import json

SKILLS_BASE_DIR = Path.home() / ".claude" / "skills"


def parse_skill_metadata(skill_path: Path) -> Dict:
    """解析skill的元数据"""
    metadata = {
        'name': skill_path.name,
        'path': str(skill_path),
        'description': '',
        'keywords': [],
        'capabilities': [],
        'line_count': 0,
        'has_scripts': False,
        'has_references': False,
    }

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return metadata

    content = skill_md.read_text(encoding='utf-8')
    metadata['line_count'] = len(content.splitlines())

    # 解析frontmatter
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # 提取description
        desc_match = re.search(r'description:\s*\|\s*\n(.*?)(?=\n\w+:|$)', frontmatter, re.DOTALL)
        if desc_match:
            metadata['description'] = desc_match.group(1).strip()
        else:
            desc_match = re.search(r'description:\s*(.+?)(?=\n|$)', frontmatter)
            if desc_match:
                metadata['description'] = desc_match.group(1).strip()

        # 提取关键词（从description中）
        if '关键词' in metadata['description']:
            kw_match = re.search(r'关键词.*?：(.+?)(?:\n|$)', metadata['description'])
            if kw_match:
                metadata['keywords'] = [k.strip() for k in kw_match.group(1).split(',')]

    # 检查是否有scripts和references
    metadata['has_scripts'] = (skill_path / "scripts").exists()
    metadata['has_references'] = (skill_path / "references").exists()

    # 从内容中提取能力标签
    cap_matches = re.findall(r'##\s*(.+?)(?:能力|专家|系统)', content)
    metadata['capabilities'] = cap_matches[:5]  # 最多5个

    return metadata


def scan_all_skills() -> List[Dict]:
    """扫描所有skill"""
    skills = []

    if not SKILLS_BASE_DIR.exists():
        print(f"Error: Skills directory not found: {SKILLS_BASE_DIR}")
        return skills

    for skill_dir in SKILLS_BASE_DIR.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                try:
                    metadata = parse_skill_metadata(skill_dir)
                    skills.append(metadata)
                except Exception as e:
                    print(f"Warning: Failed to parse {skill_dir.name}: {e}")

    return skills


def calculate_similarity(skill_a: Dict, skill_b: Dict) -> float:
    """计算两个skill的相似度 (0-1)"""
    scores = []

    # 1. 关键词重叠度 (40%)
    if skill_a.get('keywords') and skill_b.get('keywords'):
        set_a = set(k.lower() for k in skill_a['keywords'])
        set_b = set(k.lower() for k in skill_b['keywords'])
        if set_a and set_b:
            overlap = len(set_a & set_b)
            union = len(set_a | set_b)
            keyword_sim = overlap / union if union > 0 else 0
            scores.append(('keywords', keyword_sim, 0.4))

    # 2. 描述文本相似度 - 简化版：共享词汇 (30%)
    desc_a = skill_a.get('description', '').lower()
    desc_b = skill_b.get('description', '').lower()

    # 提取技术词汇（长度>2的词）
    words_a = set(re.findall(r'\b[a-z]{3,}\b', desc_a))
    words_b = set(re.findall(r'\b[a-z]{3,}\b', desc_b))

    if words_a and words_b:
        # 计算Jaccard相似度
        overlap = len(words_a & words_b)
        union = len(words_a | words_b)
        desc_sim = overlap / union if union > 0 else 0
        scores.append(('description', desc_sim, 0.3))

    # 3. 能力标签匹配 (20%)
    caps_a = set(c.lower() for c in skill_a.get('capabilities', []))
    caps_b = set(c.lower() for c in skill_b.get('capabilities', []))
    if caps_a and caps_b:
        overlap = len(caps_a & caps_b)
        union = len(caps_a | caps_b)
        cap_sim = overlap / union if union > 0 else 0
        scores.append(('capabilities', cap_sim, 0.2))

    # 4. 目录结构相似度 (10%)
    struct_sim = 0
    if skill_a.get('has_scripts') == skill_b.get('has_scripts'):
        struct_sim += 0.05
    if skill_a.get('has_references') == skill_b.get('has_references'):
        struct_sim += 0.05
    scores.append(('structure', struct_sim, 0.1))

    # 计算加权总分
    total_score = sum(score * weight for _, score, weight in scores)
    total_weight = sum(weight for _, _, weight in scores)

    return total_score / total_weight if total_weight > 0 else 0


def find_similar_skills(target_skill: Dict, all_skills: List[Dict], top_k: int = 5, threshold: float = 0.3) -> List[Tuple[Dict, float]]:
    """找到与目标skill最相似的skills"""
    similarities = []

    for skill in all_skills:
        if skill['name'] != target_skill['name']:
            score = calculate_similarity(target_skill, skill)
            if score >= threshold:
                similarities.append((skill, score))

    return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]


def build_skill_graph(skills: List[Dict]) -> Dict:
    """构建技能关系图谱"""
    graph = {
        'nodes': [],
        'edges': [],
        'clusters': {}
    }

    # 添加节点
    for skill in skills:
        graph['nodes'].append({
            'name': skill['name'],
            'line_count': skill.get('line_count', 0),
            'has_scripts': skill.get('has_scripts', False),
        })

    # 识别技能簇
    clusters = {
        'os-dev': [],
        'debug': [],
        'meta': [],
        'dev-agent': [],
        'hardware': [],
        'frontend': [],
        'other': []
    }

    for skill in skills:
        name = skill['name'].lower()
        if name.startswith('os-'):
            clusters['os-dev'].append(skill['name'])
        elif 'debug' in name:
            clusters['debug'].append(skill['name'])
        elif name in ['skill-refiner', 'skill-creator']:
            clusters['meta'].append(skill['name'])
        elif name.startswith('dev-agent'):
            clusters['dev-agent'].append(skill['name'])
        elif 'hw' in name or 'hardware' in name:
            clusters['hardware'].append(skill['name'])
        elif 'frontend' in name:
            clusters['frontend'].append(skill['name'])
        else:
            clusters['other'].append(skill['name'])

    graph['clusters'] = {k: v for k, v in clusters.items() if v}

    # 计算边（相似度>0.5）
    for i, skill_a in enumerate(skills):
        for skill_b in skills[i+1:]:
            sim = calculate_similarity(skill_a, skill_b)
            if sim > 0.5:
                graph['edges'].append({
                    'source': skill_a['name'],
                    'target': skill_b['name'],
                    'similarity': round(sim, 2)
                })

    return graph


def print_skill_list(skills: List[Dict]):
    """打印skill列表"""
    print(f"\n{'='*60}")
    print(f"发现 {len(skills)} 个Skills:")
    print(f"{'='*60}")

    for skill in sorted(skills, key=lambda x: x['name']):
        scripts = "[S]" if skill.get('has_scripts') else "   "
        refs = "[R]" if skill.get('has_references') else "   "
        lines = skill.get('line_count', 0)
        print(f"  {scripts} {refs} {lines:4d}L  {skill['name']}")


def print_similar_skills(target_name: str, similar: List[Tuple[Dict, float]]):
    """打印相似skill结果"""
    print(f"\n{'='*60}")
    print(f"与 '{target_name}' 相似的Skills:")
    print(f"{'='*60}")

    if not similar:
        print("  未找到相似skill（阈值: 0.3）")
        return

    for skill, score in similar:
        bar = "█" * int(score * 20)
        print(f"  {score:.2f} {bar:<20} {skill['name']}")
        # 打印简要描述
        desc = skill.get('description', '')[:60].replace('\n', ' ')
        print(f"       {desc}...")


def print_skill_graph(graph: Dict):
    """打印技能图谱"""
    print(f"\n{'='*60}")
    print("技能关系图谱")
    print(f"{'='*60}")

    print(f"\n节点数: {len(graph['nodes'])}")
    print(f"关系边: {len(graph['edges'])}")

    print("\n技能簇:")
    for cluster_name, skills in graph['clusters'].items():
        print(f"  [{cluster_name}] {len(skills)}个: {', '.join(skills[:5])}")
        if len(skills) > 5:
            print(f"           ... 等{len(skills)-5}个")

    if graph['edges']:
        print("\n强关联 (>0.5相似度):")
        for edge in sorted(graph['edges'], key=lambda x: x['similarity'], reverse=True)[:10]:
            print(f"  {edge['source']} <--{edge['similarity']}--> {edge['target']}")


def main():
    parser = argparse.ArgumentParser(description='Skill发现工具')
    parser.add_argument('--scan-all', action='store_true', help='扫描所有skill')
    parser.add_argument('--target', type=str, help='目标skill名称')
    parser.add_argument('--find-similar', action='store_true', help='查找相似skill')
    parser.add_argument('--build-graph', action='store_true', help='构建技能图谱')
    parser.add_argument('--top-k', type=int, default=5, help='返回相似skill数量')
    parser.add_argument('--threshold', type=float, default=0.3, help='相似度阈值')
    parser.add_argument('--output', type=str, help='输出JSON文件')

    args = parser.parse_args()

    if args.scan_all:
        skills = scan_all_skills()
        print_skill_list(skills)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(skills, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {args.output}")

    elif args.target and args.find_similar:
        all_skills = scan_all_skills()
        target = next((s for s in all_skills if s['name'] == args.target), None)

        if not target:
            print(f"Error: Skill '{args.target}' 未找到")
            print(f"可用skills: {', '.join(s['name'] for s in all_skills[:10])}...")
            return

        similar = find_similar_skills(target, all_skills, args.top_k, args.threshold)
        print_similar_skills(args.target, similar)

    elif args.build_graph:
        skills = scan_all_skills()
        graph = build_skill_graph(skills)
        print_skill_graph(graph)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(graph, f, ensure_ascii=False, indent=2)
            print(f"\n图谱已保存到: {args.output}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
