# 前端开发环境配置指南

## 当前状态

✅ 已完成:
- React 18 + TypeScript + Vite 项目初始化
- Ant Design 5 UI 组件库集成
- React Router v6 路由配置
- Axios API 服务封装
- 三个核心页面实现:
  - 上传页面 (`/`)
  - 报告列表 (`/reports`)
  - 报告详情 (`/reports/:id`)

## 快速启动

### 1. 安装依赖

```bash
cd frontend
npm install
```

**注意**: 如果 npm install 超时,可以使用国内镜像:

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:3000

### 3. 启动后端服务

前端需要后端 API 支持,请确保后端服务已启动:

```bash
# 在另一个终端窗口
cd backend

# 创建虚拟环境(如果还没有)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 项目结构

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout/
│   │       └── MainLayout.tsx        # 主布局组件
│   ├── pages/
│   │   ├── Upload/
│   │   │   └── index.tsx             # 上传页面
│   │   ├── ReportList/
│   │   │   └── index.tsx             # 报告列表页面
│   │   └── ReportDetail/
│   │       └── index.tsx             # 报告详情页面
│   ├── services/
│   │   └── api.ts                    # API 服务封装
│   ├── types/
│   │   └── index.ts                  # TypeScript 类型定义
│   ├── App.tsx                       # 根组件
│   └── main.tsx                      # 入口文件
├── package.json
├── vite.config.ts                    # Vite 配置
└── tsconfig.json                     # TypeScript 配置
```

## 已实现功能

### 1. 上传页面

- 拖拽上传 AWR 报告
- 文件类型验证 (.html)
- 文件大小限制 (50MB)
- 上传成功后自动跳转到详情页

### 2. 报告列表页面

- 表格展示报告列表
- 分页、排序、筛选
- 报告状态标签 (待解析/解析中/已解析/失败)
- 查看和删除操作

### 3. 报告详情页面

- 报告基本信息展示
- 诊断分析结果展示
- 问题汇总统计
- 触发分析按钮

## API 接口

所有 API 请求通过 Vite 代理转发到后端:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### 可用接口

- `POST /api/v1/reports/upload` - 上传报告
- `GET /api/v1/reports` - 获取报告列表
- `GET /api/v1/reports/:id` - 获取报告详情
- `DELETE /api/v1/reports/:id` - 删除报告
- `POST /api/v1/reports/:id/analyze` - 触发分析
- `GET /api/v1/reports/:id/diagnostics` - 获取诊断结果

## 待实现功能

### 优先级 P0 (核心功能)

1. **性能指标图表展示**
   - Load Profile 柱状图
   - 等待事件饼图
   - Top SQL 表格
   - 使用 ECharts 实现

2. **错误处理优化**
   - 全局错误提示
   - 请求失败重试
   - 加载状态优化

### 优先级 P1 (增强功能)

1. **历史对比功能**
   - 选择两个报告对比
   - 指标变化趋势图

2. **报告导出**
   - PDF 导出
   - Excel 导出

3. **搜索和筛选**
   - 按数据库名搜索
   - 按时间范围筛选

### 优先级 P2 (优化功能)

1. **响应式设计**
   - 移动端适配
   - 平板适配

2. **主题切换**
   - 深色模式
   - 浅色模式

3. **国际化**
   - 中英文切换

## 开发技巧

### 1. 使用 React DevTools

安装浏览器扩展以调试 React 组件:
- [React Developer Tools](https://react.dev/learn/react-developer-tools)

### 2. 使用 Ant Design ProComponents

对于复杂表单和表格,可以考虑使用:
```bash
npm install @ant-design/pro-components
```

### 3. 状态管理

当前使用 useState 和 useEffect,如果状态管理变复杂,可以引入:
- Zustand (轻量级)
- Redux Toolkit (全功能)

### 4. 性能优化

- 使用 React.memo 避免不必要的重渲染
- 使用 useMemo 和 useCallback 优化计算
- 代码分割: React.lazy + Suspense

## 常见问题

### Q1: npm install 失败

A: 切换到国内镜像:
```bash
npm config set registry https://registry.npmmirror.com
```

### Q2: 启动后看不到数据

A: 确保后端服务已启动并运行在 http://localhost:8000

### Q3: 跨域问题

A: Vite 已配置代理,确保 vite.config.ts 中的 proxy 配置正确

### Q4: TypeScript 报错

A: 检查 tsconfig.json 配置,确保所有必要的依赖已安装

## 测试

### 手动测试流程

1. **测试上传功能**
   - 访问 http://localhost:3000
   - 拖拽一个 AWR HTML 文件
   - 验证上传成功并跳转

2. **测试列表功能**
   - 访问 http://localhost:3000/reports
   - 验证报告列表显示
   - 测试分页和筛选

3. **测试详情功能**
   - 点击某个报告的"查看"
   - 验证详情信息显示
   - 点击"触发分析"
   - 验证诊断结果显示

### 单元测试 (待实现)

```bash
# 安装测试依赖
npm install -D vitest @testing-library/react @testing-library/user-event

# 运行测试
npm run test
```

## 部署

### 开发环境

```bash
npm run dev
```

### 生产环境

```bash
# 构建
npm run build

# 预览构建结果
npm run preview
```

构建产物在 `dist/` 目录,可以部署到任何静态服务器。

### Docker 部署

使用项目根目录的 `docker-compose.yml`:

```bash
docker-compose up -d
```

访问 http://localhost (Nginx 反向代理)

## 参考资源

- [React 官方文档](https://react.dev/)
- [Ant Design 官方文档](https://ant.design/)
- [Vite 官方文档](https://vitejs.dev/)
- [React Router 官方文档](https://reactrouter.com/)
- [ECharts 官方文档](https://echarts.apache.org/)

## 下一步

1. 安装依赖: `cd frontend && npm install`
2. 启动开发: `npm run dev`
3. 实现图表组件 (ECharts)
4. 完善错误处理
5. 添加单元测试
