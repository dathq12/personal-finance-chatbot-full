import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';

import LogoIcon from '../components/ui/LogoIcon';
import AuthHeader from '../components/Authen/AuthHeader';
import TextInput from '../components/Authen/TextInput';
import CheckboxWithLabel from '../components/Authen/CheckboxWithLabel';
import SubmitButton from '../components/Authen/SubmitButton';
import AuthFooter from '../components/Authen/AuthFooter';
import { Input } from '../components/ui/input';

const Register = () => {
  const [full_name, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [agree, setAgree] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await API.post('/auth/register', {
        full_name,
        email,
        password,
      });

      // Giả sử trả token sau khi đăng ký thành công
      localStorage.setItem('token', response.data.token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng ký thất bại.');
    }
  };

  return (
    <div className="p-6 bg-black text-white min-h-screen space-y-6 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-[#121212] p-8 rounded-xl shadow">
        <div className="flex items-end justify-center space-x-2 mb-6">
          <LogoIcon />
          <AuthHeader title="Tạo tài khoản mới ✨" />
        </div>


        {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            type="text"
            placeholder="Họ và tên"
            value={full_name}
            onChange={(e) => setFullName(e.target.value)}
          />
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <CheckboxWithLabel
            label="Mật khẩu"
            checked={agree}
            onChange={() => setAgree(!agree)}
          />

          <SubmitButton label="Tạo tài khoản" />
        </form>

        <AuthFooter
          question="Đã có tài khoản"
          linkText="Đăng nhập"
          linkHref="/login"
        />
      </div>
    </div>
  );
};

export default Register;
