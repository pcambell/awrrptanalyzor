# Oracle AWR 报告分析软件 - 技术设计文档

**文档版本**: v1.0
**创建日期**: 2025-10-02
**项目名称**: AWR Report Analyzer

---

## 1. 技术架构设计

### 1.1 整体架构

采用**前后端分离 + 微服务化**架构:

```
┌─────────────────────────────────────────────────────┐
│              前端层 (React SPA)                      │
│  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │  上传管理    │  │  报告分析   │  │  对比导出   ││
│  └──────────────┘  └─────────────┘  └─────────────┘│
└─────────────────────┬───────────────────────────────┘
                      │ REST API (HTTPS)
┌─────────────────────▼───────────────────────────────┐
│            API 网关 (Nginx)                          │
│  - SSL 终端                                          │
│  - 反向代理                                          │
│  - 负载均衡                                          │
│  - 静态资源服务                                      │
└─────────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼─────────┐  ┌───▼──────────┐  ┌──▼────────────┐
│  Web API    │  │  解析服务    │  │  分析服务     │
│  服务       │  │  (Worker)    │  │  (Worker)     │
│  (FastAPI)  │  │  (Celery)    │  │  (Celery)     │
└───┬─────────┘  └───┬──────────┘  └──┬────────────┘
    │                │                 │
    └────────────────┼─────────────────┘
                     │
    ┌────────────────┼─────────────────┐
    │                │                 │
┌───▼──────┐   ┌────▼─────┐     ┌────▼──────┐
│PostgreSQL│   │  Redis   │     │  MinIO    │
│ (元数据) │   │  (缓存+  │     │ (对象存储)│
│          │   │  消息队列)│     │           │
└──────────┘   └──────────┘     └───────────┘
```

### 1.2 技术栈选型

#### 1.2.1 后端技术栈

| 技术 | 版本 | 用途 | 选择理由 |
|-----|------|------|---------|
| Python | 3.11+ | 核心开发语言 | 数据处理优势、生态丰富 |
| FastAPI | 0.104+ | Web 框架 | 高性能异步、自动文档生成 |
| Pydantic | 2.0+ | 数据验证 | 类型安全、自动校验 |
| SQLAlchemy | 2.0+ | ORM | 成熟的 ORM、支持 asyncio |
| Alembic | 1.12+ | 数据库迁移 | SQLAlchemy 官方迁移工具 |
| Celery | 5.3+ | 异步任务队列 | 成熟稳定、支持多种 broker |
| BeautifulSoup4 | 4.12+ | HTML 解析 | 容错性强、API 简洁 |
| lxml | 4.9+ | XML/HTML 解析 | 高性能、XPath 支持 |
| Pandas | 2.0+ | 数据处理 | 强大的数据分析能力 |
| NumPy | 1.24+ | 数值计算 | 科学计算基础库 |
| SciPy | 1.11+ | 统计分析 | 趋势分析、异常检测 |
| WeasyPrint | 60+ | PDF 生成 | HTML 转 PDF、样式保留 |
| openpyxl | 3.1+ | Excel 生成 | xlsx 格式、样式支持 |
| Jinja2 | 3.1+ | 模板引擎 | 报告模板渲染 |
| PyYAML | 6.0+ | 配置管理 | 规则库配置文件 |
| python-jose | 3.3+ | JWT 认证 | Token 认证 (Phase 2) |
| passlib | 1.7+ | 密码加密 | 安全的密码哈希 (Phase 2) |

#### 1.2.2 前端技术栈

| 技术 | 版本 | 用途 | 选择理由 |
|-----|------|------|---------|
| React | 18.2+ | UI 框架 | 组件化、生态成熟 |
| TypeScript | 5.0+ | 类型系统 | 类型安全、可维护性 |
| Ant Design | 5.0+ | UI 组件库 | 企业级、组件丰富 |
| Ant Design Pro | 5.0+ | 管理后台框架 | 开箱即用的后台方案 |
| ECharts | 5.4+ | 图表库 | 功能强大、性能优异 |
| Axios | 1.6+ | HTTP 客户端 | 易用、拦截器支持 |
| SWR | 2.2+ | 数据获取 | 缓存、自动重新验证 |
| Zustand | 4.4+ | 状态管理 | 轻量、易用 |
| React Router | 6.20+ | 路由管理 | 官方路由方案 |
| Vite | 5.0+ | 构建工具 | 快速热更新、现代化 |

#### 1.2.3 数据存储

| 技术 | 版本 | 用途 | 选择理由 |
|-----|------|------|---------|
| PostgreSQL | 14+ | 主数据库 | JSONB 支持、高级查询 |
| Redis | 7+ | 缓存 + 消息队列 | 高性能、多数据结构 |
| MinIO | 2023.11+ | 对象存储 (可选) | S3 兼容、私有部署 |

#### 1.2.4 运维监控

| 技术 | 版本 | 用途 |
|-----|------|------|
| Docker | 20.10+ | 容器化 |
| Docker Compose | 2.0+ | 本地开发编排 |
| Nginx | 1.24+ | 反向代理、负载均衡 |
| Prometheus | 2.47+ | 指标监控 (Phase 3) |
| Grafana | 10.2+ | 可视化监控 (Phase 3) |

### 1.3 系统部署架构

#### 1.3.1 开发环境

