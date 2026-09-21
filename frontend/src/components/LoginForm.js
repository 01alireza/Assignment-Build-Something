import React, { useState } from 'react';
import api from '../api/client';

function LoginForm({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      let response;
      if (isRegistering) {
        response = await api.post('/api/users/register', { username, password });
      } else {
        response = await api.post('/api/users/login', { username, password });
      }

      const { token } = response.data;
      localStorage.setItem('token', token);
      localStorage.setItem('username', username);
      onLogin({ username, token });
    } catch (err) {
      const message = err.response?.data?.error
        || (isRegistering ? 'Registration failed' : 'Login failed');
      setError(message);
      console.error(err);
    }
  };

  return (
    <div className="card login-form">
      <h2>{isRegistering ? 'Register' : 'Login'}</h2>
      {error && <div className="error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary">
          {isRegistering ? 'Register' : 'Login'}
        </button>
        <button
          type="button"
          className="btn"
          style={{marginLeft: '10px', background: '#ecf0f1'}}
          onClick={() => setIsRegistering(!isRegistering)}
        >
          {isRegistering ? 'Already have an account? Login' : 'Need an account? Register'}
        </button>
      </form>
    </div>
  );
}

export default LoginForm;
