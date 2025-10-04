// AWR Report Types
export interface AWRReport {
  id: number;
  filename: string;
  file_size: number;
  status: 'pending' | 'parsing' | 'parsed' | 'failed';
  upload_time: string;
  parse_time?: string;
  error_message?: string;
  db_name?: string;
  db_version?: string;
  instance_name?: string;
  host_name?: string;
  begin_snap_id?: number;
  end_snap_id?: number;
  begin_time?: string;
  end_time?: string;
}

// Performance Metric Types
export interface PerformanceMetric {
  id: number;
  report_id: number;
  category: string;
  metric_name: string;
  metric_value: any;
  data: any;
}

// Diagnostic Result Types
export interface DiagnosticResult {
  id: number;
  report_id: number;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: string;
  issue_title: string;
  issue_description?: string;
  recommendation?: string;
  related_metrics?: any;
}

// API Response Types
export interface ListResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface UploadResponse {
  id: number;
  filename: string;
  status: string;
  upload_time: string;
}

export interface DiagnosticSummary {
  report_id: number;
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  diagnostics: DiagnosticResult[];
}

// Chart Data Types
export interface LoadProfileData {
  category: string;
  data: Record<string, {
    per_second: number;
    per_txn: number;
  }>;
}

export interface WaitEventData {
  event: string;
  waits: number;
  time_waited_s: number;
  avg_wait_ms: number;
  pct_db_time: number;
}

export interface TopSQLData {
  sql_id: string;
  plan_hash_value: number;
  executions: number;
  elapsed_time_s: number;
  cpu_time_s: number;
  buffer_gets: number;
  sql_text?: string;
}