```yaml
docker-compose.dev.yml:
  - frontend (Vite Dev Server: 3000)
  - backend (FastAPI Uvicorn: 8000)
  - celery_worker (Celery Worker)
  - postgres (5432)
  - redis (6379)
```

#### 1.3.2 生产环境

```
┌────────────────────────────────────┐
│        负载均衡器 (Nginx)          │
│     (SSL, 反向代理, 静态资源)      │
└────────┬──────────────┬────────────┘
         │              │
    ┌────▼────┐    ┌───▼─────┐
    │FastAPI-1│    │FastAPI-2│  (Gunicorn + Uvicorn Workers)
    └────┬────┘    └───┬─────┘
         │             │
    ┌────▼─────────────▼────┐
    │  PostgreSQL (Primary) │
    │  └──> Standby (可选)  │
    └───────────────────────┘
         │             │
    ┌────▼────┐   ┌───▼──────┐
    │ Redis   │   │  MinIO   │
    │(Sentinel│   │ (可选)   │
    │  模式)  │   │          │
    └─────────┘   └──────────┘
```

---

## 2. 核心模块设计

### 2.1 后端模块设计

#### 2.1.1 项目目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── dependencies.py         # 依赖注入
│   │
│   ├── api/                    # API 路由
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── reports.py      # 报告管理 API
│   │   │   ├── analysis.py     # 分析 API
│   │   │   ├── comparison.py   # 对比 API
│   │   │   ├── export.py       # 导出 API
│   │   │   └── tasks.py        # 任务监控 API
│   │
│   ├── core/                   # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── parser/             # AWR 解析模块
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # 基础解析器
│   │   │   ├── factory.py      # 解析器工厂
│   │   │   ├── version_detector.py
│   │   │   ├── oracle11g.py
│   │   │   ├── oracle12c.py
│   │   │   ├── oracle19c.py
│   │   │   └── utils.py        # 解析工具函数
│   │   │
│   │   ├── analyzer/           # 分析引擎
│   │   │   ├── __init__.py
│   │   │   ├── metrics_calculator.py
│   │   │   ├── rule_engine.py
│   │   │   ├── anomaly_detector.py
│   │   │   └── recommendation.py
│   │   │
│   │   ├── comparison/         # 对比引擎
│   │   │   ├── __init__.py
│   │   │   ├── comparator.py
│   │   │   └── trend_analyzer.py
│   │   │
│   │   └── exporter/           # 导出模块
│   │       ├── __init__.py
│   │       ├── pdf_exporter.py
│   │       ├── excel_exporter.py
│   │       └── templates/      # 导出模板
│   │
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── database.py         # 数据库连接
│   │   ├── awr_report.py
│   │   ├── performance_metric.py
│   │   ├── diagnostic_result.py
│   │   └── comparison_result.py
│   │
│   ├── schemas/                # Pydantic 模式
│   │   ├── __init__.py
│   │   ├── report.py
│   │   ├── metric.py
│   │   ├── diagnostic.py
│   │   └── comparison.py
│   │
│   ├── services/               # 业务服务层
│   │   ├── __init__.py
│   │   ├── file_service.py
│   │   ├── parse_service.py
│   │   ├── analysis_service.py
│   │   ├── comparison_service.py
│   │   └── export_service.py
│   │
│   ├── tasks/                  # Celery 任务
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── parse_tasks.py
│   │   └── export_tasks.py
│   │
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── cache.py
│   │   └── logging.py
│   │
│   └── rules/                  # 诊断规则库
│       ├── cpu_rules.yaml
│       ├── memory_rules.yaml
│       ├── io_rules.yaml
│       ├── sql_rules.yaml
│       └── wait_event_rules.yaml
│
├── tests/                      # 测试
│   ├── unit/
│   ├── integration/
│   └── fixtures/               # 测试用 AWR 样本
│
├── migrations/                 # 数据库迁移
│   └── versions/
│
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── pytest.ini
├── .env.example
└── Dockerfile
```

#### 2.1.2 核心类设计

##### AWR 解析器设计

```python
# app/core/parser/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from bs4 import BeautifulSoup

class BaseAWRParser(ABC):
    """AWR 解析器基类"""

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.data: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        """主解析入口"""
        self.data = {
            'instance_info': self._parse_instance_info(),
            'snapshot_info': self._parse_snapshot_info(),
            'load_profile': self._parse_load_profile(),
            'wait_events': self._parse_wait_events(),
            'top_sql': self._parse_top_sql(),
            'memory_stats': self._parse_memory_stats(),
            'io_stats': self._parse_io_stats(),
            'instance_efficiency': self._parse_instance_efficiency(),
        }
        return self.data

    @abstractmethod
    def _parse_instance_info(self) -> Dict[str, Any]:
        """解析实例信息 (子类实现)"""
        pass

    @abstractmethod
    def _parse_load_profile(self) -> Dict[str, Any]:
        """解析 Load Profile (子类实现)"""
        pass

    # ... 其他抽象方法

    def _find_table_by_header(self, header_text: str):
        """通用表格定位方法"""
        # 策略 1: 通过 th 文本
        for th in self.soup.find_all('th'):
            if header_text in th.get_text():
                return th.find_parent('table')

        # 策略 2: 通过 a 标签锚点
        for a in self.soup.find_all('a', attrs={'name': True}):
            if header_text.lower() in a['name'].lower():
                return a.find_next('table')

        return None

    def _parse_value(self, text: str) -> float:
        """解析带单位的数值"""
        import re
        text = text.strip().replace(',', '')

        if '%' in text:
            return float(text.replace('%', ''))

        multipliers = {'K': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12}
        for suffix, mult in multipliers.items():
            if text.endswith(suffix):
                return float(text[:-1]) * mult

        # 时间格式 HH:MM:SS.ms
        if ':' in text:
            parts = text.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)

        return float(text)


