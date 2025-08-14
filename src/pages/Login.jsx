import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import { useEffect } from 'react';

import LogoIcon from '../components/ui/LogoIcon';
import AuthHeader from '../components/Authen/AuthHeader';
import TextInput from '../components/Authen/TextInput';
import CheckboxWithLabel from '../components/Authen/CheckboxWithLabel';
import SubmitButton from '../components/Authen/SubmitButton';
import AuthFooter from '../components/Authen/AuthFooter';
import { Input } from '../components/ui/input';



const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();


const account = { email, password };

// Lấy ra trong useEffect
useEffect(() => {
  const saved = localStorage.getItem('rememberedAccount');
  console.log(saved);
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      setEmail(parsed.email);
      setPassword(parsed.password);
      setRememberMe(true);
    } catch (err) {
      console.error("rememberedAccount không phải JSON hợp lệ:", err);
      localStorage.removeItem('rememberedAccount'); // xoá dữ liệu cũ hỏng
    }
  }
}, []);

  //   useEffect(() => {
  //   const saved  = localStorage.getItem('rememberedAccount');
  //   if (saved) {
  //     const parsed = JSON.parse(atob(saved));
  //     setEmail(parsed.email);
  //     setPassword(parsed.password);
  //     setRememberMe(true);
  //   }
  // }, []);

  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (rememberMe) {
      // const encoded = btoa(JSON.stringify({ email, password }));
      localStorage.setItem('rememberedAccount', JSON.stringify(account));
      
    } else {
      localStorage.removeItem('rememberedAccount');
    }


    try {
      const res = await API.post('/auth/login', { email, password });
      sessionStorage.setItem("token", res.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng nhập thất bại.');
    }
  };

  return (
    <div className="h-dvh p-6 bg-black text-white  space-y-6 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-[#1e1e1e] p-8 rounded-xl shadow">
        <div className="flex items-end justify-center space-x-2 mb-6">
          <LogoIcon className="w-8 h-8" />
          <h1 className="text-xl font-bold flex items-center gap-1">
            AI FinanceManager xin chào
            <span className="text-2xl">👋</span>
          </h1>
        </div>
        

        {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input type="password" placeholder="Mật khẩu" value={password} onChange={(e) => setPassword(e.target.value)} />

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
