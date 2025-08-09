import { useState } from 'react';
import Layout from '../components/Layout/Layout';
import { FiFilter, FiPlus, FiSearch } from 'react-icons/fi';

const ManualEntry = () => {
  const [type, setType] = useState('Thu');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [note, setNote] = useState('');
  const [dateTime, setDateTime] = useState(new Date().toISOString().slice(0, 16));
  const [entries, setEntries] = useState([]);

  const handleSave = () => {
    const newEntry = {
      id: Date.now(),
      type,
      amount,
      category,
      note,
      dateTime,
    };
    setEntries([newEntry, ...entries]);
    setAmount('');
    setCategory('');
    setNote('');
    setDateTime(new Date().toISOString().slice(0, 16));
  };

  return (
    <Layout>
      <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Transactions</h1>
          <div className="space-x-2">
            <button className="bg-white text-black px-4 py-2 rounded flex items-center gap-1">
              <FiSearch /> Export
            </button>
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
              type="text"
              placeholder="Search transactions..."
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
            />
            <select className="px-3 py-2 rounded bg-[#121212] border border-gray-700">
              <option>All Categories</option>
            </select>
            <select className="px-3 py-2 rounded bg-[#121212] border border-gray-700">
              <option>All Types</option>
            </select>
            <input
              type="date"
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
            />
          </div>
          <div className="flex gap-2 pt-2">
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center gap-1">
              <FiFilter /> Apply Filters
            </button>
            <button className="px-4 py-2 border border-gray-600 rounded">Reset</button>
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
                    <tr key={entry.id} className="border-b border-gray-800">
                      <td>{entry.note}</td>
                      <td>{entry.category}</td>
                      <td>{new Date(entry.dateTime).toLocaleDateString()}</td>
                      <td>{entry.amount}₫</td>
                      <td>{entry.type}</td>
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