# app/core/parser/oracle19c.py
class Oracle19cParser(BaseAWRParser):
    """Oracle 19c AWR 解析器"""

    def _parse_instance_info(self) -> Dict[str, Any]:
        # 查找包含 "DB Name" 的表格
        table = self._find_table_by_header("DB Name")
        if not table:
            raise ValueError("无法找到实例信息表格")

        rows = table.find_all('tr')
        info = {}

        # 提取关键信息
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text().strip()
                value = cells[1].get_text().strip()

                if 'DB Name' in key:
                    info['db_name'] = value
                elif 'Instance' in key:
                    info['instance_name'] = value
                elif 'Host' in key:
                    info['host_name'] = value
                # ... 更多字段

        return info

    def _parse_load_profile(self) -> Dict[str, Any]:
        table = self._find_table_by_header("Load Profile")
        if not table:
            return {}

        profile = {}
        rows = table.find_all('tr')[1:]  # 跳过表头

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                metric_name = cells[0].get_text().strip()
                per_second = self._parse_value(cells[1].get_text())
                per_txn = self._parse_value(cells[2].get_text())

                profile[metric_name] = {
                    'per_second': per_second,
                    'per_txn': per_txn
                }

        return profile

    # ... 实现其他方法


# app/core/parser/factory.py
class AWRParserFactory:
    """解析器工厂"""

    @staticmethod
    def create_parser(html_content: str) -> BaseAWRParser:
        version = detect_oracle_version(html_content)

        if version.startswith('11'):
            return Oracle11gParser(html_content)
        elif version.startswith('12'):
            return Oracle12cParser(html_content)
        elif version.startswith('19') or version.startswith('21'):
            return Oracle19cParser(html_content)
        else:
            raise ValueError(f"不支持的 Oracle 版本: {version}")


def detect_oracle_version(html_content: str) -> str:
    """检测 Oracle 版本"""
    soup = BeautifulSoup(html_content, 'lxml')

    # 策略 1: 查找版本号文本
    for tag in soup.find_all(['td', 'th', 'p']):
        text = tag.get_text()
        match = re.search(r'Release (\d+\.\d+\.\d+)', text)
        if match:
            return match.group(1)

    # 策略 2: 根据特征判断
    if soup.find(text=re.compile('Pluggable Database')):
        return '12.1.0'  # 12c+ 特征

    return '19.0.0'  # 默认最新版本
```

##### 分析引擎设计

```python
# app/core/analyzer/rule_engine.py
from typing import List, Dict, Any
import yaml

