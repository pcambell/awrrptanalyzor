import React, { useState } from 'react';
import { Upload, Card, message, Button, Space, Alert } from 'antd';
import { InboxOutlined, UploadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { reportApi } from '../../services/api';
import { useNavigate } from 'react-router-dom';

const { Dragger } = Upload;

const UploadPage: React.FC = () => {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.html,.htm',
    maxCount: 1,
    beforeUpload: async (file) => {
      const isHTML = file.type === 'text/html' || file.name.endsWith('.html') || file.name.endsWith('.htm');
      if (!isHTML) {
        message.error('只能上传 HTML 格式的 AWR 报告文件!');
        return false;
      }

      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error('文件大小不能超过 50MB!');
        return false;
      }

      setUploading(true);

      try {
        const response = await reportApi.upload(file);
        message.success(`${file.name} 上传成功!`);

        // Navigate to report detail page after 1 second
        setTimeout(() => {
          navigate(`/reports/${response.id}`);
        }, 1000);
      } catch (error: any) {
        message.error(`上传失败: ${error.message}`);
      } finally {
        setUploading(false);
      }

      return false; // Prevent default upload behavior
    },
  };

  return (
    <div>
      <Card title="上传 AWR 报告">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Alert
            message="使用说明"
            description={
              <ul>
                <li>支持 Oracle 11g/12c/19c 版本的 AWR HTML 报告</li>
                <li>文件大小限制: 最大 50MB</li>
                <li>上传后系统将自动解析报告内容(通常在 10 秒内完成)</li>
                <li>解析完成后可查看性能分析和诊断建议</li>
              </ul>
            }
            type="info"
            showIcon
          />

          <Dragger {...uploadProps} disabled={uploading}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽 AWR 报告文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持 .html 和 .htm 格式文件
            </p>
          </Dragger>

          <div style={{ textAlign: 'center' }}>
            <Space>
              <Button
                type="primary"
                icon={<UploadOutlined />}
                onClick={() => navigate('/reports')}
              >
                查看已上传报告
              </Button>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default UploadPage;
