import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Tag, Space, message, Popconfirm } from 'antd';
import { EyeOutlined, DeleteOutlined, SyncOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useNavigate } from 'react-router-dom';
import { reportApi } from '../../services/api';
import type { AWRReport } from '../../types';
import dayjs from 'dayjs';

const ReportListPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [reports, setReports] = useState<AWRReport[]>([]);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
  });

  const fetchReports = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await reportApi.list({
        page,
        page_size: pageSize,
      });
      setReports(response.items);
      setTotal(response.total);
      setPagination({ current: page, pageSize });
    } catch (error: any) {
      message.error(`加载失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await reportApi.delete(id);
      message.success('删除成功');
      fetchReports(pagination.current, pagination.pageSize);
    } catch (error: any) {
      message.error(`删除失败: ${error.message}`);
    }
  };

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      pending: { color: 'default', text: '待解析' },
      parsing: { color: 'processing', text: '解析中' },
      parsed: { color: 'success', text: '已解析' },
      failed: { color: 'error', text: '解析失败' },
    };
    const statusInfo = statusMap[status] || { color: 'default', text: status };
    return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
  };

  const columns: ColumnsType<AWRReport> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      ellipsis: true,
    },
    {
      title: '数据库',
      dataIndex: 'db_name',
      key: 'db_name',
      width: 120,
    },
    {
      title: '实例',
      dataIndex: 'instance_name',
      key: 'instance_name',
      width: 120,
    },
    {
      title: '版本',
      dataIndex: 'db_version',
      key: 'db_version',
      width: 150,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '上传时间',
      dataIndex: 'upload_time',
      key: 'upload_time',
      width: 180,
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: AWRReport) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/reports/${record.id}`)}
            disabled={record.status !== 'parsed'}
          >
            查看
          </Button>
          <Popconfirm
            title="确定要删除这个报告吗?"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card
        title="AWR 报告列表"
        extra={
          <Button
            icon={<SyncOutlined />}
            onClick={() => fetchReports(pagination.current, pagination.pageSize)}
          >
            刷新
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={reports}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              fetchReports(page, pageSize);
            },
          }}
        />
      </Card>
    </div>
  );
};

export default ReportListPage;