class RuleEngine:
    """规则引擎"""

    def __init__(self, rules_dir: str):
        self.rules = self._load_rules(rules_dir)

    def _load_rules(self, rules_dir: str) -> List[Dict]:
        """加载所有规则"""
        import glob
        import os

        rules = []
        for rule_file in glob.glob(os.path.join(rules_dir, '*.yaml')):
            with open(rule_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                rules.extend(data.get('rules', []))

        return rules

    def evaluate(self, metrics: Dict[str, Any]) -> List[Dict]:
        """评估规则,返回诊断结果"""
        results = []

        for rule in self.rules:
            if self._match_conditions(rule['conditions'], metrics):
                results.append({
                    'rule_id': rule['id'],
                    'severity': rule['severity'],
                    'category': rule['category'],
                    'title': rule['name'],
                    'description': rule['description'],
                    'recommendation': rule['recommendation'],
                    'metric_values': self._extract_metrics(rule, metrics)
                })

        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        results.sort(key=lambda x: severity_order[x['severity']])

        return results

    def _match_conditions(self, conditions: List[Dict], metrics: Dict) -> bool:
        """检查条件是否匹配"""
        for cond in conditions:
            metric_value = self._get_nested_metric(metrics, cond['metric'])
            threshold = cond['threshold']
            operator = cond['operator']

            if not self._compare(metric_value, operator, threshold):
                return False

        return True

    def _compare(self, value: float, operator: str, threshold: float) -> bool:
        """比较操作"""
        ops = {
            '>': lambda v, t: v > t,
            '<': lambda v, t: v < t,
            '>=': lambda v, t: v >= t,
            '<=': lambda v, t: v <= t,
            '==': lambda v, t: v == t,
            'in_range': lambda v, t: t[0] <= v <= t[1]
        }
        return ops[operator](value, threshold)

    def _get_nested_metric(self, metrics: Dict, path: str):
        """获取嵌套指标 (如 'load_profile.cpu_time')"""
        keys = path.split('.')
        value = metrics
        for key in keys:
            value = value.get(key, 0)
        return value

    def _extract_metrics(self, rule: Dict, metrics: Dict) -> Dict:
        """提取相关指标值"""
        result = {}
        for cond in rule['conditions']:
            metric_path = cond['metric']
            result[metric_path] = self._get_nested_metric(metrics, metric_path)
        return result


# app/core/analyzer/metrics_calculator.py
class MetricsCalculator:
    """指标计算器"""

    @staticmethod
    def calculate_derived_metrics(raw_metrics: Dict) -> Dict:
        """计算衍生指标"""
        derived = {}

        # CPU 使用率
        if 'db_time' in raw_metrics and 'cpu_time' in raw_metrics:
            db_time = raw_metrics['db_time']
            cpu_time = raw_metrics['cpu_time']
            derived['cpu_utilization'] = (cpu_time / db_time * 100) if db_time > 0 else 0

        # Buffer Cache 命中率
        if 'logical_reads' in raw_metrics and 'physical_reads' in raw_metrics:
            logical = raw_metrics['logical_reads']
            physical = raw_metrics['physical_reads']
            derived['buffer_hit_ratio'] = (1 - physical / logical) * 100 if logical > 0 else 0

        # 平均活跃会话数
        if 'db_time' in raw_metrics and 'elapsed_time' in raw_metrics:
            db_time_sec = raw_metrics['db_time'] / 1e6
            elapsed = raw_metrics['elapsed_time']
            derived['avg_active_sessions'] = db_time_sec / elapsed if elapsed > 0 else 0

        # 硬解析率
        if 'parse_count_hard' in raw_metrics and 'parse_count_total' in raw_metrics:
            hard = raw_metrics['parse_count_hard']
            total = raw_metrics['parse_count_total']
            derived['hard_parse_ratio'] = (hard / total * 100) if total > 0 else 0

        return derived
```

##### 数据模型设计

```python
# app/models/awr_report.py
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"

class AWRReport(Base):
    __tablename__ = "awr_reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(BigInteger)
    upload_time = Column(DateTime, default=datetime.utcnow)

    # 实例信息
    oracle_version = Column(String(50))
    db_name = Column(String(100), index=True)
    instance_name = Column(String(100))
    host_name = Column(String(100))

    # 快照信息
    snapshot_begin = Column(DateTime, index=True)
    snapshot_end = Column(DateTime)
    snapshot_interval = Column(Integer)  # 分钟

    # 状态
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    metrics = relationship("PerformanceMetric", back_populates="report", cascade="all, delete-orphan")
    diagnostics = relationship("DiagnosticResult", back_populates="report", cascade="all, delete-orphan")


# app/models/performance_metric.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("awr_reports.id"), nullable=False, index=True)

    # 指标分类
    metric_category = Column(String(50), nullable=False, index=True)
    # load_profile, wait_events, sql_stats, io_stats, memory_stats, instance_efficiency

    # 灵活存储不同版本的数据
    metric_data = Column(JSONB, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    report = relationship("AWRReport", back_populates="metrics")


# app/models/diagnostic_result.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base

class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DiagnosticResult(Base):
    __tablename__ = "diagnostic_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("awr_reports.id"), nullable=False, index=True)

    rule_id = Column(String(50), nullable=False)
    severity = Column(Enum(Severity), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # cpu, io, memory, sql, wait_event

    issue_title = Column(String(255), nullable=False)
    issue_description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)

    metric_values = Column(JSONB)  # 相关指标值

    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    report = relationship("AWRReport", back_populates="diagnostics")
```

##### API 路由设计

```python
# app/api/v1/reports.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.dependencies import get_db
from app.schemas.report import ReportResponse, ReportListResponse, ReportDetail
from app.services.file_service import FileService
from app.tasks.parse_tasks import parse_awr_report_task

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/upload", response_model=ReportResponse)
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传 AWR 报告"""

    # 文件校验
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="仅支持 HTML 文件")

    if file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    # 保存文件
    file_service = FileService(db)
    report = await file_service.save_uploaded_file(file)

    # 触发异步解析任务
    task = parse_awr_report_task.delay(report.id)

    return {
        "id": report.id,
        "filename": report.filename,
        "status": report.status,
        "task_id": task.id
    }


@router.get("", response_model=ReportListResponse)
def list_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取报告列表"""

    file_service = FileService(db)
    total, reports = file_service.list_reports(
        page=page,
        size=size,
        db_name=db_name,
        date_from=date_from,
        date_to=date_to
    )

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": reports
    }


@router.get("/{report_id}", response_model=ReportDetail)
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取报告详情"""

    file_service = FileService(db)
    report = file_service.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """删除报告"""

    file_service = FileService(db)
    success = file_service.delete_report(report_id)

    if not success:
        raise HTTPException(status_code=404, detail="报告不存在")

    return {"message": "删除成功"}


# app/api/v1/analysis.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.diagnostic import DiagnosticResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/reports", tags=["analysis"])

@router.post("/{report_id}/analyze")
def analyze_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """触发报告分析"""

    analysis_service = AnalysisService(db)
    task_id = analysis_service.analyze_report(report_id)

    return {"task_id": task_id, "message": "分析任务已启动"}


@router.get("/{report_id}/diagnostics", response_model=DiagnosticResponse)
def get_diagnostics(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取诊断结果"""

    analysis_service = AnalysisService(db)
    diagnostics = analysis_service.get_diagnostics(report_id)

    return {
        "report_id": report_id,
        "diagnostics": diagnostics
    }


@router.get("/{report_id}/metrics/{category}")
def get_metrics(
    report_id: int,
    category: str,
    db: Session = Depends(get_db)
):
    """获取指定类别的性能指标"""

    analysis_service = AnalysisService(db)
    metrics = analysis_service.get_metrics(report_id, category)

    if not metrics:
        raise HTTPException(status_code=404, detail="未找到指标数据")

    return metrics
```

##### Celery 任务设计

```python
# app/tasks/celery_app.py
from celery import Celery

from app.config import settings

celery_app = Celery(
    "awrrptanalyzor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.tasks.parse_tasks.*": {"queue": "parse"},
    "app.tasks.export_tasks.*": {"queue": "export"}
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 分钟超时
)


# app/tasks/parse_tasks.py
from celery import Task
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.awr_report import AWRReport, ReportStatus
from app.core.parser.factory import AWRParserFactory
from app.models.performance_metric import PerformanceMetric

class DatabaseTask(Task):
    """自动管理数据库会话的任务基类"""
    _db: Session = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(base=DatabaseTask, bind=True)
def parse_awr_report_task(self, report_id: int):
    """解析 AWR 报告任务"""

    db = self.db

    # 更新状态为 parsing
    report = db.query(AWRReport).filter(AWRReport.id == report_id).first()
    if not report:
        raise ValueError(f"报告不存在: {report_id}")

    report.status = ReportStatus.PARSING
    db.commit()

    try:
        # 读取文件
        with open(report.file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 创建解析器并解析
        parser = AWRParserFactory.create_parser(html_content)
        parsed_data = parser.parse()

        # 更新报告元数据
        instance_info = parsed_data['instance_info']
        snapshot_info = parsed_data['snapshot_info']

        report.oracle_version = instance_info.get('oracle_version')
        report.db_name = instance_info.get('db_name')
        report.instance_name = instance_info.get('instance_name')
        report.host_name = instance_info.get('host_name')
        report.snapshot_begin = snapshot_info.get('begin_time')
        report.snapshot_end = snapshot_info.get('end_time')
        report.snapshot_interval = snapshot_info.get('interval')

        # 存储性能指标
        for category, data in parsed_data.items():
            if category in ['instance_info', 'snapshot_info']:
                continue

            metric = PerformanceMetric(
                report_id=report.id,
                metric_category=category,
                metric_data=data
            )
            db.add(metric)

        # 更新状态为 parsed
        report.status = ReportStatus.PARSED
        db.commit()

        return {"status": "success", "report_id": report_id}

    except Exception as e:
        # 更新状态为 failed
        report.status = ReportStatus.FAILED
        report.error_message = str(e)
        db.commit()

        raise
```

### 2.2 前端模块设计

#### 2.2.1 项目目录结构

```
frontend/
├── src/
│   ├── assets/              # 静态资源
│   ├── components/          # 通用组件
│   │   ├── FileUpload/
│   │   ├── ReportCard/
│   │   ├── DiagnosticCard/
│   │   └── ComparisonChart/
│   │
│   ├── pages/               # 页面组件
│   │   ├── Home/
│   │   ├── ReportList/
│   │   ├── ReportDetail/
│   │   ├── Diagnostic/
│   │   ├── Comparison/
│   │   └── Export/
│   │
│   ├── services/            # API 服务
│   │   ├── api.ts           # Axios 配置
│   │   ├── reportService.ts
│   │   ├── analysisService.ts
│   │   └── exportService.ts
│   │
│   ├── stores/              # 状态管理 (Zustand)
│   │   ├── reportStore.ts
│   │   └── userStore.ts
│   │
│   ├── types/               # TypeScript 类型
│   │   ├── report.ts
│   │   ├── metric.ts
│   │   └── diagnostic.ts
│   │
│   ├── utils/               # 工具函数
│   │   ├── format.ts
│   │   └── chart.ts
│   │
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useReports.ts
│   │   └── useDiagnostics.ts
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── routes.tsx
│
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
```

#### 2.2.2 核心组件设计

```typescript
// src/types/report.ts
export interface AWRReport {
  id: number;
  filename: string;
  file_size: number;
  upload_time: string;
  oracle_version?: string;
  db_name: string;
  instance_name: string;
  host_name?: string;
  snapshot_begin: string;
  snapshot_end: string;
  snapshot_interval: number;
  status: 'pending' | 'parsing' | 'parsed' | 'failed';
  error_message?: string;
}

export interface MetricData {
  [key: string]: any;
}

export interface DiagnosticResult {
  id: number;
  rule_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  issue_title: string;
  issue_description: string;
  recommendation: string;
  metric_values: Record<string, number>;
}


// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加 Token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 统一错误处理
    if (error.response?.status === 401) {
      // 跳转登录
    }
    return Promise.reject(error);
  }
);

