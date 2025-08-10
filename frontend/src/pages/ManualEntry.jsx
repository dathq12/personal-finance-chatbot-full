import { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import { useNavigate } from "react-router-dom";
import { FiFilter, FiPlus, FiSearch } from 'react-icons/fi';

const ManualEntry = () => {
  const navigate = useNavigate();

  // State entries lấy từ API
  const [entries, setEntries] = useState([]);

  // State filter
  const [filters, setFilters] = useState({
    search: '',
    category_display_name: '',
    transaction_type: '',
    date_from: '',
    date_to: '',
    // Bạn có thể thêm các filter khác nếu cần
  });

  // Hàm gọi API lấy dữ liệu transactions theo filter
  const fetchTransactions = async () => {
    try {
      const token = sessionStorage.getItem("token");

      // Build query params từ filters
      const params = new URLSearchParams();

      if (filters.transaction_type) params.append('transaction_type', filters.transaction_type);
      if (filters.category_display_name) params.append('category_display_name', filters.category_display_name);
      if (filters.search) params.append('search', filters.search);
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
      // Bạn có thể thêm các tham số khác nếu API cần

      // Mặc định các param khác theo ví dụ của bạn
      params.append('payment_method', 'cash');
      params.append('location', 'Hà Nội');
      params.append('created_by', 'manual');
      params.append('skip', '0');
      params.append('limit', '10');
      params.append('sort_by', 'created_at');
      params.append('sort_order', 'desc');

      const res = await fetch(`http://127.0.0.1:8000/transactions/?${params.toString()}`, {
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!res.ok) throw new Error(`Error: ${res.status}`);

      const data = await res.json();
      console.log("API data:", data);

      // Giả sử API trả về mảng data
      setEntries(data.transaction || []);
    } catch (error) {
      console.error("Failed to fetch transactions:", error);
      setEntries([]);
    }
  };

  // Handle thay đổi filter input
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Khi nhấn nút Apply Filters thì gọi API
  const handleApplyFilters = () => {
    fetchTransactions();
  };

  // Điều hướng tới trang tạo transaction mới
  const handleSave = () => {
    navigate("/create/transaction");
  };

  // Optionally, load data lần đầu khi component mount
  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <Layout>
      <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Transactions</h1>
          <div className="flex space-x-2">
            <button onClick={handleSave} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-1">
              <FiPlus /> Add Transaction
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-[#1e1e1e] p-4 rounded space-y-4">
          <h2 className="text-lg font-semibold">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <input
              name="search"
              value={filters.search}
              onChange={handleFilterChange}
              type="text"
              placeholder="Search transactions..."
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
            />
            <select
              name="category_display_name"
              value={filters.category_display_name}
              onChange={handleFilterChange}
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
            >
              <option value="">All Categories</option>
              <option value="Thu nhập">Thu nhập</option>
              <option value="Chi tiêu">Chi tiêu</option>
              {/* Thêm option category nếu bạn có */}
            </select>
            <select
              name="transaction_type"
              value={filters.transaction_type}
              onChange={handleFilterChange}
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
            >
              <option value="">All Types</option>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
              {/* Thêm các loại khác nếu có */}
            </select>
            <input
              name="date_from"
              value={filters.date_from}
              onChange={handleFilterChange}
              type="date"
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
              placeholder="Date from"
            />
            <input
              name="date_to"
              value={filters.date_to}
              onChange={handleFilterChange}
              type="date"
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
              placeholder="Date to"
            />
          </div>
          <div className="flex gap-2 pt-2">
            <button
              onClick={handleApplyFilters}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-1"
            >
              <FiFilter /> Apply Filters
            </button>
            <button
              onClick={() => setFilters({
                search: '',
                category_display_name: '',
                transaction_type: '',
                date_from: '',
                date_to: '',
              })}
              className="px-4 py-2 border border-gray-600 rounded"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Transaction Table */}
        <div className="bg-[#1e1e1e] p-4 rounded">
          <div className="flex gap-2 mb-4">
            <button className="bg-gray-800 px-4 py-2 rounded">List View</button>
            <button className="bg-gray-700 px-4 py-2 rounded text-gray-400">Categories</button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b border-gray-700">
                  <th className="pb-2">Description</th>
                  <th>Category</th>
                  <th>Date</th>
                  <th>Amount</th>
                  <th>Type</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {entries.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center text-gray-500 py-6">
                      No transactions found matching your filters.
                    </td>
                  </tr>
                ) : (
                  entries.map((entry) => (
                    <tr key={entry.TransactionID} className="border-b border-gray-800">
                      <td>{entry.description || entry.notes}</td>
                      <td>{entry.category_display_name}</td>
                      <td>{new Date(entry.transaction_date).toLocaleDateString()}</td>
                      <td>{parseFloat(entry.amount).toLocaleString()}₫</td>
                      <td>{entry.transaction_type}</td>
                      <td>
                        <button className="text-red-500 text-xs">Delete</button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ManualEntry;
