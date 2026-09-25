import React from 'react';

function TaskList({ tasks, onDelete, onEdit }) {
  if (tasks.length === 0) {
    return <div className="empty-state">No tasks yet. Add one above!</div>;
  }

  return (
    <ul className="task-list">
      {tasks.map(task => (
        <li key={task.id} className="task-item">
          <div>
            <h3>{task.title}</h3>
            {task.description && <p>{task.description}</p>}
            <small style={{ color: '#999' }}>
              Created: {new Date(task.created_at).toLocaleString()}
            </small>
          </div>
          <div className="task-actions">
            <button
              onClick={() => onEdit(task)}
              className="btn btn-primary"
            >
              Edit
            </button>
            <button
              onClick={() => onDelete(task.id)}
              className="btn btn-danger"
            >
              Delete
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

export default TaskList;
