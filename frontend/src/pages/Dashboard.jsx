import { useState } from 'react';
import Layout from '../components/Layout/Layout';
import { FiUsers, FiFileText, FiDownload, FiPlus, FiTrendingUp, FiTrendingDown, FiUser } from 'react-icons/fi';
import { FaChartPie } from 'react-icons/fa';

const Dashboard = () => {



    return (
        <Layout>
                <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="space-x-2">
          <button className="bg-white text-black px-4 py-2 rounded">Export</button>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">Add Transaction</button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-3 gap-4">
        {[
          { label: 'Total Balance', value: '$12,546.00', sub: '+2.5% from last month' },
          { label: 'Income', value: '$4,935.00', sub: '+10.1% from last month' },
          { label: 'Expenses', value: '$2,463.00', sub: '+7.2% from last month' },
        ].map(({ label, value, sub }, i) => (
          <div key={i} className="bg-[#1e1e1e] p-4 rounded shadow">
            <div className="text-gray-400 text-sm">{label}</div>
            <div className="text-xl font-semibold">{value}</div>
            <div className="text-green-500 text-sm">{sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent Transactions */}
        <div className="bg-[#1e1e1e] p-4 rounded">
          <h2 className="text-lg font-semibold mb-1">Recent Transactions</h2>
          <p className="text-sm text-gray-400 mb-4">Your most recent financial activities</p>
          <ul className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <li key={i} className="flex justify-between border-b border-gray-700 pb-2">
                <div>
                  <div className="font-medium">Grocery Shopping</div>
                  <div className="text-xs text-gray-500">July {21 + i}, 2025</div>
                </div>
                <div className="text-right">
                  <div className="text-red-500 font-semibold">-${(84.1 + i * 0.1).toFixed(2)}</div>
                  <div className="text-xs text-gray-500">Food</div>
                </div>
              </li>
            ))}
          </ul>
          <button className="w-full text-center text-sm text-blue-400 mt-3">View all transactions</button>
        </div>

        {/* Budget Status */}
        <div className="bg-[#1e1e1e] p-4 rounded">
          <h2 className="text-lg font-semibold mb-1">Budget Status</h2>
          <p className="text-sm text-gray-400 mb-4">Your current budget utilization</p>
          {[
            { name: 'Food', percent: 75, color: 'bg-white' },
            { name: 'Transportation', percent: 50, color: 'bg-white' },
            { name: 'Entertainment', percent: 90, color: 'bg-red-500' },
            { name: 'Utilities', percent: 30, color: 'bg-white' },
          ].map(({ name, percent, color }) => (
            <div key={name} className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>{name}</span>
                <span>{percent}%</span>
              </div>
              <div className="w-full h-2 bg-gray-700 rounded">
                <div
                  className={`${color} h-2 rounded`}
                  style={{ width: `${percent}%` }}
                ></div>
              </div>
            </div>
          ))}
          <button className="w-full text-center text-sm text-blue-400">View all budgets</button>
        </div>
      </div>

      
    </div>

        </Layout>
    )
}

export default Dashboard