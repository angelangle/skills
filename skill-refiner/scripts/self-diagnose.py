#!/usr/bin/env python3
"""
self-diagnose.py - Skill Refiner自我诊断工具

本脚本用于skill-refiner的自我检查和改进建议生成。
体现"元能力"的核心：能够识别自身不足并提出改进方案。

Usage:
    python3 self-diagnose.py [--check-list]
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class SelfDiagnoser:
    """自我诊断器"""

    def __init__(self):
        self.skill_path = Path(__file__).parent.parent
        self.findings = []
        self.improvements = []

    def diagnose(self) -> Dict:
        """执行全面自我诊断"""
        print("🔬 Skill Refiner 自我诊断")
        print("=" * 60)
        print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Skill路径: {self.skill_path}")
        print()

        # 各维度自我检查
        meta_capabilities = self._check_meta_capabilities()
        tool_chain = self._check_tool_chain()
        knowledge_base = self._check_knowledge_base()
        self_improvement = self._check_self_improvement()

        return {
            'meta_capabilities': meta_capabilities,
            'tool_chain': tool_chain,
            'knowledge_base': knowledge_base,
            'self_improvement': self_improvement,
            'findings': self.findings,
            'improvements': self.improvements
        }

    def _check_meta_capabilities(self) -> Dict:
        """检查元能力定义"""
        print("🧠 检查元能力定义...")

        skill_md = self.skill_path / 'SKILL.md'
        content = skill_md.read_text()

        checks = {
            'has_self_evolution': '自我进化' in content or 'self-evolution' in content.lower(),
            'has_skill_evolution': 'skill进化' in content or 'skill evolution' in content.lower(),
            'has_research_enhancement': '科研' in content,
            'has_engineering_optimization': '工程' in content,
            'has_network_retrieval': '网络检索' in content or 'websearch' in content.lower(),
        }

        # 评估
        score = sum(checks.values()) / len(checks) * 100

        for capability, present in checks.items():
            if not present:
                self.findings.append({
                    'category': '元能力',
                    'issue': f"缺少或未明确声明: {capability}",
                    'severity': 'warning'
                })
                self.improvements.append(f"在SKILL.md中强化'{capability}'的定义和流程")

        print(f"   元能力覆盖: {sum(checks.values())}/{len(checks)} ({score:.0f}%)")
        return {'checks': checks, 'score': score}

    def _check_tool_chain(self) -> Dict:
        """检查工具链完整性"""
        print("🔧 检查工具链...")

        scripts_dir = self.skill_path / 'scripts'
        expected_tools = {
            'skill-doctor.py': 'Skill诊断工具',
            'desc-optimizer.py': 'Description优化器',
            'research-expander.py': '科研扩展器',
            'self-diagnose.py': '自我诊断工具',
        }

        existing = {}
        for script, desc in expected_tools.items():
            path = scripts_dir / script
            exists = path.exists()
            existing[script] = exists

            if not exists:
                self.findings.append({
                    'category': '工具链',
                    'issue': f"缺少工具: {script} ({desc})",
                    'severity': 'info'
                })
                self.improvements.append(f"创建{script}实现{desc}功能")

        score = sum(existing.values()) / len(existing) * 100
        print(f"   工具完整度: {sum(existing.values())}/{len(existing)} ({score:.0f}%)")
        return {'existing': existing, 'score': score}

    def _check_knowledge_base(self) -> Dict:
        """检查知识库"""
        print("📚 检查知识库...")

        refs_dir = self.skill_path / 'references'

        expected_refs = {
            'meta-capabilities.md': '元能力理论',
            'skill-evolution-patterns.md': 'Skill进化模式',
            'research-methods.md': '科研方法论',
            'engineering-practices.md': '工程实践',
        }

        existing = {}
        for ref, desc in expected_refs.items():
            path = refs_dir / ref
            exists = path.exists()
            existing[ref] = exists

            if not exists:
                self.findings.append({
                    'category': '知识库',
                    'issue': f"缺少参考资料: {ref} ({desc})",
                    'severity': 'info'
                })
                self.improvements.append(f"创建references/{ref}，整合{desc}相关内容")

        # 检查现有references
        existing_refs = list(refs_dir.glob('*.md')) if refs_dir.exists() else []

        score = sum(existing.values()) / len(existing) * 100
        print(f"   知识库覆盖: {len(existing_refs)}文件, 缺失{len(expected_refs) - sum(existing.values())}")
        return {'existing': existing, 'actual_refs': [r.name for r in existing_refs], 'score': score}

    def _check_self_improvement(self) -> Dict:
        """检查自我改进机制"""
        print("🔄 检查自我改进机制...")

        checks = {
            'has_self_check_list': False,
            'has_improvement_log': False,
            'has_version_tracking': False,
        }

        skill_md = self.skill_path / 'SKILL.md'
        content = skill_md.read_text()

        # 检查自检清单
        if '自我诊断' in content or 'self-check' in content.lower():
            checks['has_self_check_list'] = True
        else:
            self.findings.append({
                'category': '自我改进',
                'issue': "缺少定期自我诊断机制",
                'severity': 'info'
            })
            self.improvements.append("添加定期自我诊断清单到SKILL.md")

        # 检查改进日志
        log_file = self.skill_path / 'references' / 'self-improvement-log.md'
        checks['has_improvement_log'] = log_file.exists()
        if not log_file.exists():
            self.findings.append({
                'category': '自我改进',
                'issue': "缺少改进日志文件",
                'severity': 'info'
            })
            self.improvements.append("创建references/self-improvement-log.md记录改进历史")

        # 检查版本追踪
        if '版本' in content or 'Version' in content:
            checks['has_version_tracking'] = True

        score = sum(checks.values()) / len(checks) * 100
        print(f"   自改进机制: {sum(checks.values())}/{len(checks)} ({score:.0f}%)")
        return {'checks': checks, 'score': score}

    def generate_improvement_plan(self) -> str:
        """生成改进计划"""
        plan = []

        plan.append("# Skill Refiner 自我改进计划")
        plan.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        plan.append(f"\n## 诊断摘要")
        plan.append(f"- 发现问题: {len(self.findings)}项")
        plan.append(f"- 改进建议: {len(self.improvements)}项")

        if self.findings:
            plan.append(f"\n## 问题清单")
            for i, finding in enumerate(self.findings, 1):
                plan.append(f"{i}. [{finding['category']}] {finding['issue']}")

        if self.improvements:
            plan.append(f"\n## 改进行动")
            for i, imp in enumerate(self.improvements, 1):
                plan.append(f"{i}. {imp}")

        plan.append("\n## 优先级排序")
        plan.append("### 高优先级")
        high_priority = [f for f in self.findings if f.get('severity') == 'warning']
        if high_priority:
            for f in high_priority:
                plan.append(f"- [ ] {f['issue']}")
        else:
            plan.append("- 无高优先级问题")

        plan.append("\n### 中优先级")
        plan.append("- [ ] 完善工具链脚本")
        plan.append("- [ ] 扩展知识库文档")

        plan.append("\n### 低优先级")
        plan.append("- [ ] 添加更多示例和模板")

        return '\n'.join(plan)

    def print_report(self, results: Dict):
        """打印诊断报告"""
        print("\n" + "=" * 60)
        print("📊 自我诊断报告")
        print("=" * 60)

        # 各维度得分
        print("\n## 维度评分")
        print(f"- 元能力定义: {results['meta_capabilities']['score']:.1f}%")
        print(f"- 工具链完整: {results['tool_chain']['score']:.1f}%")
        print(f"- 知识库覆盖: {results['knowledge_base']['score']:.1f}%")
        print(f"- 自改进机制: {results['self_improvement']['score']:.1f}%")

        overall = (
            results['meta_capabilities']['score'] +
            results['tool_chain']['score'] +
            results['knowledge_base']['score'] +
            results['self_improvement']['score']
        ) / 4
        print(f"\n**综合得分: {overall:.1f}%**")

        if results['findings']:
            print(f"\n## 发现 {len(results['findings'])} 个问题")
            for finding in results['findings']:
                emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(
                    finding.get('severity', 'info'), '•')
                print(f"{emoji} [{finding['category']}] {finding['issue']}")

        # 输出改进计划
        plan = self.generate_improvement_plan()
        print("\n" + "=" * 60)
        print(plan)

        # 保存改进计划
        plan_path = self.skill_path / 'references' / 'improvement-plan.md'
        plan_path.write_text(plan)
        print(f"\n💾 改进计划已保存到: {plan_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Skill Refiner自我诊断')
    parser.add_argument('--check-list', action='store_true',
                       help='仅输出自检清单')
    args = parser.parse_args()

    if args.check_list:
        print("""
# Skill Refiner 定期自检清单

## 每月检查
- [ ] 触发率分析 - 是否经常被正确调用？
- [ ] 覆盖度检查 - 是否遗漏重要维护场景？
- [ ] 逻辑完备性 - 工作流程是否有盲区？
- [ ] 时效性评估 - 方法是否跟上最新实践？
- [ ] 工具链完善 - 辅助脚本是否齐全？
- [ ] 科研深度 - 是否有理论支撑？

## 每季度检查
- [ ] 对比其他meta-skill（如有）
- [ ] 检索技能优化最新方法论
- [ ] 更新和改进工具脚本
- [ ] 扩充知识库
- [ ] 完善自我诊断机制

## 年度检查
- [ ] 全面重构（如有必要）
- [ ] 与其他skill整合评估
        """)
        return

    diagnoser = SelfDiagnoser()
    results = diagnoser.diagnose()
    diagnoser.print_report(results)


if __name__ == '__main__':
    main()
