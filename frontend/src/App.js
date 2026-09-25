import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import LoginForm from './components/LoginForm';
import api from './api/client';

function App() {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [editingTask, setEditingTask] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check if user is logged in (simple token check)
  useEffect(() => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    if (token && username) {
      setUser({ username, token });
    }
  }, []);

  // Fetch tasks when user logs in
  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user]);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/api/tasks');
      setTasks(response.data);
    } catch (err) {
      setError('Failed to load tasks. Is the task-service running?');
      console.error(err);
    }
    setLoading(false);
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setUser(null);
    setTasks([]);
    setEditingTask(null);
  };

  const handleAddTask = async (taskData) => {
    try {
      const response = await api.post('/api/tasks', taskData);
      setTasks([...tasks, response.data]);
    } catch (err) {
      setError('Failed to add task');
      console.error(err);
    }
  };

  const handleUpdateTask = async (taskData) => {
    try {
      const response = await api.put(`/api/tasks/${editingTask.id}`, taskData);
      setTasks(currentTasks => currentTasks.map(task => (
        task.id === editingTask.id ? response.data : task
      )));
      setEditingTask(null);
    } catch (err) {
      setError('Failed to update task');
      console.error(err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await api.delete(`/api/tasks/${taskId}`);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (err) {
      setError('Failed to delete task');
      console.error(err);
    }
  };

  if (!user) {
    return (
      <div className="container">
        <LoginForm onLogin={handleLogin} />
      </div>
    );
  }

  return (
    <div className="container">
      <Navbar user={user} onLogout={handleLogout} />

      <div className="card">
        <h2>{editingTask ? 'Edit Task' : 'Add New Task'}</h2>
        <TaskForm
          onSubmit={editingTask ? handleUpdateTask : handleAddTask}
          initialTask={editingTask}
          submitLabel={editingTask ? 'Save Changes' : 'Add Task'}
          onCancel={editingTask ? () => setEditingTask(null) : undefined}
        />
      </div>

      <div className="card">
        <h2>Your Tasks</h2>
        {error && <div className="error">{error}</div>}
        {loading ? (
          <div className="loading">Loading tasks...</div>
        ) : (
          <TaskList
            tasks={tasks}
            onDelete={handleDeleteTask}
            onEdit={setEditingTask}
          />
        )}
      </div>
    </div>
  );
}

export default App;
