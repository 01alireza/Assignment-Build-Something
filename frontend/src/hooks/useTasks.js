import { useState, useEffect } from 'react';
import api from '../api/client';

export function useTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/tasks');
      setTasks(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch tasks');
    }
    setLoading(false);
  };

  const addTask = async (taskData) => {
    try {
      const response = await api.post('/api/tasks', taskData);
      setTasks([...tasks, response.data]);
      return true;
    } catch (err) {
      setError('Failed to add task');
      return false;
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await api.delete(`/api/tasks/${taskId}`);
      setTasks(tasks.filter(t => t.id !== taskId));
      return true;
    } catch (err) {
      setError('Failed to delete task');
      return false;
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return { tasks, loading, error, fetchTasks, addTask, deleteTask };
}
