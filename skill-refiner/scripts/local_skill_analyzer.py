#!/usr/bin/env python3
"""
本地 Skill 文档分析器 - NotebookLM 的平替
使用 Claude 原生文件读取能力
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict


class LocalSkillAnalyzer:
    """本地 skill 文档分析器 - 无需外部认证"""
    
    def __init__(self, skills_base_dir: Path = None):
        self.skills_base_dir = skills_base_dir or Path.home() / ".claude" / "skills"
        
    def analyze_skill(self, skill_name: str) -> Dict:
        """分析单个 skill"""
        skill_path = self.skills_base_dir / skill_name
        skill_md = skill_path / "SKILL.md"
        
        if not skill_md.exists():
            return {"error": f"Skill {skill_name} not found"}
        
        content = skill_md.read_text(encoding='utf-8')
        
        return {
            "skill_name": skill_name,
            "path": str(skill_path),
            "analysis_ready": True,
            "content_stats": {
                "total_lines": len(content.split('\n')),
                "total_chars": len(content),
                "sections": self._count_sections(content),
                "code_blocks": content.count('```'),
            },
            "structure": self._extract_structure(content),
            "suggested_questions": self._generate_questions(skill_name, content),
            "claude_commands": self._generate_claude_commands(skill_name, skill_path)
        }
    
    def _count_sections(self, content: str) -> int:
        """统计章节数"""
        return sum(1 for line in content.split('\n') if line.startswith('#'))
    
    def _extract_structure(self, content: str) -> List[Dict]:
        """提取文档结构"""
        sections = []
        current_section = None
        
        for line in content.split('\n'):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.strip('# ')
                sections.append({
                    "level": level,
                    "title": title,
                    "line": line
                })
        
        return sections[:20]  # 前20个章节
    
    def _generate_questions(self, skill_name: str, content: str) -> List[str]:
        """生成建议询问 Claude 的问题"""
        return [
            f"分析 {skill_name} 的 frontmatter 描述质量",
            f"{skill_name} 的触发关键词覆盖是否完整？",
            f"{skill_name} 的章节结构是否合理？",
            f"与同类 skill 相比，{skill_name} 有哪些独特能力？",
            f"{skill_name} 有哪些可以改进的地方？",
        ]
    
    def _generate_claude_commands(self, skill_name: str, skill_path: Path) -> List[str]:
        """生成可直接使用的 Claude 命令"""
        return [
            f"Read {skill_path}/SKILL.md",
            f"分析 {skill_name} 的结构完整性和可改进点",
            f"对比 {skill_name} 和其他相似 skill 的差异",
        ]
    
    def compare_skills(self, skill_names: List[str]) -> Dict:
        """对比多个 skill"""
        analyses = {}
        for name in skill_names:
            analyses[name] = self.analyze_skill(name)
        
        return {
            "comparison_ready": True,
            "skills_analyzed": list(analyses.keys()),
            "claude_prompt": self._generate_comparison_prompt(skill_names),
            "analyses": analyses
        }
    
    def _generate_comparison_prompt(self, skill_names: List[str]) -> str:
        """生成对比分析的 Claude prompt"""
        paths = [f"~/.claude/skills/{name}/SKILL.md" for name in skill_names]
        return f"请对比分析以下 skill 的能力差异：\n" + "\n".join([f"- {p}" for p in paths])


def main():
    parser = argparse.ArgumentParser(description='本地 Skill 文档分析器')
    parser.add_argument('--skill', '-s', help='要分析的 skill 名称')
    parser.add_argument('--compare', '-c', nargs='+', help='对比多个 skill')
    parser.add_argument('--output', '-o', help='输出 JSON 文件')
    
    args = parser.parse_args()
    
    analyzer = LocalSkillAnalyzer()
    
    if args.compare:
        result = analyzer.compare_skills(args.compare)
    elif args.skill:
        result = analyzer.analyze_skill(args.skill)
    else:
        print("请指定 --skill 或 --compare")
        return
    
    # 美化输出
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
