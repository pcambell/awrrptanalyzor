#!/usr/bin/env python3
"""Test script for Rule Engine"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.analyzer.rule_engine import RuleEngine

def test_rule_loading():
    """Test rule loading from YAML files"""
    print("=" * 60)
    print("测试规则引擎 - 规则加载")
    print("=" * 60)
    print()

    # Initialize rule engine
    rules_dir = Path(__file__).parent / "app" / "rules"
    engine = RuleEngine(str(rules_dir))

    print(f"规则目录: {rules_dir}")
    print(f"总共加载规则数: {len(engine.rules)}")
    print()

    # Group rules by category
    rules_by_category = {}
    for rule in engine.rules:
        category = rule.get('category', 'unknown')
        if category not in rules_by_category:
            rules_by_category[category] = []
        rules_by_category[category].append(rule)

    # Print summary
    print("按类别统计:")
    print("-" * 60)
    for category, rules in sorted(rules_by_category.items()):
        print(f"{category:20s}: {len(rules):2d} 条规则")
    print()

    # Print all rules
    print("规则详情:")
    print("-" * 60)
    for category, rules in sorted(rules_by_category.items()):
        print(f"\n[{category.upper()}]")
        for rule in rules:
            print(f"  - {rule['id']:40s} [{rule['severity']:8s}] {rule['name']}")

    print()
    return engine


def test_rule_evaluation():
    """Test rule evaluation with sample metrics"""
    print()
    print("=" * 60)
    print("测试规则引擎 - 规则评估")
    print("=" * 60)
    print()

    # Initialize rule engine
    rules_dir = Path(__file__).parent / "app" / "rules"
    engine = RuleEngine(str(rules_dir))

    # Sample metrics that should trigger some rules
    sample_metrics = {
        'derived': {
            'cpu_utilization': 85.0,  # Should trigger HIGH_CPU_USAGE
            'buffer_hit_ratio': 85.0,  # Should trigger LOW_BUFFER_HIT_RATIO
        },
        'wait_events': {
            'db_file_sequential_read': {
                'pct_db_time': 35.0  # Should trigger HIGH_DB_FILE_SEQUENTIAL_READ
            },
            'db_file_scattered_read': {
                'pct_db_time': 28.0  # Should trigger HIGH_DB_FILE_SCATTERED_READ
            },
            'log_file_sync': {
                'pct_db_time': 18.0  # Should trigger HIGH_LOG_FILE_SYNC
            }
        },
        'load_profile': {
            'Physical read (blocks)': {
                'per_second': 12000  # Should trigger HIGH_PHYSICAL_READS
            }
        }
    }

    # Evaluate rules
    diagnostics = engine.evaluate(sample_metrics)

    print(f"触发的诊断规则数: {len(diagnostics)}")
    print()

    if diagnostics:
        print("诊断结果:")
        print("-" * 60)
        for i, diag in enumerate(diagnostics, 1):
            print(f"\n{i}. [{diag['severity'].upper()}] {diag['issue_title']}")
            print(f"   规则ID: {diag['rule_id']}")
            print(f"   类别: {diag['category']}")
            print(f"   触发指标: {diag['metric_values']}")
            print(f"   描述: {diag['issue_description'][:100]}...")
            print(f"   建议: {diag['recommendation'][:150]}...")
    else:
        print("未触发任何诊断规则")

    print()


def test_severity_distribution():
    """Test severity distribution of loaded rules"""
    print()
    print("=" * 60)
    print("规则严重性分布")
    print("=" * 60)
    print()

    rules_dir = Path(__file__).parent / "app" / "rules"
    engine = RuleEngine(str(rules_dir))

    severity_count = {}
    for rule in engine.rules:
        severity = rule.get('severity', 'unknown')
        severity_count[severity] = severity_count.get(severity, 0) + 1

    print("严重性统计:")
    print("-" * 60)
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_count.get(severity, 0)
        percentage = (count / len(engine.rules) * 100) if engine.rules else 0
        bar = '█' * int(count / 2)
        print(f"{severity:10s}: {count:2d} ({percentage:5.1f}%) {bar}")

    print()


if __name__ == "__main__":
    try:
        # Windows encoding fix
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

        # Run tests
        test_rule_loading()
        test_rule_evaluation()
        test_severity_distribution()

        print("=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
