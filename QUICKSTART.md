# 快速启动指南

本指南将帮助您在5分钟内启动 Oracle AWR 报告分析软件。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存

## 快速启动步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/awrrptanalyzor.git
cd awrrptanalyzor
```

### 2. 配置环境变量 (可选)

如果需要自定义配置,复制并编辑环境变量文件:

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件修改配置
cd ..
```

### 3. 启动所有服务

```bash
# 构建并启动所有容器
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

等待所有服务启动完成 (约 1-2 分钟)。

### 4. 初始化数据库

首次启动需要运行数据库迁移:

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据库迁移
alembic upgrade head

# 退出容器
exit
```

### 5. 访问应用

- **前端界面**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 验证安装

### 检查后端健康状态

```bash
curl http://localhost:8000/health
```

应该返回:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 检查服务状态

```bash
docker-compose ps
```

所有服务应该显示 "Up" 状态:
- awr_postgres
- awr_redis
- awr_backend
- awr_celery_worker
- awr_frontend

## 使用示例

### 1. 准备 AWR 报告

在 Oracle 数据库中生成 AWR 报告 (HTML 格式):

```sql
-- 在 SQL*Plus 或 SQL Developer 中执行
@?/rdbms/admin/awrrpt.sql
```

按提示选择快照 ID 和输出格式 (选择 HTML)。

### 2. 上传报告

1. 打开浏览器访问 http://localhost
2. 拖拽 AWR HTML 文件到上传区域,或点击选择文件
3. 等待解析完成 (通常 10 秒内)
4. 点击"查看"进入报告详情页

### 3. 查看分析结果

- **概览**: 关键性能指标概览
- **Load Profile**: 负载详情
- **等待事件**: Top 等待事件分析
- **SQL 统计**: 高消耗 SQL 排行
- **诊断**: 智能诊断问题和建议

## 停止服务

```bash
# 停止所有容器
docker-compose stop

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷 (注意:会删除所有数据)
docker-compose down -v
```

## 常见问题

### Q1: 端口冲突

如果 80 或 8000 端口已被占用,编辑 `docker-compose.yml` 修改端口映射:

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 修改为 8080
  backend:
    ports:
      - "8001:8000"  # 修改为 8001
```

### Q2: 容器启动失败

查看日志排查问题:

```bash
docker-compose logs backend
docker-compose logs postgres
```

### Q3: 数据库连接失败

确保 PostgreSQL 容器已完全启动:

```bash
docker-compose logs postgres | grep "database system is ready"
```

### Q4: 上传文件失败

检查后端容器日志:

```bash
docker-compose logs -f backend
```

确保 uploads 目录有写权限:

```bash
docker-compose exec backend ls -la uploads
```

## 开发模式

如果需要修改代码并实时查看效果:

### 后端开发

```bash
cd backend

# 使用本地 Python 环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

# 启动开发服务器 (支持热重载)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 在另一个终端启动 Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

## 生产部署

生产环境部署建议:

1. **修改密码和密钥**:编辑 `.env` 文件,修改所有默认密码和密钥
2. **配置 HTTPS**: 使用 Let's Encrypt 或其他 SSL 证书
3. **配置域名**: 修改 `ALLOWED_ORIGINS` 和 Nginx 配置
4. **数据备份**: 配置 PostgreSQL 自动备份
5. **监控告警**: 集成 Prometheus + Grafana

详细部署文档见 [docs/Deployment.md](docs/Deployment.md)

## 下一步

- 阅读[用户手册](docs/UserGuide.md)了解完整功能
- 阅读[技术文档](docs/TechnicalDesign.md)了解架构设计
- 查看[API 文档](http://localhost:8000/docs)了解 API 接口
- 加入社区反馈问题和建议

## 技术支持

- 问题反馈: https://github.com/yourusername/awrrptanalyzor/issues
- 邮箱: support@example.com
