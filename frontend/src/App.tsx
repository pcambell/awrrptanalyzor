import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from './components/Layout/MainLayout';
import UploadPage from './pages/Upload';
import ReportListPage from './pages/ReportList';
import ReportDetailPage from './pages/ReportDetail';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<UploadPage />} />
            <Route path="reports" element={<ReportListPage />} />
            <Route path="reports/:id" element={<ReportDetailPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
