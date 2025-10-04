"""Rule-based Diagnostic Engine"""

import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RuleEngine:
    """Rule-based diagnostic engine for AWR reports"""

    def __init__(self, rules_dir: str):
        """
        Initialize rule engine

        Args:
            rules_dir: Directory containing YAML rule files
        """
        self.rules_dir = Path(rules_dir)
        self.rules: List[Dict] = []
        self._load_rules()

    def _load_rules(self):
        """Load all rules from YAML files"""
        if not self.rules_dir.exists():
            logger.warning(f"Rules directory not found: {self.rules_dir}")
            return

        for rule_file in self.rules_dir.glob("*.yaml"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'rules' in data:
                        self.rules.extend(data['rules'])
                        logger.info(f"Loaded {len(data['rules'])} rules from {rule_file.name}")
            except Exception as e:
                logger.error(f"Failed to load rules from {rule_file}: {e}")

        logger.info(f"Total rules loaded: {len(self.rules)}")

    def evaluate(self, metrics: Dict[str, Any]) -> List[Dict]:
        """
        Evaluate all rules against metrics

        Args:
            metrics: Dictionary of performance metrics

        Returns:
            List of diagnostic results
        """
        results = []

        for rule in self.rules:
            try:
                if self._match_conditions(rule.get('conditions', []), metrics):
                    results.append({
                        'rule_id': rule['id'],
                        'severity': rule['severity'],
                        'category': rule['category'],
                        'issue_title': rule['name'],
                        'issue_description': rule.get('description', ''),
                        'recommendation': rule.get('recommendation', ''),
                        'metric_values': self._extract_metrics(rule, metrics)
                    })
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.get('id')}: {e}")

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        results.sort(key=lambda x: severity_order.get(x['severity'], 999))

        return results

    def _match_conditions(self, conditions: List[Dict], metrics: Dict) -> bool:
        """Check if all conditions match"""
        for condition in conditions:
            metric_value = self._get_nested_value(metrics, condition['metric'])
            threshold = condition['threshold']
            operator = condition['operator']

            if not self._compare(metric_value, operator, threshold):
                return False

        return True

    def _compare(self, value: Any, operator: str, threshold: Any) -> bool:
        """Compare value with threshold using operator"""
        try:
            if operator == '>':
                return float(value) > float(threshold)
            elif operator == '<':
                return float(value) < float(threshold)
            elif operator == '>=':
                return float(value) >= float(threshold)
            elif operator == '<=':
                return float(value) <= float(threshold)
            elif operator == '==':
                return value == threshold
            elif operator == 'in_range':
                return threshold[0] <= float(value) <= threshold[1]
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        except (ValueError, TypeError) as e:
            logger.debug(f"Comparison failed: value={value}, operator={operator}, threshold={threshold}, error={e}")
            return False

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return None
            else:
                return None

        return value

    def _extract_metrics(self, rule: Dict, metrics: Dict) -> Dict:
        """Extract relevant metric values for the rule"""
        result = {}

        for condition in rule.get('conditions', []):
            metric_path = condition['metric']
            value = self._get_nested_value(metrics, metric_path)
            if value is not None:
                result[metric_path] = value

        return result
