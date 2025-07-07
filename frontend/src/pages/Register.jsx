import React, { useState } from 'react';
import API from '../services/api';

const Register = () => {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({ email: '', password: '' });

  const handleChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await API.post('/auth/register', formData);
      console.log('Register success:', response.data);
      setSuccess('Đăng ký thành công!');
    } catch (err) {
      console.error('Register error:', err);
      setError(err.response?.data?.detail || 'Đã có lỗi xảy ra khi đăng ký');
    }
  };

  return (
    <div>
      <h2>Đăng ký</h2>

      {/* ✅ HIỂN THỊ THÔNG BÁO SAU KHI ĐÃ KHAI BÁO STATE */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}

      <form onSubmit={handleSubmit}>
        <input name="email" type="email" placeholder="Email" onChange={handleChange} />
        <input name="password" type="password" placeholder="Mật khẩu" onChange={handleChange} />
        <button type="submit">Đăng ký</button>
      </form>
    </div>
  );
};

export default Register;
