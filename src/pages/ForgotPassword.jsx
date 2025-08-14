import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

import LogoIcon from '../components/ui/LogoIcon';
import AuthHeader from '../components/Authen/AuthHeader';
import TextInput from '../components/Authen/TextInput';
import SubmitButton from '../components/Authen/SubmitButton';
import { Input } from '../components/ui/input';

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
    <div className="h-dvh p-6 bg-black text-white  space-y-6 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-[#1e1e1e] p-8 rounded-xl shadow">
        <div className="flex items-end justify-center space-x-2 mb-6">
          <LogoIcon />
          <AuthHeader title="Quên mật khẩu? 🔒" />
        </div>
        {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
        {successMsg && <p className="text-green-600 text-sm text-center mb-4">{successMsg}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
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
