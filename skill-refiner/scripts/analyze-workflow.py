#!/usr/bin/env python3
"""
Workflow Analyzer - 执行逻辑分析工具
分析 SKILL.md 中的工作流程，提供优化建议
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


class WorkflowAnalyzer:
    """工作流程分析器"""

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_md = self.skill_path / "SKILL.md"
        self.content = self._load_content()

    def _load_content(self) -> str:
        """加载 SKILL.md 内容"""
        if not self.skill_md.exists():
            print(f"Error: {self.skill_md} not found")
            sys.exit(1)
        return self.skill_md.read_text(encoding='utf-8')

    def analyze_phases(self) -> Dict:
        """分析工作阶段"""
        # 查找阶段/phase 标记
        phase_patterns = [
            r'##\s*(?:Phase|阶段)\s*(\d+)[\s:：]*(\w+)',
            r'###\s*(?:Phase|阶段)\s*(\d+)[\s:：]*(\w+)',
            r'##\s*(\d+)\.\s*(\w+)',
            r'###\s*步骤\s*(\d+)[\s:：]*(\w+)',
        ]

        phases = []
        for pattern in phase_patterns:
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            for match in matches:
                phases.append({
                    'num': match.group(1),
                    'name': match.group(2),
                    'position': match.start()
                })

        return {
            'count': len(phases),
            'phases': sorted(phases, key=lambda x: x['position'])
        }

    def analyze_checklists(self) -> Dict:
        """分析检查清单"""
        # 查找 - [ ] 或 - [x] 标记
        checklist_pattern = r'[-*]\s*\[([ x])\]\s*(.+)'
        matches = re.finditer(checklist_pattern, self.content)

        items = []
        for match in matches:
            items.append({
                'checked': match.group(1) == 'x',
                'text': match.group(2).strip()
            })

        checked = sum(1 for item in items if item['checked'])

        return {
            'total': len(items),
            'checked': checked,
            'unchecked': len(items) - checked,
            'items': items
        }

    def analyze_decisions(self) -> Dict:
        """分析决策分支"""
        # 查找条件语句
        decision_patterns = [
            r'(?:如果|if|假如)\s*[:：]',
            r'(?:否则|else|不然)\s*[:：]',
            r'(?:根据|依据)\s*.+?[:：]',
            r'(?:分支|条件)\s*[:：]',
        ]

        decisions = []
        for pattern in decision_patterns:
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            for match in matches:
                # 获取上下文
                start = max(0, match.start() - 50)
                end = min(len(self.content), match.end() + 50)
                context = self.content[start:end].replace('\n', ' ')
                decisions.append({
                    'pattern': pattern,
                    'context': context.strip()
                })

        return {
            'count': len(decisions),
            'decisions': decisions[:10]  # 限制数量
        }

    def analyze_examples(self) -> Dict:
        """分析示例数量"""
        # 查找示例标记
        example_patterns = [
            r'##\s*示例',
            r'###\s*示例',
            r'##\s*Example',
            r'###\s*Example',
            r'```\w*\n',  # 代码块
        ]

        examples = []
        for pattern in example_patterns:
            matches = re.finditer(pattern, self.content, re.IGNORECASE)
            examples.extend(matches)

        # 统计代码块
        code_blocks = re.findall(r'```[\s\S]*?```', self.content)

        return {
            'example_sections': len(examples),
            'code_blocks': len(code_blocks)
        }

    def analyze_references(self) -> Dict:
        """分析参考资料"""
        refs_dir = self.skill_path / "references"

        if not refs_dir.exists():
            return {'exists': False, 'files': []}

        files = list(refs_dir.glob('*.md'))

        return {
            'exists': True,
            'count': len(files),
            'files': [f.name for f in files]
        }

    def analyze_completeness(self) -> Dict:
        """分析完整性"""
        checks = {
            'has_workflow': bool(re.search(r'(?:workflow|工作流程|执行流程)', self.content, re.I)),
            'has_examples': bool(re.search(r'(?:example|示例|例子)', self.content, re.I)),
            'has_error_handling': bool(re.search(r'(?:error|错误|异常|exception)', self.content, re.I)),
            'has_output_spec': bool(re.search(r'(?:output|输出|规范|spec)', self.content, re.I)),
            'has_checklist': bool(re.search(r'- \[', self.content)),
            'has_references_section': bool(re.search(r'(?:reference|参考|资料)', self.content, re.I)),
        }

        score = sum(checks.values()) / len(checks) * 100

        return {
            'checks': checks,
            'score': round(score, 1)
        }

    def generate_report(self) -> str:
        """生成分析报告"""
        phases = self.analyze_phases()
        checklists = self.analyze_checklists()
        decisions = self.analyze_decisions()
        examples = self.analyze_examples()
        references = self.analyze_references()
        completeness = self.analyze_completeness()

        report = f"""
{'='*60}
Skill Workflow Analysis Report
{'='*60}

Skill: {self.skill_path.name}

📊 Completeness Score: {completeness['score']}/100

Basic Elements:
  ✓ Workflow defined:     {completeness['checks']['has_workflow']}
  ✓ Examples included:    {completeness['checks']['has_examples']}
  ✓ Error handling:       {completeness['checks']['has_error_handling']}
  ✓ Output specification: {completeness['checks']['has_output_spec']}
  ✓ Checklist present:    {completeness['checks']['has_checklist']}
  ✓ References section:   {completeness['checks']['has_references_section']}

🔢 Statistics:
  - Workflow phases: {phases['count']}
  - Checklist items: {checklists['total']} ({checklists['checked']} checked)
  - Decision points: {decisions['count']}
  - Code examples:   {examples['code_blocks']}
  - Reference files: {references['count']}

📁 References Directory:
  - Exists: {references['exists']}
"""

        if references['files']:
            report += "  - Files:\n"
            for f in references['files']:
                report += f"    • {f}\n"

        # 建议
        report += "\n💡 Suggestions:\n"

        if completeness['score'] < 60:
            report += "  ⚠️  Completeness score is low. Consider adding:\n"
            for key, value in completeness['checks'].items():
                if not value:
                    report += f"     - {key.replace('has_', '').replace('_', ' ').title()}\n"

        if phases['count'] < 2:
            report += "  ⚠️  Workflow phases unclear. Consider defining clear phases.\n"

        if examples['code_blocks'] < 3:
            report += "  ⚠️  Few code examples. Consider adding more examples.\n"

        if not references['exists'] or references['count'] == 0:
            report += "  ⚠️  No references directory. Consider creating one with docs.\n"

        if decisions['count'] < 2:
            report += "  ⚠️  Few decision branches. Consider adding conditional logic.\n"

        report += "\n" + "="*60 + "\n"

        return report


def main():
    parser = argparse.ArgumentParser(description='Skill Workflow Analyzer')
    parser.add_argument('skill_path', help='Path to skill directory')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output as JSON')

    args = parser.parse_args()

    analyzer = WorkflowAnalyzer(args.skill_path)

    if args.json:
        import json
        result = {
            'phases': analyzer.analyze_phases(),
            'checklists': analyzer.analyze_checklists(),
            'decisions': analyzer.analyze_decisions(),
            'examples': analyzer.analyze_examples(),
            'references': analyzer.analyze_references(),
            'completeness': analyzer.analyze_completeness()
        }
        print(json.dumps(result, indent=2))
    else:
        print(analyzer.generate_report())


if __name__ == '__main__':
    main()
