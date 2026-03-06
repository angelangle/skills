#!/usr/bin/env python3
"""
Skill Trigger Rate Tester
测试 skill description 的触发效果
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


class TriggerTestSet:
    """触发测试集"""

    def __init__(self):
        self.positive_cases: List[str] = []
        self.negative_cases: List[str] = []

    def add_positive(self, case: str):
        """添加正向用例（应该触发）"""
        self.positive_cases.append(case)

    def add_negative(self, case: str):
        """添加负向用例（不该触发）"""
        self.negative_cases.append(case)

    def load_from_file(self, filepath: str):
        """从文件加载测试集"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.positive_cases = data.get('positive', [])
            self.negative_cases = data.get('negative', [])

    def save_to_file(self, filepath: str):
        """保存测试集到文件"""
        data = {
            'positive': self.positive_cases,
            'negative': self.negative_cases
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


class TriggerAnalyzer:
    """触发分析器"""

    def __init__(self, description: str):
        self.description = description.lower()
        self.keywords = self._extract_keywords()

    def _extract_keywords(self) -> List[str]:
        """提取关键词（简单实现）"""
        # 实际应该使用 NLP，这里用简单分词
        words = self.description.split()
        # 过滤常见词
        stop_words = {'the', 'a', 'an', 'is', 'are', 'for', 'to', 'of', 'and', 'or'}
        return [w for w in words if w not in stop_words and len(w) > 3]

    def analyze_query(self, query: str) -> Dict:
        """分析 query 与 description 的匹配度"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        keyword_set = set(self.keywords)

        matched = query_words & keyword_set
        unmatched_keywords = keyword_set - query_words

        # 简单匹配分数
        if len(keyword_set) > 0:
            score = len(matched) / len(keyword_set)
        else:
            score = 0

        return {
            'query': query,
            'matched_keywords': list(matched),
            'unmatched_keywords': list(unmatched_keywords)[:5],
            'match_score': score,
            'should_trigger': score > 0.3  # 阈值
        }

    def run_test(self, test_set: TriggerTestSet) -> Dict:
        """运行完整测试"""
        results = {
            'positive': [],
            'negative': [],
            'summary': {}
        }

        tp, fp, tn, fn = 0, 0, 0, 0

        # 测试正向用例
        for case in test_set.positive_cases:
            result = self.analyze_query(case)
            results['positive'].append(result)
            if result['should_trigger']:
                tp += 1
            else:
                fn += 1

        # 测试负向用例
        for case in test_set.negative_cases:
            result = self.analyze_query(case)
            results['negative'].append(result)
            if result['should_trigger']:
                fp += 1
            else:
                tn += 1

        # 计算指标
        total_positive = tp + fn
        total_negative = tn + fp

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / total_positive if total_positive > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        results['summary'] = {
            'true_positives': tp,
            'false_positives': fp,
            'true_negatives': tn,
            'false_negatives': fn,
            'precision': round(precision, 2),
            'recall': round(recall, 2),
            'f1_score': round(f1, 2)
        }

        return results


def print_report(results: Dict):
    """打印测试报告"""
    summary = results['summary']

    print("\n" + "="*50)
    print("Trigger Test Report")
    print("="*50)

    print(f"\n📊 Summary")
    print(f"  True Positives:  {summary['true_positives']}")
    print(f"  False Positives: {summary['false_positives']}")
    print(f"  True Negatives:  {summary['true_negatives']}")
    print(f"  False Negatives: {summary['false_negatives']}")

    print(f"\n📈 Metrics")
    print(f"  Precision: {summary['precision']:.2%}")
    print(f"  Recall:    {summary['recall']:.2%}")
    print(f"  F1 Score:  {summary['f1_score']:.2%}")

    # 问题用例
    print(f"\n❌ False Positives (should NOT trigger but did)")
    for r in results['negative']:
        if r['should_trigger']:
            print(f"  - {r['query'][:60]}...")

    print(f"\n❌ False Negatives (should trigger but did NOT)")
    for r in results['positive']:
        if not r['should_trigger']:
            print(f"  - {r['query'][:60]}...")

    print("\n" + "="*50)


def main():
    parser = argparse.ArgumentParser(description='Skill Trigger Tester')
    parser.add_argument('skill_file', help='Path to SKILL.md file')
    parser.add_argument('--test-set', '-t', help='Path to test set JSON file')
    parser.add_argument('--create-sample', '-c', action='store_true',
                        help='Create sample test set')

    args = parser.parse_args()

    # 读取 skill description
    with open(args.skill_file, 'r') as f:
        content = f.read()

    # 简单提取 description（在实际使用中应该解析 YAML）
    desc_start = content.find('description:')
    desc_end = content.find('---', desc_start + 1)
    description = content[desc_start:desc_end]

    # 创建或加载测试集
    test_set = TriggerTestSet()

    if args.create_sample:
        # 创建示例测试集
        test_set.add_positive("How do I optimize database performance?")
        test_set.add_positive("SQL query is running slow")
        test_set.add_positive("Need to tune database indexes")
        test_set.add_negative("How to install MySQL?")
        test_set.add_negative("Backup database to cloud")
        test_set.add_negative("Write a Python script")

        output_file = args.test_set or 'test_set.json'
        test_set.save_to_file(output_file)
        print(f"Created sample test set: {output_file}")
        return

    if args.test_set:
        test_set.load_from_file(args.test_set)
    else:
        print("Error: No test set provided. Use --create-sample to create one.")
        sys.exit(1)

    # 运行测试
    analyzer = TriggerAnalyzer(description)
    results = analyzer.run_test(test_set)

    # 打印报告
    print_report(results)


if __name__ == '__main__':
    main()
