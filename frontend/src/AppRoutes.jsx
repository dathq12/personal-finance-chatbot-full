// AppRoutes.jsx
import React from "react";
import { Routes, Route } from "react-router-dom";

// import Login from "./pages/Login-co.jsx";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login.jsx";
import Chatbot from "./pages/Chatbot.jsx";
import ManualEntry from "./pages/ManualEntry.jsx";
import ReportPage from "./pages/Reports.jsx"
import Dashboard from "./pages/Dashboard.jsx"
import Account from "./pages/Account.jsx"

function AppRoutes() {
  return (
    <Routes>
      {/* Finance App Routes */}
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/chatbot" element={<Chatbot />} />
      <Route path="/manual-input" element={<ManualEntry />} />
      <Route path="/reports" element={<ReportPage />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/account" element={<Account />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default AppRoutes;
