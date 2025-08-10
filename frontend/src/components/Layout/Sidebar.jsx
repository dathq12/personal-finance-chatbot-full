import { FiHome, FiUsers, FiCreditCard, FiDollarSign, FiFileText, FiBarChart2, FiMessageSquare, FiSettings } from 'react-icons/fi';
import { useLocation, Link } from 'react-router-dom';

const navItems = [
  { icon: FiBarChart2, label: 'Dashboard', path: '/dashboard', color: 'text-blue-400' },
  { icon: FiMessageSquare, label: 'Chatbot', path: '/chatbot', color: 'text-pink-400' },
  { icon: FiCreditCard, label: 'Transactions', path: '/manual-input', color: 'text-green-400' },
  { icon: FiDollarSign, label: 'Budgets', path: '/budget', color: 'text-yellow-400' },
  // { icon: FiBarChart2, label: 'Analytics', path: '/analytics', color: 'text-purple-400' },
  { icon: FiSettings, label: 'Settings', path: '/settings', color: 'text-gray-400' },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-64 h-screen bg-[#1e1e1e] text-white flex flex-col justify-between">
      <div>
        <h1 className="text-xl font-bold px-4 py-6">FinanceManager</h1>
        <nav className="space-y-1">
          {navItems.map(({ icon: Icon, label, path, color }) => {
            const isActive = location.pathname === path;
            return (
              <Link
                key={label}
                to={path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg mx-2 ${
                  isActive ? 'bg-[#333] text-white' : 'text-gray-400 hover:bg-[#2c2c2e]'
                }`}
              >
                <Icon className={`text-lg ${color}`} />
                <span>{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="flex items-center gap-3 px-4 py-4 text-sm border-t border-gray-700">
        <div className="bg-gray-700 p-2 rounded-full">
          <FiUsers className="text-white" />
        </div>
        <div>
          <div className="font-semibold">John Doe</div>
          <div className="text-gray-400 text-xs">Admin</div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
