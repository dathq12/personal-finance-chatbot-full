import { Routes, Route } from 'react-router-dom';

import Login from './pages/Login.jsx'; // Trang login mặc định
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Chatbot from './pages/Chatbot';
import Dashboard from './pages/Dashboard';
import NotFound from './pages/NotFound';

// Các trang chatbot UI (từ converted JSX)
import Locale from "./pages/Home.jsx";
import Workspace from "./pages/Workspace.jsx";
import Chat from "./pages/Chat.jsx";
import ChatDetail from "./pages/ChatDetail.jsx";
import Help from "./pages/Help.jsx";
import LocaleLogin from "./pages/Login.jsx";           // 🔁 đổi tên tránh trùng
import Password from "./pages/ChangePassword.jsx";
import Setup from "./pages/Setup.jsx";

function AppRoutes() {
  return (
    <Routes>
      {/* Các route gốc của ứng dụng tài chính */}
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/chatbot" element={<Chatbot />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="*" element={<NotFound />} />

      {/* Các route mở rộng từ chatbot-ui-main */}
      <Route path="/:locale" element={<Locale />} />
      <Route path="/:locale/:workspaceid" element={<Workspace />} />
      <Route path="/:locale/:workspaceid/chat" element={<Chat />} />
      <Route path="/:locale/:workspaceid/chat/:chatid" element={<ChatDetail />} />
      <Route path="/:locale/help" element={<Help />} />
      <Route path="/:locale/login" element={<LocaleLogin />} />
      <Route path="/:locale/login/password" element={<Password />} />
      <Route path="/:locale/setup" element={<Setup />} />
    </Routes>
  );
}

export default AppRoutes;
