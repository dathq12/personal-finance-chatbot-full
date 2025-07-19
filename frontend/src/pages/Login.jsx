import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

import LogoIcon from '../components/Authen/LogoIcon';
import AuthHeader from '../components/Authen/AuthHeader';
import TextInput from '../components/Authen/TextInput';
import CheckboxWithLabel from '../components/Authen/CheckboxWithLabel';
import SubmitButton from '../components/Authen/SubmitButton';
import AuthFooter from '../components/Authen/AuthFooter';



const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      // const res = await API.post('/auth/login', { email, password });
      // localStorage.setItem('token', res.data.token);
      navigate('/chatbot');
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng nhập thất bại.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow">
        <LogoIcon />
        <AuthHeader title="Chào mừng trở lại" />

        {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <TextInput type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <TextInput type="password" placeholder="Mật khẩu" value={password} onChange={(e) => setPassword(e.target.value)} />

          <div className="flex items-center justify-between">
            <CheckboxWithLabel label="Ghi nhớ tôi" checked={rememberMe} onChange={() => setRememberMe(!rememberMe)} />
            <a href="/forgot-password" className="text-sm text-blue-600 hover:underline">Quên mật khẩu?</a>
          </div>

          <SubmitButton label="Đăng Nhập" />
        </form>

        <p className="text-center text-sm text-gray-600 mt-6">
          <AuthFooter question="Chưa có tài khoản?" linkText="Đăng ký" linkHref="/register" />
        </p>
      </div>
    </div>
  );
};

export default Login;
