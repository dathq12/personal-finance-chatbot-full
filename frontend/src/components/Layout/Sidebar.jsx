import { FiHome, FiMessageSquare, FiEdit2, FiBarChart2 } from 'react-icons/fi';
import { useLocation, Link } from 'react-router-dom';

const navItems = [
  { icon: FiHome, label: 'Dashboard', path: '/dashboard' },
  { icon: FiMessageSquare, label: 'Chatbot tài chính cá nhân', path: '/chatbot' },
  { icon: FiEdit2, label: 'Nhập Thu/Chi Thủ Công', path: '/manual-input' },
  { icon: FiBarChart2, label: 'Báo Cáo Tài Chính', path: '/reports' },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-64 bg-white shadow-sm border-r p-4">
      <nav className="space-y-2 text-sm font-medium text-gray-700">
        {navItems.map(({ icon: Icon, label, path }) => (
          <Link
            to={path}
            key={label}
            className={`flex items-center gap-2 p-2 rounded-lg ${
              location.pathname === path
                ? 'bg-gray-100 text-blue-600'
                : 'hover:bg-gray-100'
            }`}
          >
            <Icon size={18} />
            <span>{label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
