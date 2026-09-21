import React from 'react';

function Navbar({ user, onLogout }) {
  return (
    <header>
      <h1>📋 Task Manager</h1>
      <p>Welcome, {user.username}! 
        <button onClick={onLogout} className="btn btn-danger" style={{marginLeft: '15px'}}>
          Logout
        </button>
      </p>
    </header>
  );
}

export default Navbar;
