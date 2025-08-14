// src/pages/NotFound.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6">
      <div style={styles.container}>
        <h1 style={styles.code}>404</h1>
        <p style={styles.message}>Trang bạn tìm kiếm không tồn tại.</p>
        <Link to="/dashboard" style={styles.link}>Quay về trang chủ</Link>
      </div>
    </div>
  );
}

const styles = {
  container: {
    textAlign: 'center',
    padding: '100px 20px',
    fontFamily: 'Arial, sans-serif',
  },
  code: {
    fontSize: '100px',
    margin: '0',
    color: '#e74c3c',
  },
  message: {
    fontSize: '24px',
    margin: '20px 0',
    color: '#ffffffff',
  },
  link: {
    textDecoration: 'none',
    color: '#3498db',
    fontSize: '18px',
  }
};

export default NotFound;
