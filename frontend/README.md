# AWR 报告分析器 - 前端

基于 React 18 + TypeScript + Ant Design 的前端应用。

## 技术栈

- **框架**: React 18
- **构建工具**: Vite
- **UI 库**: Ant Design 5
- **路由**: React Router v6
- **HTTP 客户端**: Axios
- **图表**: ECharts
- **语言**: TypeScript

## 开发环境

### 前置要求

- Node.js 18+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── components/        # 通用组件
│   ├── Layout/       # 布局组件
│   └── Charts/       # 图表组件
├── pages/            # 页面组件
│   ├── Upload/       # 上传页面
│   ├── ReportList/   # 报告列表
│   └── ReportDetail/ # 报告详情
├── services/         # API 服务
│   └── api.ts        # API 封装
├── types/            # TypeScript 类型定义
│   └── index.ts
└── utils/            # 工具函数
```

## 功能特性

- ✅ AWR 报告上传
- ✅ 报告列表展示
- ✅ 报告详情查看
- ✅ 性能诊断分析
- 🚧 图表可视化 (待实现)
- 🚧 历史对比 (待实现)

## API 配置

开发环境下,所有 `/api` 请求会被代理到后端服务器 `http://localhost:8000`

可在 `vite.config.ts` 中修改配置:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

## 后续开发计划

1. 实现 ECharts 图表组件 (Load Profile、等待事件、Top SQL)
2. 添加历史对比功能
3. 实现报告导出
4. 添加单元测试
