# Oracle AWR Report Analyzer

Oracle AWR 报告分析软件 - 智能化数据库性能诊断工具

## 项目简介

本项目旨在开发一款面向 DBA 和数据库工程师的 Oracle AWR 报告智能分析工具。通过自动解析 AWR HTML 报告,提供深度性能分析、智能诊断建议、历史趋势对比和多格式报告导出功能。

### 核心功能

- ✅ **AWR 报告解析**: 支持 Oracle 11g/12c/19c 多版本 AWR HTML 报告自动解析
- 📊 **性能指标可视化**: 图表化展示 Load Profile、等待事件、Top SQL 等核心指标
- 🔍 **智能诊断分析**: 基于专家规则库自动识别性能瓶颈并提供优化建议
- 📈 **历史对比分析**: 对比不同时间点的性能变化趋势
- 📑 **多格式导出**: 支持 PDF、Excel、JSON 格式报告导出
- 🐳 **Docker 部署**: 一键部署,开箱即用

### 技术栈

**后端**:
- Python 3.11+
- FastAPI (Web 框架)
- SQLAlchemy (ORM)
- Celery (异步任务)
- PostgreSQL (数据库)
- Redis (缓存 + 消息队列)

**前端**:
- React 18 + TypeScript
- Ant Design Pro
- ECharts (图表)
- Vite (构建工具)

**部署**:
- Docker + Docker Compose
- Nginx (反向代理)

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- (可选) Python 3.11+, Node.js 18+

### 使用 Docker 启动 (推荐)

```bash
# 克隆仓库
git clone https://github.com/yourusername/awrrptanalyzor.git
cd awrrptanalyzor

# 启动所有服务
docker-compose up -d

# 访问应用
# 前端: http://localhost
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 配置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动 Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 使用指南

### 1. 上传 AWR 报告

1. 在 Oracle 数据库中生成 AWR 报告 (HTML 格式)
2. 访问系统首页,拖拽或点击上传报告文件
3. 系统自动解析报告 (通常 10 秒内完成)

### 2. 查看性能分析

1. 在报告列表中点击"查看"进入详情页
2. 通过 Tab 切换查看不同维度的性能指标:
   - 概览: 关键指标卡片
   - Load Profile: 负载概况
   - 等待事件: Top 等待事件分析
   - SQL 统计: Top SQL 排行
   - 内存: SGA/PGA 使用情况
   - IO: 表空间和文件 IO 统计

### 3. 智能诊断

1. 进入诊断页面,系统自动识别性能问题
2. 按严重程度查看问题列表
3. 展开查看详细的问题描述和优化建议

### 4. 历史对比

1. 选择两个不同时间点的报告
2. 查看各项指标的变化趋势
3. 识别性能退化或改善的原因

### 5. 导出报告

1. 选择导出格式 (PDF/Excel/JSON)
2. 自定义导出内容
3. 下载报告文件

## 项目文档

- [产品需求文档 (PRD)](./docs/PRD.md)
- [技术设计文档](./docs/TechnicalDesign.md)
- [工作分解结构 (WBS)](./docs/WBS.md)
- [API 文档](http://localhost:8000/docs) (启动后端后访问)
- [部署指南](./docs/Deployment.md) (待完成)
- [用户手册](./docs/UserGuide.md) (待完成)

## 项目结构

```
awrrptanalyzor/
├── backend/              # 后端 Python 代码
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心业务逻辑 (解析器、分析引擎)
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # 业务服务层
│   │   ├── tasks/        # Celery 异步任务
│   │   ├── rules/        # 诊断规则库
│   │   └── main.py       # FastAPI 应用入口
│   ├── migrations/       # 数据库迁移
│   ├── tests/            # 测试
│   └── requirements.txt
│
├── frontend/             # 前端 React 代码
│   ├── src/
│   │   ├── pages/        # 页面组件
│   │   ├── components/   # 通用组件
│   │   ├── services/     # API 服务
│   │   ├── stores/       # 状态管理
│   │   └── types/        # TypeScript 类型
│   ├── public/
│   └── package.json
│
├── docs/                 # 项目文档
├── docker-compose.yml    # Docker Compose 配置
└── README.md
```

## 开发路线图

### Phase 1: MVP (已完成)
- [x] 基础架构搭建
- [x] Oracle 19c AWR 解析
- [x] 基本性能指标展示
- [x] 简单诊断规则 (5 条)

### Phase 2: 核心功能 (进行中)
- [ ] 支持 Oracle 11g/12c
- [ ] 完整诊断规则库 (30+ 条)
- [ ] 历史对比功能
- [ ] PDF/Excel 导出

### Phase 3: 高级特性 (计划中)
- [ ] RAC 支持
- [ ] 趋势分析
- [ ] 机器学习异常检测
- [ ] 用户权限管理

## 贡献指南

欢迎贡献代码、报告问题或提出功能建议!

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- Python: 遵循 PEP 8 规范
- TypeScript: 使用 ESLint 配置
- 提交信息: 遵循 Conventional Commits 规范

## 测试

```bash
# 后端测试
cd backend
pytest tests/ -v --cov=app

# 前端测试
cd frontend
npm run test
```

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页: https://github.com/yourusername/awrrptanalyzor
- 问题反馈: https://github.com/yourusername/awrrptanalyzor/issues
- 邮箱: your.email@example.com

## 致谢

感谢所有贡献者和以下开源项目:

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Ant Design](https://ant.design/)
- [ECharts](https://echarts.apache.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Celery](https://docs.celeryproject.org/)
