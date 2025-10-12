/**
 * API client for nakamura-misaki backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Task {
  id: string;
  user_id: string;
  title: string;
  due_date: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  progress: number;
  description: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  user_id: string;
  name: string;
  real_name: string;
  display_name: string;
  email: string;
  is_admin: boolean;
  is_bot: boolean;
  created_at: string;
}

export interface Session {
  session_id: string;
  user_id: string;
  created_at: string;
  last_active: string;
  title: string;
  message_count: number;
  is_active: boolean;
}

export interface Prompt {
  name: string;
  system_prompt: string;
  description: string;
  version: string;
  created_at: string;
  updated_at: string;
}

export interface ErrorLog {
  id: number;
  error_hash: string;
  message: string;
  stack?: string;
  url?: string;
  user_agent?: string;
  context?: Record<string, unknown>;
  occurrence_count: number;
  first_seen: string;
  last_seen: string;
}

// API functions
export const taskApi = {
  list: async (userId?: string) => {
    const url = userId ? `/api/tasks/user/${userId}` : '/api/tasks';
    const response = await api.get<Task[]>(url);
    return response.data;
  },

  get: async (taskId: string) => {
    const response = await api.get<Task>(`/api/tasks/${taskId}`);
    return response.data;
  },

  create: async (data: Partial<Task>) => {
    const response = await api.post<Task>('/api/tasks', data);
    return response.data;
  },

  updateProgress: async (taskId: string, progress: number) => {
    const response = await api.put<Task>(`/api/tasks/${taskId}/progress`, { progress });
    return response.data;
  },

  updateStatus: async (taskId: string, status: Task['status']) => {
    const response = await api.put<Task>(`/api/tasks/${taskId}/status`, { status });
    return response.data;
  },

  delete: async (taskId: string) => {
    await api.delete(`/api/tasks/${taskId}`);
  },
};

export const userApi = {
  list: async () => {
    const response = await api.get<User[]>('/api/users');
    return response.data;
  },
};

export const sessionApi = {
  list: async (userId?: string) => {
    const url = userId ? `/api/sessions/user/${userId}` : '/api/sessions';
    const response = await api.get<Session[]>(url);
    return response.data;
  },
};

export const promptApi = {
  list: async () => {
    const response = await api.get<Prompt[]>('/api/admin/prompts');
    return response.data;
  },

  get: async (name: string) => {
    const response = await api.get<Prompt>(`/api/admin/prompts/${name}`);
    return response.data;
  },

  update: async (data: Partial<Prompt>) => {
    const response = await api.post<Prompt>('/api/admin/prompts', data);
    return response.data;
  },

  delete: async (name: string) => {
    await api.delete(`/api/admin/prompts/${name}`);
  },
};

export const errorLogApi = {
  list: async (limit: number = 100) => {
    const response = await api.get<ErrorLog[]>(`/api/logs/errors?limit=${limit}`);
    return response.data;
  },
};

export default api;
