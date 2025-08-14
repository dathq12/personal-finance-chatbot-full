import React, { useState } from 'react';
import Layout from '../components/Layout/Layout';
import LogoIcon from '../components/ui/LogoIcon';

const Account = () => {
  const [user, setUser] = useState({
    name: 'Hà Quang Đạt',
    email: 'dathq12@gmail.com',
    phone: '0123 456 789',
  });

  const [isEditing, setIsEditing] = useState(false);

  const handleChange = (e) => {
    setUser({ ...user, [e.target.name]: e.target.value });
  };

  const handleSave = () => {
    setIsEditing(false);
    // Gọi API lưu thông tin nếu cần
  };

  return (
    <Layout>
        <div className="flex flex-col flex-1 bg-black px-6 py-8 text-left">
      <h2 className="text-2xl font-bold text-white mb-6">Tài khoản của bạn</h2>

      {/* Avatar + info */}
      <div className="flex items-center space-x-4 mb-8">
        <LogoIcon/>
        <div>
          <p className="text-lg font-semibold text-white">{user.name}</p>
          <p className="text-sm text-gray-500">{user.email}</p>
        </div>
      </div>

      {/* Form thông tin */}
      <div className="space-y-5 max-w-md">
        <div>
          <label className="block text-sm font-medium text-white mb-1">Họ tên</label>
          <input
            name="name"
            value={user.name}
            onChange={handleChange}
            disabled={!isEditing}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1">Email</label>
          <input
            name="email"
            value={user.email}
            onChange={handleChange}
            disabled={!isEditing}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-white mb-1">Số điện thoại</label>
          <input
            name="phone"
            value={user.phone}
            onChange={handleChange}
            disabled={!isEditing}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Nút */}
      <div className="mt-8">
        {isEditing ? (
          <button
            onClick={handleSave}
            className="bg-blue-600 text-white px-5 py-2 rounded-md hover:bg-blue-700"
          >
            Lưu thay đổi
          </button>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="bg-gray-200 text-gray-800 px-5 py-2 rounded-md hover:bg-gray-300"
          >
            Chỉnh sửa
          </button>
        )}
      </div>
    </div>
    </Layout>
  );
};

export default Account;
