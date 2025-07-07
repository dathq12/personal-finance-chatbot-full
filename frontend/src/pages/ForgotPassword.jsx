import API from '../services/api'; // Đảm bảo bạn đã tạo file này
import { useState } from 'react';





const ForgotPassword = () => {
  {error && <p style={{ color: 'red' }}>{error}</p>}
{success && <p style={{ color: 'green' }}>{success}</p>}

const [message, setMessage] = useState('');
const [error, setError] = useState('');

  const [email, setEmail] = useState('');

  const handleSubmit = async (e) => {
  e.preventDefault();
  setMessage('');
  setError('');

  try {
    const response = await API.post('/auth/forgot-password', { email });
    console.log('Reset email sent:', response.data);
    setMessage('Chúng tôi đã gửi hướng dẫn đặt lại mật khẩu đến email của bạn.');
  } catch (err) {
    console.error('Forgot password error:', err);
    setError(err.response?.data?.detail || 'Không thể gửi yêu cầu đặt lại mật khẩu.');
  }
    };

  return (
    <div>
      <h2>Quên mật khẩu</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <button type="submit">Gửi yêu cầu</button>
      </form>
    </div>
  );
};

export default ForgotPassword;
