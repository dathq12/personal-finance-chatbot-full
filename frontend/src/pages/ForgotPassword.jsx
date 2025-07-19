import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

import LogoIcon from '../components/Authen/LogoIcon';
import AuthHeader from '../components/Authen/AuthHeader';
import TextInput from '../components/Authen/TextInput';
import SubmitButton from '../components/Authen/SubmitButton';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    try {
      await API.post('/auth/forgot-password', { email });
      setSuccessMsg('Liên kết khôi phục đã được gửi đến email của bạn.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Không thể gửi liên kết khôi phục.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow">
        <LogoIcon />
        <AuthHeader title="Quên mật khẩu? 🔒" />

        {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
        {successMsg && <p className="text-green-600 text-sm text-center mb-4">{successMsg}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <TextInput
            type="email"
            placeholder="Địa chỉ email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <SubmitButton label="Gửi liên kết khôi phục" />
        </form>

        <div className="text-sm text-center text-blue-600 mt-6">
          <a href="/login" className="hover:underline">← Quay lại đăng nhập</a>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
