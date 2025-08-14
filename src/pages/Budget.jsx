

import { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { Plus, Download } from "lucide-react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

const Budget = () => {
    const navigate = useNavigate();
    const [budgets, setBudgets] = useState([]);
    const [loading, setLoading] = useState(true);

    const handleSave = () => navigate("/create/budget");

    // Filter state
    const [filters, setFilters] = useState({
        budget_type: "",
        is_active: true,
        date_from: "",
        date_to: "",
        skip: 0,
        limit: 10,
        sort_by: "CreatedAt",
        sort_order: "desc",
    });

    // Fetch budgets with overview & vsActual (initial load)
    const fetchInitialBudgets = async () => {
        try {
            const token = sessionStorage.getItem("token");
            const headers = { Authorization: `Bearer ${token}` };
            const resBudgets = await API.get(
                '/budgets/?skip=0&limit=10&sort_by=CreatedAt&sort_order=desc',
                { headers }
            );
            const budgetList = resBudgets.data.budgets || [];

            const budgetsWithDetails = await Promise.all(
                budgetList.map(async (budget) => {
                    const overviewRes = await API.get(
                        `/budgets/${budget.BudgetID}/overview`,
                        { headers }
                    );

                    let vsActualData = [];
                    try {
                        const vsActualRes = await API.get(
                            `/budgets/${budget.BudgetID}/vs-actual`,
                            { headers }
                        );
                        vsActualData = vsActualRes.data.categories || [];
                    } catch (err) {
                        console.warn(`Failed to fetch vsActual for budget ${budget.BudgetID}`, err);
                    }

                    return {
                        ...budget,
                        overview: overviewRes.data.categories || [],
                        vsActual: vsActualData
                    };
                })
            );

            setBudgets(budgetsWithDetails);
        } catch (error) {
            console.error("Error fetching budgets:", error);
        } finally {
            setLoading(false);
        }
    };

    // Fetch budgets with filter
    const fetchBudgetsWithFilter = async () => {
        setLoading(true);
        try {
            const token = sessionStorage.getItem("token");
            const query = new URLSearchParams(filters).toString();

            const response = await API.get(`/budgets/?${query}`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            const data = response.data;
            setBudgets(data.budgets || []);
            setOverview(data.overview || {});
            setVsActual(data.vs_actual || {});
        } catch (err) {
            console.error("Error fetching budgets:", err);
        } finally {
            setLoading(false);
        }
    };

    
    // Load initial budgets when page mounts
    useEffect(() => {
        fetchInitialBudgets();
    }, []);

    // Handle filter change
    const handleFilterChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFilters((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    if (loading) {
        return (
            <Layout>
                <div className="h-dvh bg-[#121212] text-white p-6 space-y-6">
                    {/* Header */}
                    <div className="flex justify-between items-center">
                        <div className="text-2xl font-bold">Budget Management</div>
                        <div className="space-x-2">
                            <Button variant="outline">
                                <Download className="w-4 h-4 mr-2" /> Export
                            </Button>
                            <Button onClick={handleSave}>
                                <Plus className="w-4 h-4 mr-2" /> Create Budget
                            </Button>
                        </div>
                    </div>

                    {/* Filter */}
                    <div>
                        <div className="mb-6 p-4 bg-[#121212] border border-gray-700 rounded-lg flex flex-wrap gap-4 items-end">
                            <div>
                                <label className="block text-sm font-medium mb-1">Budget Type</label>
                                <select
                                    name="budget_type"
                                    value={filters.budget_type}
                                    onChange={handleFilterChange}
                                    className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                                >
                                    <option value="">All</option>
                                    <option value="monthly">Monthly</option>
                                    <option value="weekly">Weekly</option>
                                    <option value="daily">Daily</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1 ">From</label>
                                <input
                                    type="date"
                                    name="date_from"
                                    value={filters.date_from}
                                    onChange={handleFilterChange}
                                    className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-1">To</label>
                                <input
                                    type="date"
                                    name="date_to"
                                    value={filters.date_to}
                                    onChange={handleFilterChange}
                                    className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                                />
                            </div>

                            <Button onClick={fetchBudgetsWithFilter}>Apply Filter</Button>
                        </div>

                        {/* Budget List */}
                        <div className="overflow-x-auto bg-[#1e1e1e] p-4 rounded">
                            <table className="flex-1 min-w-full text-left gap-4">
                                <thead className="border-b border-gray-700 mb-4">
                                    <tr>
                                        <th className="px-4 pb-4 text-left">Name</th>
                                        <th className="px-4 pb-4 text-left">Type</th>
                                        <th className="px-4 pb-4 text-left">Amount</th>
                                        <th className="px-4 pb-4 text-left">Start</th>
                                        <th className="px-4 pb-4 text-left">End</th>
                                        <th className="px-4 pb-4 text-left">Total Spent</th>
                                        <th className="px-4 pb-4 text-left">Active</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loading ? (
                                        <tr><td colSpan="7" className="text-center py-4">Loading...</td></tr>
                                    ) : budgets.length === 0 ? (
                                        <tr><td colSpan="7" className="text-center py-4">No budgets found.</td></tr>
                                    ) : (
                                        budgets.map((b) => (
                                            <tr key={b.BudgetID} className="text-center">
                                                <td className="px-4 py-2 ">{b.budget_name}</td>
                                                <td className="px-4 py-2 ">{b.budget_type}</td>
                                                <td className="px-4 py-2 ">{b.amount}</td>
                                                <td className="px-4 py-2 ">{b.period_start}</td>
                                                <td className="px-4 py-2 ">{b.period_end}</td>
                                                <td className="px-4 py-2 ">{b.total_spent}</td>
                                                <td className="px-4 py-2 ">{b.is_active ? "Yes" : "No"}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </Layout>
        )
    }

    return (
        <Layout>
            <div className="h-dvh bg-[#121212] text-white p-6 space-y-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div className="text-2xl font-bold">Budget Management</div>
                    <div className="space-x-2">
                        <Button variant="outline">
                            <Download className="w-4 h-4 mr-2" /> Export
                        </Button>
                        <Button onClick={handleSave}>
                            <Plus className="w-4 h-4 mr-2" /> Create Budget
                        </Button>
                    </div>
                </div>

                {/* Budget Overview & Budget vs Actual */}
                {/* Budget Overview */}
                <div className="flex flex-row gap-6">
                    {/* Budget Overview */}
                    <Card className="w-1/3 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg">
                        <CardContent className="p-6">
                            <h3 className="text-lg font-semibold mb-2 text-white">Budget Overview</h3>
                            <p className="text-sm text-gray-400 mb-4">Your monthly budget breakdown</p>
                            <div className="space-y-5">
                                {budgets.length > 0 ? (
                                    budgets
                                        .filter(b => b.overview && b.overview.length > 0) // chỉ render nếu có data
                                        .map(budget =>
                                            budget.overview.map((cat, idx) => {
                                                const colors = [
                                                    "bg-blue-500",
                                                    // "bg-green-500",
                                                    // "bg-purple-500",
                                                    // "bg-orange-500",
                                                    // "bg-red-500",
                                                    // "bg-pink-500",
                                                ];
                                                const percentUsed = Number(cat.percentage_used || 0).toFixed(0);
                                                return (
                                                    <div key={cat.user_category_id} className="space-y-1">
                                                        <div className="flex justify-between text-sm font-medium">
                                                            <span className="flex items-center gap-2">
                                                                <span
                                                                    className={`w-2 h-2 rounded-full ${colors[idx % colors.length]}`}
                                                                />
                                                                {cat.category_name}
                                                            </span>
                                                            <span className="text-white font-medium">
                                                                ${Number(cat.spent_amount || 0).toFixed(2)}{" "}
                                                                <span className="text-gray-400 text-xs">
                                                                    of ${Number(cat.allocated_amount || 0).toFixed(2)}
                                                                </span>
                                                            </span>
                                                        </div>
                                                        <Progress
                                                            value={percentUsed}
                                                            className={`h-2 rounded-full ${colors[idx % colors.length]}`}
                                                        />
                                                        <div className="text-xs text-gray-400">{percentUsed}% used</div>
                                                    </div>
                                                );
                                            })
                                        )
                                ) : (
                                    <div className="text-gray-400">No budgets found</div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Budget vs Actual */}
                    <Card className="w-2/3 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg">
                        <CardContent className="p-6">
                            <h3 className="text-lg font-semibold mb-2 text-white">Budget vs Actual</h3>
                            <p className="text-sm text-gray-400 mb-4">
                                Compare your budgeted amounts with actual spending
                            </p>

                            {/* Title row - chỉ render 1 lần */}
                            <div className="grid grid-cols-6 text-xs font-semibold text-gray-400 border-b border-zinc-800 pb-2 mb-2">
                                <div>Category</div>
                                <div>Budgeted</div>
                                <div>Spent</div>
                                <div>Remaining</div>
                                <div>Progress</div>
                                <div>Status</div>
                            </div>

                            {budgets.length > 0 ? (
                                budgets
                                    .filter(b => b.vsActual && b.vsActual.length > 0) // chỉ render nếu có data
                                    .map(budget =>
                                        budget.vsActual.map((cat, idx) => {
                                            const progress = Number(cat.percentage_used) || 0;
                                            return (
                                                <div
                                                    key={cat.user_category_id}
                                                    className="grid grid-cols-6 items-center min-h-14 py-2 border-b border-zinc-800 text-sm text-white"
                                                >
                                                    <div>{cat.category_name}</div>
                                                    <div>${Number(cat.allocated_amount).toFixed(2)}</div>
                                                    <div>${Number(cat.spent_amount).toFixed(2)}</div>
                                                    <div
                                                        className={
                                                            Number(cat.remaining_amount) < 0
                                                                ? "text-red-500"
                                                                : "text-green-500"
                                                        }
                                                    >
                                                        ${Number(cat.remaining_amount).toFixed(2)}
                                                    </div>
                                                    <Progress value={progress} className="h-1 bg-zinc-700" />
                                                    <div>
                                                        <span
                                                            className={`px-2 py-0.5 rounded-full text-xs ${cat.over_budget
                                                                ? "bg-red-500/20 text-red-400"
                                                                : progress > 90
                                                                    ? "bg-yellow-500/20 text-yellow-400"
                                                                    : "bg-green-500/20 text-green-400"
                                                                }`}
                                                        >
                                                            {cat.over_budget
                                                                ? "Over Budget"
                                                                : progress > 90
                                                                    ? "Near Limit"
                                                                    : "On Track"}
                                                        </span>
                                                    </div>
                                                </div>
                                            );
                                        })
                                    )
                            ) : (
                                <div className="text-gray-400">No budgets found</div>
                            )}
                        </CardContent>
                    </Card>
                </div>



                {/* Filter */}
                <div>
                    <div className="mb-6 p-4 bg-[#121212] border border-gray-700 rounded-lg flex flex-wrap gap-4 items-end">
                        <div>
                            <label className="block text-sm font-medium mb-1">Budget Type</label>
                            <select
                                name="budget_type"
                                value={filters.budget_type}
                                onChange={handleFilterChange}
                                className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                            >
                                <option value="">All</option>
                                <option value="monthly">Monthly</option>
                                <option value="weekly">Weekly</option>
                                <option value="daily">Daily</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1 ">From</label>
                            <input
                                type="date"
                                name="date_from"
                                value={filters.date_from}
                                onChange={handleFilterChange}
                                className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">To</label>
                            <input
                                type="date"
                                name="date_to"
                                value={filters.date_to}
                                onChange={handleFilterChange}
                                className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                            />
                        </div>

                        <Button onClick={fetchBudgetsWithFilter}>Apply Filter</Button>
                    </div>

                    {/* Budget List */}
                    <div className="overflow-x-auto bg-[#1e1e1e] p-4 rounded">
                        <table className="flex-1 min-w-full text-left gap-4">
                            <thead className="border-b border-gray-700 mb-4">
                                <tr>
                                    <th className="px-4 pb-4 text-left">Name</th>
                                    <th className="px-4 pb-4 text-left">Type</th>
                                    <th className="px-4 pb-4 text-left">Amount</th>
                                    <th className="px-4 pb-4 text-left">Start</th>
                                    <th className="px-4 pb-4 text-left">End</th>
                                    <th className="px-4 pb-4 text-left">Total Spent</th>
                                    <th className="px-4 pb-4 text-left">Active</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr><td colSpan="7" className="text-center py-4">Loading...</td></tr>
                                ) : budgets.length === 0 ? (
                                    <tr><td colSpan="7" className="text-center py-4">No budgets found.</td></tr>
                                ) : (
                                    budgets.map((b) => (
                                        <tr key={b.BudgetID} className="text-left">
                                            <td className="px-4 py-2 ">{b.budget_name}</td>
                                            <td className="px-4 py-2 ">{b.budget_type}</td>
                                            <td className="px-4 py-2 ">{b.amount}</td>
                                            <td className="px-4 py-2 ">{b.period_start}</td>
                                            <td className="px-4 py-2 ">{b.period_end}</td>
                                            <td className="px-4 py-2 ">{b.total_spent}</td>
                                            <td className="px-4 py-2 ">{b.is_active ? "Yes" : "No"}</td>
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

export default Budget;