export default api;


// src/services/reportService.ts
import api from './api';
import { AWRReport } from '../types/report';

export const reportService = {
  uploadReport: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return api.post<any, { id: number; task_id: string }>('/reports/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
        console.log(`Upload Progress: ${percent}%`);
      },
    });
  },

  listReports: async (params: {
    page: number;
    size: number;
    db_name?: string;
    date_from?: string;
    date_to?: string;
  }) => {
    return api.get<any, { total: number; items: AWRReport[] }>('/reports', { params });
  },

  getReport: async (id: number) => {
    return api.get<any, AWRReport>(`/reports/${id}`);
  },

  deleteReport: async (id: number) => {
    return api.delete(`/reports/${id}`);
  },

  getMetrics: async (id: number, category: string) => {
    return api.get(`/reports/${id}/metrics/${category}`);
  },
};


// src/hooks/useReports.ts
import useSWR from 'swr';
import { reportService } from '../services/reportService';

export const useReports = (page: number, size: number, filters?: any) => {
  const { data, error, mutate } = useSWR(
    ['/reports', page, size, filters],
    () => reportService.listReports({ page, size, ...filters })
  );

  return {
    reports: data?.items || [],
    total: data?.total || 0,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
};


// src/pages/ReportList/index.tsx
import React, { useState } from 'react';
import { Table, Button, Input, Space, Tag } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useReports } from '../../hooks/useReports';

