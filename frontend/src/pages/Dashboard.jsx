import { useState } from 'react';
import Layout from '../components/Layout/Layout';
import { FiUsers, FiFileText, FiDownload, FiPlus, FiTrendingUp, FiTrendingDown, FiUser, FiFilter } from 'react-icons/fi';
import { FaChartPie } from 'react-icons/fa';
import React from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import Select from "../components/ui/selection";
import API from "../services/api"
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  // const today = new Date().toISOString().split("T")[0];
  const [dataStatitis, setDataStatitis] = useState(null);

  // State filter
  const [filters, setFilters] = useState({
    date_from: '',
    date_to: '',
    // Bạn có thể thêm các filter khác nếu cần
  });

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Khi nhấn nút Apply Filters thì gọi API
  const handleApplyFilters = () => {
    getTransactionStatistics();
  };

  const navigate = useNavigate();

  const getTransactionStatistics = async () => {
    try {
      const params = new URLSearchParams();

      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);

      const token = sessionStorage.getItem("token");
      const res = await API.get(
        `/transactions/summary/statistics?${params.toString()}`,
        {
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("Transaction statistics:", res.data);
      setDataStatitis(res.data);
      return res.data; // axios trả data trực tiếp ở đây

    } catch (error) {
      console.error("Error fetching transaction statistics:", error);
    }
  };

  // State entries lấy từ API
  const [entries, setEntries] = useState([]);

  // Hàm gọi API lấy dữ liệu transactions theo filter
  const fetchTransactions = async () => {
    try {
      const token = sessionStorage.getItem("token");

      // Build query params từ filters
      const params = new URLSearchParams();

      // if (filters.transaction_type) params.append('transaction_type', filters.transaction_type);
      // if (filters.category_display_name) params.append('category_display_name', filters.category_display_name);
      // if (filters.search) params.append('search', filters.search);
      // if (filters.date_from) params.append('date_from', filters.date_from);
      // if (filters.date_to) params.append('date_to', filters.date_to);
      // Bạn có thể thêm các tham số khác nếu API cần

      // // Mặc định các param khác theo ví dụ của bạn
      // params.append('payment_method', 'cash');
      // params.append('location', 'Hà Nội');
      // params.append('created_by', 'manual');
      params.append('skip', '0');
      params.append('limit', '5');
      params.append('sort_by', 'CreatedAt');
      params.append('sort_order', 'asc');


      const res = await API.get(`/transactions/?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json',
        }
      });
      const data = res.data;
      console.log("API data:", data);


      // Giả sử API trả về mảng data
      setEntries(res.data.transaction || []);
      console.log('Entries set:', res.data.transaction);
    } catch (error) {
      console.error("Failed to fetch transactions:", error);
      setEntries([]);
    }
  };

  useEffect(() => {
    getTransactionStatistics();
    fetchTransactions();
  }, []);


  return (
    <Layout>
      <div className="h-dvh bg-[#121212] text-white p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <div className="space-x-2">
            {/* <button className="bg-white text-black px-4 py-2 rounded">Export</button> */}
            {/* <button
              type="button"
              onClick={() => {
                navigate("/create/transaction");
                console.log("Button Cancel clicked");
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">Add Transaction</button> */}
          </div>
        </div>

        <div className="bg-[#1e1e1e] p-4 rounded space-y-4">
          <h2 className="flex flex-row text-lg font-semibold">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">

            <input
              type="text"
              name="date_from"
              value={filters.date_from}
              onChange={handleFilterChange}
              placeholder="Date from"
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
              onFocus={(e) => e.target.type = "date"}
              onBlur={(e) => e.target.type = "text"}
            />
            <input
              type="text"
              name="date_to"
              value={filters.date_to}
              onChange={handleFilterChange}
              className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
              placeholder="Date to"
              onFocus={(e) => e.target.type = "date"}
              onBlur={(e) => e.target.type = "text"}
            />

            <div className="flex gap-2 pt-1">
              <button
                onClick={handleApplyFilters}
                className=" bg-blue-600 hover:bg-blue-700 text-white px-4 rounded flex items-center gap-1"
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
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-[#111] text-green-400">
            <CardContent className="p-4">
              <p>Total Income</p>
              <p className="text-xl font-bold">${dataStatitis?.total_income?.toLocaleString() ?? 0}</p>
              <p className="text-xs text-green-300">+12.5% from last period</p>
            </CardContent>
          </Card>
          <Card className="bg-[#111] text-red-400">
            <CardContent className="p-4">
              <p>Total Expenses</p>
              <p className="text-xl font-bold">${dataStatitis?.total_expense?.toLocaleString() ?? 0}</p>
              <p className="text-xs text-red-300">-8.2% from last period</p>
            </CardContent>
          </Card>
          <Card className="bg-[#111] text-green-400">
            <CardContent className="p-4">
              <p>Net Income</p>
              <p className="text-xl font-bold">${dataStatitis?.net_amount?.toLocaleString() ?? 0}</p>
              <p className="text-xs text-green-300">+24.1% from last period</p>
            </CardContent>
          </Card>
          <Card className="bg-[#111] text-white">
            <CardContent className="p-4">
              <p>Savings Rate</p>
              {dataStatitis?.total_income ? (
                <>
                  {(() => {
                    const savingsRate = ((dataStatitis.total_income - dataStatitis.total_expense) / dataStatitis.total_income) * 100;
                    const displayRate = savingsRate.toFixed(2) + '%';
                    const barWidth = Math.min(Math.max(savingsRate, 0), 100) + '%'; // giới hạn 0-100%
                    return (
                      <>
                        <p className="text-xl font-bold">{displayRate}</p>
                        <div className="w-full bg-gray-700 h-2 rounded mt-2">
                          <div className="h-2 bg-green-400 rounded" style={{ width: barWidth }}></div>
                        </div>
                      </>
                    );
                  })()}
                </>
              ) : (
                <>
                  <p className="text-xl font-bold">100%</p>
                  <div className="w-full bg-gray-700 h-2 rounded mt-2">
                    <div className="h-2 bg-green-400 rounded" style={{ width: '100%' }}></div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Stats Cards */}
        {/* <div className="grid grid-cols-1 md:grid-cols-1 lg:grid-cols-3 gap-4">
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
        </div> */}

        <div className="grid grid-cols-1 lg:grid-cols-1 gap-4">
          {/* Recent Transactions */}
          <div className="bg-[#1e1e1e] p-4 rounded">
            <h2 className="text-lg font-semibold mb-1">Recent Transactions</h2>
            <p className="text-sm text-gray-400 mb-4">Your most recent financial activities</p>
            <ul className="space-y-3">
              {entries.slice(0, 5).map((entry) => (
                <li key={entry.id} className="flex justify-between border-b border-gray-700 pb-2">
                  <div>
                    <div className="font-medium">{entry.description}</div>
                    <div className="text-xs text-gray-500">{new Date(entry.CreatedAt).toLocaleString("vi-VN", {
                      day: "2-digit",
                      month: "2-digit",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit"
                    })}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-semibold ${entry.transaction_type === "income" ? "text-green-500" : "text-red-500"
                      }`}>${entry.amount}</div>
                    <div className="text-xs text-gray-500">{entry.category_display_name}</div>
                  </div>
                </li>
              ))}
            </ul>
            <button
              type="button"
              onClick={() => {
                navigate("/manual-input");
                console.log("Button Cancel clicked");
              }}
              className="w-full text-center text-sm text-blue-400 mt-3"
            >View all transactions</button>
          </div>

          {/* Budget Status */}
          {/* <div className="bg-[#1e1e1e] p-4 rounded">
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
            <button
              onClick={() => {
                navigate("/budget");
              }}
              className="w-full text-center text-sm text-blue-400">View all budgets</button>
          </div> */}
        </div>




        {/* Budget Utilization & Insights
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="bg-[#111]">
                        <CardContent className="p-4 text-white">
                            <p className="font-semibold">Budget Utilization</p>
                            <p className="text-sm mb-2">Overall Budget Usage: 81.3%</p>
                            <div className="w-full bg-gray-700 h-2 rounded">
                                <div className="h-2 bg-blue-400 rounded" style={{ width: '81.3%' }}></div>
                            </div>
                            <div className="text-xs mt-2">Transactions: 47 | Avg. Size: $60.48</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-[#111]">
                        <CardContent className="p-4 text-white space-y-2">
                            <p className="font-semibold">Quick Insights</p>
                            <div className="text-sm">Top Spending Category: <span className="text-red-400 font-medium">Food ($450.75)</span></div>
                            <div className="text-sm">Budget Performance: <span className="text-red-400">- $127.30 (3 categories over budget)</span></div>
                        </CardContent>
                    </Card>
                </div>

                {/* Spending Trends */}
        {/* <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="bg-[#111]">
                        <CardContent className="p-4 text-white">
                            <p className="font-semibold mb-2">Spending Over Time</p>
                            {[
                                { week: "Week 1", amount: 425.5, change: "+12.5%", color: "text-green-300" },
                                { week: "Week 2", amount: 380.25, change: "+10.6%", color: "text-green-300" },
                                { week: "Week 3", amount: 520.75, change: "+36.9%", color: "text-red-300" },
                                { week: "Week 4", amount: 445.3, change: "+14.5%", color: "text-green-300" },
                            ].map((item, idx) => (
                                <div key={idx} className="mb-2">
                                    <p className="text-sm">{item.week}: <span className={item.color}>${item.amount} ({item.change})</span></p>
                                    <div className="w-full bg-gray-700 h-2 rounded">
                                        <div className="h-2 bg-blue-400 rounded" style={{ width: `${(item.amount / 600) * 100}%` }}></div>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card> */}

        {/* Category Trends */}
        {/* <Card className="bg-[#111]">
                        <CardContent className="p-4 text-white">
                            <p className="font-semibold mb-2">Category Trends</p>
                            {[
                                { label: "Food", from: 420.3, to: 450.75, change: "+7.2%", up: true },
                                { label: "Transportation", from: 245.8, to: 210.5, change: "-14.4%", up: false },
                                { label: "Entertainment", from: 165.9, to: 180.25, change: "+8.6%", up: true },
                            ].map((cat, idx) => (
                                <div key={idx} className="text-sm mb-2">
                                    {cat.label}: ${cat.from.toFixed(2)} → ${cat.to.toFixed(2)} <span className={cat.up ? "text-green-300" : "text-red-300"}>{cat.change}</span>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                 </div> */}

      </div>

    </Layout>
  )
}

export default Dashboard