import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Descriptions, Tabs, Spin, message, Button, Space, Alert } from 'antd';
import { SyncOutlined, ExperimentOutlined } from '@ant-design/icons';
import { reportApi } from '../../services/api';
import type { AWRReport, DiagnosticSummary } from '../../types';
import dayjs from 'dayjs';

const ReportDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<AWRReport | null>(null);
  const [diagnostics, setDiagnostics] = useState<DiagnosticSummary | null>(null);

  const fetchReport = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await reportApi.get(parseInt(id));
      setReport(data);
    } catch (error: any) {
      message.error(`加载失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchDiagnostics = async () => {
    if (!id) return;
    try {
      const data = await reportApi.getDiagnostics(parseInt(id));
      setDiagnostics(data);
    } catch (error: any) {
      // Diagnostics might not exist yet
      console.error('Failed to fetch diagnostics:', error);
    }
  };

  const handleAnalyze = async () => {
    if (!id) return;
    setAnalyzing(true);
    try {
      await reportApi.analyze(parseInt(id));
      message.success('分析完成');
      await fetchDiagnostics();
    } catch (error: any) {
      message.error(`分析失败: ${error.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    fetchReport();
    fetchDiagnostics();
  }, [id]);

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  if (!report) {
    return <Alert message="报告不存在" type="error" />;
  }

  const tabItems = [
    {
      key: 'overview',
      label: '概览',
      children: (
        <Descriptions bordered column={2}>
          <Descriptions.Item label="报告ID">{report.id}</Descriptions.Item>
          <Descriptions.Item label="文件名">{report.filename}</Descriptions.Item>
          <Descriptions.Item label="数据库名">{report.db_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="实例名">{report.instance_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="主机名">{report.host_name || '-'}</Descriptions.Item>
          <Descriptions.Item label="数据库版本">{report.db_version || '-'}</Descriptions.Item>
          <Descriptions.Item label="起始快照ID">{report.begin_snap_id || '-'}</Descriptions.Item>
          <Descriptions.Item label="结束快照ID">{report.end_snap_id || '-'}</Descriptions.Item>
          <Descriptions.Item label="起始时间">
            {report.begin_time ? dayjs(report.begin_time).format('YYYY-MM-DD HH:mm:ss') : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="结束时间">
            {report.end_time ? dayjs(report.end_time).format('YYYY-MM-DD HH:mm:ss') : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="上传时间">
            {dayjs(report.upload_time).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          <Descriptions.Item label="解析时间">
            {report.parse_time ? dayjs(report.parse_time).format('YYYY-MM-DD HH:mm:ss') : '-'}
          </Descriptions.Item>
        </Descriptions>
      ),
    },
    {
      key: 'diagnostics',
      label: '诊断分析',
      children: diagnostics ? (
        <div>
          <Card
            size="small"
            style={{ marginBottom: 16 }}
            title="问题汇总"
          >
            <Space size="large">
              <span>严重: <strong style={{ color: 'red' }}>{diagnostics.summary.critical}</strong></span>
              <span>高危: <strong style={{ color: 'orange' }}>{diagnostics.summary.high}</strong></span>
              <span>中等: <strong style={{ color: 'gold' }}>{diagnostics.summary.medium}</strong></span>
              <span>低危: <strong>{diagnostics.summary.low}</strong></span>
            </Space>
          </Card>

          {diagnostics.diagnostics.map((diag, index) => (
            <Card
              key={index}
              size="small"
              style={{ marginBottom: 8 }}
              title={diag.issue_title}
              extra={
                <span style={{
                  color: diag.severity === 'critical' ? 'red' :
                    diag.severity === 'high' ? 'orange' :
                      diag.severity === 'medium' ? 'gold' : 'inherit'
                }}>
                  {diag.severity}
                </span>
              }
            >
              {diag.issue_description && <p>{diag.issue_description}</p>}
              {diag.recommendation && (
                <Alert
                  message="优化建议"
                  description={diag.recommendation}
                  type="info"
                  showIcon
                />
              )}
            </Card>
          ))}
        </div>
      ) : (
        <Alert
          message="暂无诊断结果"
          description={
            <Space>
              <span>点击右上角"触发分析"按钮开始诊断</span>
            </Space>
          }
          type="info"
        />
      ),
    },
  ];

  return (
    <div>
      <Card
        title={`AWR 报告详情 - ${report.filename}`}
        extra={
          <Space>
            <Button
              icon={<SyncOutlined />}
              onClick={() => {
                fetchReport();
                fetchDiagnostics();
              }}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<ExperimentOutlined />}
              onClick={handleAnalyze}
              loading={analyzing}
            >
              触发分析
            </Button>
          </Space>
        }
      >
        <Tabs items={tabItems} />
      </Card>
    </div>
  );
};

export default ReportDetailPage;