const ReportList: React.FC = () => {
  const [page, setPage] = useState(1);
  const [size] = useState(20);
  const [filters, setFilters] = useState({});
  const navigate = useNavigate();

  const { reports, total, isLoading } = useReports(page, size, filters);

  const columns = [
    {
      title: '数据库名',
      dataIndex: 'db_name',
      key: 'db_name',
    },
    {
      title: '实例名',
      dataIndex: 'instance_name',
      key: 'instance_name',
    },
    {
      title: '快照时间',
      key: 'snapshot_time',
      render: (record: any) =>
        `${record.snapshot_begin} ~ ${record.snapshot_end}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors = {
          pending: 'orange',
          parsing: 'blue',
          parsed: 'green',
          failed: 'red',
        };
        return <Tag color={colors[status as keyof typeof colors]}>{status}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      render: (record: any) => (
        <Space>
          <Button type="link" onClick={() => navigate(`/reports/${record.id}`)}>
            查看
          </Button>
          <Button type="link" onClick={() => handleCompare(record.id)}>
            对比
          </Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索数据库名"
          onSearch={(value) => setFilters({ ...filters, db_name: value })}
          style={{ width: 200 }}
        />
      </Space>

      <Table
        columns={columns}
        dataSource={reports}
        loading={isLoading}
        rowKey="id"
        pagination={{
          current: page,
          pageSize: size,
          total: total,
          onChange: (p) => setPage(p),
        }}
      />
    </div>
  );
};

export default ReportList;
```

---

## 3. 数据库设计

### 3.1 数据库选型

选择 **PostgreSQL 14+** 作为主数据库:

**优势**:
1. **JSONB 字段类型**: 灵活存储不同版本 AWR 的差异化数据
2. **高级查询特性**: CTE、窗口函数、GIN 索引
3. **全文搜索**: 支持报告内容搜索
4. **时序数据扩展**: 可选 TimescaleDB 扩展

### 3.2 表结构设计

```sql
-- 1. 报告元数据表
CREATE TABLE awr_reports (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size BIGINT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 实例信息
    oracle_version VARCHAR(50),
    db_name VARCHAR(100),
    instance_name VARCHAR(100),
    host_name VARCHAR(100),

    -- 快照信息
    snapshot_begin TIMESTAMP,
    snapshot_end TIMESTAMP,
    snapshot_interval INTEGER,

    -- 状态
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_awr_reports_db_name ON awr_reports(db_name);
CREATE INDEX idx_awr_reports_snapshot_begin ON awr_reports(snapshot_begin);
CREATE INDEX idx_awr_reports_status ON awr_reports(status);

-- 2. 性能指标表
CREATE TABLE performance_metrics (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES awr_reports(id) ON DELETE CASCADE,
    metric_category VARCHAR(50) NOT NULL,
    metric_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_perf_metrics_report_id ON performance_metrics(report_id);
CREATE INDEX idx_perf_metrics_category ON performance_metrics(metric_category);
CREATE INDEX idx_perf_metrics_data ON performance_metrics USING GIN(metric_data);

-- 3. 诊断结果表
CREATE TABLE diagnostic_results (
    id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES awr_reports(id) ON DELETE CASCADE,
    rule_id VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    issue_title VARCHAR(255) NOT NULL,
    issue_description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    metric_values JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_diagnostic_report_id ON diagnostic_results(report_id);
CREATE INDEX idx_diagnostic_severity ON diagnostic_results(severity);

-- 4. 对比结果表
CREATE TABLE comparison_results (
    id SERIAL PRIMARY KEY,
    baseline_report_id INTEGER NOT NULL REFERENCES awr_reports(id) ON DELETE CASCADE,
    target_report_id INTEGER NOT NULL REFERENCES awr_reports(id) ON DELETE CASCADE,
    comparison_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_comparison_baseline ON comparison_results(baseline_report_id);
CREATE INDEX idx_comparison_target ON comparison_results(target_report_id);

-- 5. 用户表 (Phase 2)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 触发器: 自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_awr_reports_updated_at
    BEFORE UPDATE ON awr_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3.3 JSONB 数据结构示例

```json
// load_profile metric_data
{
  "db_time": {
    "value": 12345678,
    "per_second": 1234.56,
    "per_txn": 0.12
  },
  "cpu_time": {
    "value": 8901234,
    "per_second": 890.12,
    "per_txn": 0.09
  },
  "logical_reads": {
    "value": 9876543210,
    "per_second": 987654.32,
    "per_txn": 9876.54
  },
  "physical_reads": {
    "value": 123456789,
    "per_second": 12345.68,
    "per_txn": 123.46
  }
}

// wait_events metric_data
{
  "events": [
    {
      "name": "db file sequential read",
      "waits": 123456,
      "time_waited": 7890.12,
      "avg_wait": 0.064,
      "pct_db_time": 25.6
    },
    {
      "name": "log file sync",
      "waits": 45678,
      "time_waited": 3456.78,
      "avg_wait": 0.076,
      "pct_db_time": 11.2
    }
  ]
}

// top_sql metric_data
{
  "sqls": [
    {
      "sql_id": "abc123xyz",
      "sql_text": "SELECT * FROM ...",
      "executions": 12345,
      "cpu_time": 567890,
      "elapsed_time": 678901,
      "buffer_gets": 9876543,
      "physical_reads": 123456,
      "rows_processed": 234567
    }
  ]
}
```

---

## 4. 接口设计

### 4.1 RESTful API 规范

**基础 URL**: `/api/v1`

**认证方式** (Phase 2): JWT Bearer Token

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

### 4.2 API 端点列表

#### 4.2.1 报告管理 API

```yaml
# 上传报告
POST /api/v1/reports/upload
Content-Type: multipart/form-data
Body:
  file: <HTML 文件>
Response:
  {
    "id": 1,
    "filename": "awr_report.html",
    "status": "pending",
    "task_id": "abc-123-xyz"
  }

# 获取报告列表
GET /api/v1/reports?page=1&size=20&db_name=PROD&date_from=2025-01-01
Response:
  {
    "total": 100,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": 1,
        "filename": "awr_report.html",
        "db_name": "PROD",
        "instance_name": "PROD1",
        "snapshot_begin": "2025-01-01T00:00:00",
        "snapshot_end": "2025-01-01T01:00:00",
        "status": "parsed"
      }
    ]
  }

# 获取报告详情
GET /api/v1/reports/{report_id}
Response:
  {
    "id": 1,
    "filename": "awr_report.html",
    "oracle_version": "19.3.0",
    "db_name": "PROD",
    "instance_name": "PROD1",
    "host_name": "server01",
    "snapshot_begin": "2025-01-01T00:00:00",
    "snapshot_end": "2025-01-01T01:00:00",
    "snapshot_interval": 60,
    "status": "parsed"
  }

# 删除报告
DELETE /api/v1/reports/{report_id}
Response:
  {
    "message": "删除成功"
  }
```

#### 4.2.2 分析 API

```yaml
# 触发分析
POST /api/v1/reports/{report_id}/analyze
Response:
  {
    "task_id": "xyz-789-abc",
    "message": "分析任务已启动"
  }

# 获取性能指标
GET /api/v1/reports/{report_id}/metrics/{category}
# category: load_profile | wait_events | sql_stats | io_stats | memory_stats
Response:
  {
    "category": "load_profile",
    "data": {
      "db_time": {"value": 12345678, "per_second": 1234.56},
      "cpu_time": {"value": 8901234, "per_second": 890.12}
    }
  }

# 获取诊断结果
GET /api/v1/reports/{report_id}/diagnostics
Response:
  {
    "report_id": 1,
    "summary": {
      "critical": 2,
      "high": 5,
      "medium": 8,
      "low": 3
    },
    "diagnostics": [
      {
        "id": 1,
        "rule_id": "HIGH_CPU_USAGE",
        "severity": "high",
        "category": "cpu",
        "issue_title": "CPU 使用率过高",
        "issue_description": "CPU 使用率达到 85%...",
        "recommendation": "1. 检查 Top SQL...",
        "metric_values": {"cpu_utilization": 85.6}
      }
    ]
  }
```

#### 4.2.3 对比 API

```yaml
# 创建对比
POST /api/v1/comparisons
Body:
  {
    "baseline_id": 1,
    "target_id": 2
  }
Response:
  {
    "id": 123,
    "baseline_id": 1,
    "target_id": 2,
    "comparison": {
      "load_profile": {
        "db_time": {
          "baseline": 12345678,
          "target": 15678901,
          "diff_abs": 3333223,
          "diff_pct": 27.0,
          "trend": "up"
        }
      },
      "wait_events": { ... },
      "top_sql": { ... }
    }
  }

# 获取对比结果
GET /api/v1/comparisons/{comparison_id}
```

#### 4.2.4 导出 API

```yaml
# 导出 PDF
GET /api/v1/reports/{report_id}/export?format=pdf
Response:
  Content-Type: application/pdf
  <Binary PDF Data>

# 导出 Excel
GET /api/v1/reports/{report_id}/export?format=excel
Response:
  Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  <Binary Excel Data>

# 导出 JSON
GET /api/v1/reports/{report_id}/export?format=json
Response:
  Content-Type: application/json
  { ... }
```

---

## 5. 部署方案

### 5.1 Docker 容器化

#### Dockerfile (后端)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile (前端)

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 安装依赖
COPY package.json package-lock.json ./
RUN npm ci

# 构建
COPY . .
RUN npm run build

# 生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 5.2 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/awrdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./data/uploads:/app/uploads
    networks:
      - app-network

  celery_worker:
    build: ./backend
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/awrdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./data/uploads:/app/uploads
    networks:
      - app-network

  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: awrdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### 5.3 环境变量配置

```bash
# .env.example
# 数据库
DATABASE_URL=postgresql://postgres:password@postgres:5432/awrdb

# Redis
REDIS_URL=redis://redis:6379/0

# 文件存储
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=52428800  # 50MB

# JWT (Phase 2)
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 其他
DEBUG=false
LOG_LEVEL=INFO
```

---

## 6. 测试策略

### 6.1 单元测试

#### 后端单元测试

```python
# tests/unit/test_parser.py
import pytest
from app.core.parser.oracle19c import Oracle19cParser

def test_parse_instance_info():
    with open('tests/fixtures/awr_19c_sample.html', 'r') as f:
        html = f.read()

    parser = Oracle19cParser(html)
    info = parser._parse_instance_info()

    assert info['db_name'] == 'TESTDB'
    assert info['instance_name'] == 'TESTDB1'


def test_parse_load_profile():
    with open('tests/fixtures/awr_19c_sample.html', 'r') as f:
        html = f.read()

    parser = Oracle19cParser(html)
    profile = parser._parse_load_profile()

    assert 'DB Time' in profile
    assert profile['DB Time']['per_second'] > 0


# tests/unit/test_rule_engine.py
from app.core.analyzer.rule_engine import RuleEngine

def test_rule_matching():
    engine = RuleEngine('app/rules')

    metrics = {
        'cpu_utilization': 85,
        'buffer_hit_ratio': 88
    }

    results = engine.evaluate(metrics)

    assert len(results) > 0
    assert any(r['rule_id'] == 'HIGH_CPU_USAGE' for r in results)
```

#### 前端单元测试

```typescript
// src/components/ReportCard/__tests__/ReportCard.test.tsx
import { render, screen } from '@testing-library/react';
import ReportCard from '../index';

describe('ReportCard', () => {
  const mockReport = {
    id: 1,
    filename: 'test.html',
    db_name: 'TESTDB',
    status: 'parsed',
  };

  test('renders report information', () => {
    render(<ReportCard report={mockReport} />);

    expect(screen.getByText('TESTDB')).toBeInTheDocument();
    expect(screen.getByText('test.html')).toBeInTheDocument();
  });
});
```

### 6.2 集成测试

```python
# tests/integration/test_upload_parse_workflow.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_and_parse_workflow():
    # 1. 上传报告
    with open('tests/fixtures/awr_19c_sample.html', 'rb') as f:
        response = client.post(
            '/api/v1/reports/upload',
            files={'file': ('test.html', f, 'text/html')}
        )

    assert response.status_code == 200
    report_id = response.json()['id']

    # 2. 等待解析完成 (使用 Celery eager 模式)
    import time
    time.sleep(2)

    # 3. 获取报告详情
    response = client.get(f'/api/v1/reports/{report_id}')
    assert response.status_code == 200
    assert response.json()['status'] == 'parsed'

    # 4. 获取指标
    response = client.get(f'/api/v1/reports/{report_id}/metrics/load_profile')
    assert response.status_code == 200
```

### 6.3 测试覆盖率目标

- **单元测试覆盖率**: > 70%
- **API 测试覆盖率**: 100% (所有端点)
- **关键路径测试**: 100% (上传-解析-分析-导出)

---

## 7. 性能优化

### 7.1 后端优化

1. **异步处理**: 使用 Celery 异步处理文件解析和分析
2. **缓存策略**: Redis 缓存解析结果和诊断结果
3. **数据库优化**:
   - 合理使用索引 (db_name, snapshot_begin, status)
   - JSONB GIN 索引加速 JSONB 查询
   - 使用连接池 (SQLAlchemy)
4. **流式处理**: 大文件分块上传和解析

### 7.2 前端优化

1. **代码分割**: React.lazy() 动态加载页面组件
2. **虚拟滚动**: 长列表使用 react-window
3. **图表优化**: ECharts 按需加载,数据采样
4. **CDN**: 静态资源 CDN 加速

### 7.3 监控指标

- API 响应时间 < 500ms (P95)
- 报告解析时间 < 10s (5MB 文件)
- 前端首屏加载 < 2s

---

## 8. 安全设计

### 8.1 安全措施

| 层级 | 措施 | 实现 |
|-----|------|------|
| 传输层 | HTTPS/TLS | Nginx SSL 配置 |
| 认证层 | JWT Token | FastAPI + python-jose (Phase 2) |
| 授权层 | RBAC 权限控制 | 用户角色表 (Phase 2) |
| 应用层 | 输入校验 | Pydantic 模型验证 |
| 应用层 | SQL 注入防护 | SQLAlchemy ORM |
| 应用层 | XSS 防护 | React 自动转义 + CSP |
| 文件层 | 文件类型校验 | 文件头检测 |
| 文件层 | 文件大小限制 | 50MB 限制 |
| 数据库层 | 密码加密 | passlib (bcrypt) |

### 8.2 敏感信息处理

- 数据库连接串等敏感信息使用环境变量
- 不在前端展示完整文件路径
- 日志中脱敏敏感信息

---

**文档状态**: 待评审
**维护人**: 技术负责人
