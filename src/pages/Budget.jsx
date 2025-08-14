// import { useState } from 'react';
// import Layout from '../components/Layout/Layout';
// import { Button } from "../components/ui/button";
// import { Card, CardContent } from "../components/ui/card";
// import { Progress } from "../components/ui/progress";
// import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs.jsx";
// import { ArrowUpRight, Plus, Download, AlertTriangle } from "lucide-react";
// import { useNavigate } from "react-router-dom";

// const Budget = () => {
//     const navigate = useNavigate();
//     const handleSave = () => {
//     navigate("/create/budget");
//   };


//     return (
//         <Layout>
//             <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6">
//                 <div className="flex justify-between items-center">
//                     <div className="text-2xl font-bold">Budget Management</div>
//                     <div className="space-x-2">
//                         <Button variant="outline">
//                             <Download className="w-4 h-4 mr-2" /> Export
//                         </Button>
//                         <Button onClick={handleSave}>
//                             <Plus className="w-4 h-4 mr-2" /> Create Budget
//                         </Button>
//                     </div>
//                 </div>

//                 <div className="flex space-x-4">
//                     <select className="bg-zinc-900 text-white px-4 py-2 rounded-md">
//                         <option>Monthly</option>
//                     </select>
//                     <select className="bg-zinc-900 text-white px-4 py-2 rounded-md">
//                         <option>July 2025</option>
//                     </select>
//                 </div>

//                 {/* Budget Alerts */}
//                 <div className="space-y-4">
//                     <Card className="bg-zinc-900 border-yellow-500 border">
//                         <CardContent className="p-4">
//                             <div className="flex justify-between items-center">
//                                 <div className="flex items-center gap-2 text-yellow-400">
//                                     <AlertTriangle className="w-5 h-5" />
//                                     Entertainment Budget Alert
//                                 </div>
//                                 <div className="text-white">$180.25 / $200.00</div>
//                             </div>
//                             <Progress value={90} className="bg-yellow-500 h-2 mt-2" />
//                         </CardContent>
//                     </Card>

//                     <Card className="bg-zinc-900 border-red-500 border">
//                         <CardContent className="p-4">
//                             <div className="flex justify-between items-center">
//                                 <div className="flex items-center gap-2 text-red-500">
//                                     <AlertTriangle className="w-5 h-5" />
//                                     Utilities Budget Alert
//                                 </div>
//                                 <div className="text-white">$245.80 / $250.00</div>
//                             </div>
//                             <Progress value={98} className="bg-red-500 h-2 mt-2" />
//                         </CardContent>
//                     </Card>

//                     <Card className="bg-zinc-900 border-green-500 border">
//                         <CardContent className="p-4">
//                             <div className="flex justify-between items-center">
//                                 <div className="flex items-center gap-2 text-green-500">
//                                     <AlertTriangle className="w-5 h-5" />
//                                     Transportation Budget Alert
//                                 </div>
//                                 <div className="text-white">$210.50 / $300.00</div>
//                             </div>
//                             <Progress value={70} className="bg-green-500 h-2 mt-2" />
//                         </CardContent>
//                     </Card>
//                 </div>

//                 {/* Overview Cards */}
//                 <div className="grid grid-cols-4 gap-4 text-sm pt6">
//                     <Card className="bg-zinc-900">
//                         <CardContent className="p-4">
//                             <div>Total Budget</div>
//                             <div className="text-2xl font-semibold">$3,500.00</div>
//                             <div className="text-xs text-muted-foreground">This month</div>
//                         </CardContent>
//                     </Card>
//                     <Card className="bg-zinc-900">
//                         <CardContent className="p-4">
//                             <div>Total Spent</div>
//                             <div className="text-2xl font-semibold">$2,847.50</div>
//                             <Progress value={81} className="h-2 mt-2" />
//                         </CardContent>
//                     </Card>
//                     <Card className="bg-zinc-900">
//                         <CardContent className="p-4">
//                             <div>Remaining</div>
//                             <div className="text-2xl font-semibold text-green-500">$652.50</div>
//                             <div className="text-xs text-muted-foreground">19% left</div>
//                         </CardContent>
//                     </Card>
//                     <Card className="bg-zinc-900">
//                         <CardContent className="p-4">
//                             <div>Categories</div>
//                             <div className="text-2xl font-semibold">4</div>
//                             <div className="text-xs text-muted-foreground">Active budgets</div>
//                         </CardContent>
//                     </Card>
//                 </div>

//                 {/* Tabs */}
//                 <Tabs defaultValue="overview" className="mt-6">
//                     <TabsList>
//                         <TabsTrigger value="overview">Overview</TabsTrigger>
//                         <TabsTrigger value="categories">Categories</TabsTrigger>
//                         <TabsTrigger value="analytics">Analytics</TabsTrigger>
//                     </TabsList>
//                 </Tabs>

//                 <div className="grid grid-cols-2 gap-6">
//                     {/* Budget Overview */}
//                     <Card className="bg-zinc-900">
//                         <CardContent className="p-4">
//                             <h3 className="font-semibold mb-4">Budget Overview</h3>
//                             <div className="space-y-2">
//                                 <div>
//                                     <div className="text-sm">Food</div>
//                                     <div className="text-xs text-muted-foreground">$450.75 of $600.00</div>
//                                     <Progress value={75} className="bg-blue-500 h-2" />
//                                 </div>
//                                 <div>
//                                     <div className="text-sm">Transportation</div>
//                                     <div className="text-xs text-muted-foreground">$210.50 of $300.00</div>
//                                     <Progress value={70} className="bg-green-500 h-2" />
//                                 </div>
//                                 <div>
//                                     <div className="text-sm">Entertainment</div>
//                                     <div className="text-xs text-muted-foreground">$180.25 of $200.00</div>
//                                     <Progress value={90} className="bg-purple-500 h-2" />
//                                 </div>
//                             </div>
//                         </CardContent>
//                     </Card>

//                     {/* Budget vs Actual */}
//                     <Card className="bg-zinc-900">
//                         <CardContent className="p-4">
//                             <h3 className="font-semibold mb-4">Budget vs Actual</h3>
//                             <div className="space-y-2 text-xs">
//                                 <div className="grid grid-cols-6 font-semibold text-muted-foreground">
//                                     <div>Category</div>
//                                     <div>Budgeted</div>
//                                     <div>Spent</div>
//                                     <div>Remaining</div>
//                                     <div>Progress</div>
//                                     <div>Status</div>
//                                 </div>
//                                 <div className="grid grid-cols-6 items-center">
//                                     <div>Food</div>
//                                     <div>$400.00</div>
//                                     <div>$320.45</div>
//                                     <div className="text-green-500">$79.55</div>
//                                     <Progress value={80} className="h-1" />
//                                     <div>On Track</div>
//                                 </div>
//                                 <div className="grid grid-cols-6 items-center">
//                                     <div>Food</div>
//                                     <div>$200.00</div>
//                                     <div>$130.30</div>
//                                     <div className="text-green-500">$69.70</div>
//                                     <Progress value={65} className="h-1" />
//                                     <div>Under Budget</div>
//                                 </div>
//                                 <div className="grid grid-cols-6 items-center">
//                                     <div>Transportation</div>
//                                     <div>$120.00</div>
//                                     <div>$85.00</div>
//                                     <div className="text-green-500">$35.00</div>
//                                     <Progress value={71} className="h-1" />
//                                     <div>Under Budget</div>
//                                 </div>
//                             </div>
//                         </CardContent>
//                     </Card>
//                 </div>
//             </div>

//         </Layout>
//     )
// }

// export default Budget

import { useState, useEffect } from 'react';
import Layout from '../components/Layout/Layout';
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { ArrowUpRight, Plus, Download } from "lucide-react";
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import API from "../services/api"

const Budget = () => {
    const navigate = useNavigate();
    const [budgets, setBudgets] = useState([]);
    const [loading, setLoading] = useState(true);

    const handleSave = () => navigate("/create/budget");

    const token = sessionStorage.getItem("token");
    const headers = { Authorization: `Bearer ${token}` };

    useEffect(() => {
        const fetchBudgets = async () => {
            try {
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
                            console.warn(`Failed to fetch vsActual for budget ${budget.budget_id}`, err);
                        }

                        return {
                            ...budget,
                            overview: overviewRes.data.categories || [],
                            vsActual: vsActualData
                        };
                    })
                );

                setBudgets(budgetsWithDetails);
                // console.log(overview);
                // console.log(vsActual);
                setBudgets(budgetsWithDetails);
                console.log("budgetsWithDetails", budgetsWithDetails);
            } catch (error) {
                console.error("Error fetching budgets:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchBudgets();
    }, []);

    // const [budgets, setBudgets] = useState([]);
    // const [loading, setLoading] = useState(false);
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

    const fetchBudgets = async () => {
        setLoading(true);
        try {
            const query = new URLSearchParams(filters).toString();
            const response = await fetch(`http://127.0.0.1:8000/budgets/?${query}`);
            const data = await response.json();
            setBudgets(data.budgets || []);
        } catch (err) {
            console.error("Error fetching budgets:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBudgets();
    }, [filters]);

    const handleFilterChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFilters((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };


    if (loading) return <div className="text-white p-6">Loading...</div>;




    return (
        <Layout>
            <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6">
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
                <div className="grid grid-cols-2 gap-6">
                    {/* Budget Overview */}
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <h3 className="font-semibold mb-4">Budget Overview</h3>
                            <div className="space-y-4">
                                {budgets.length > 0 ? (
                                    budgets.map(budget => (
                                        <div key={budget.budget_id} className="space-y-2">
                                            <div className="font-semibold">{budget.budget_name}</div>
                                            {budget.overview?.length > 0 ? (
                                                budget.overview.map(cat => (
                                                    <div key={cat.user_category_id}>
                                                        <div className="text-sm">{cat.category_name}</div>
                                                        <div className="text-xs text-gray-400">
                                                            ${Number(cat.spent_amount) || 0} of ${Number(cat.allocated_amount) || 0}
                                                        </div>
                                                        <Progress value={Number(cat.percentage_used) || 0} className="bg-blue-500 h-2" />
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="text-sm text-gray-400">No categories available</div>
                                            )}
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-gray-400">No budgets found</div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Budget vs Actual */}
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <h3 className="font-semibold mb-4">Budget vs Actual</h3>
                            {budgets.length > 0 ? (
                                budgets.map(budget => (
                                    <div key={budget.budget_id} className="space-y-2 text-xs">
                                        <div className="font-semibold mb-2">{budget.budget_name}</div>
                                        <div className="grid grid-cols-6 font-semibold text-gray-400">
                                            <div>Category</div>
                                            <div>Budgeted</div>
                                            <div>Spent</div>
                                            <div>Remaining</div>
                                            <div>Progress</div>
                                            <div>Status</div>
                                        </div>
                                        {budget.vsActual?.length > 0 ? (
                                            budget.vsActual.map(cat => (
                                                <div key={cat.user_category_id} className="grid grid-cols-6 items-center">
                                                    <div>{cat.category_name}</div>
                                                    <div>${Number(cat.allocated_amount) || 0}</div>
                                                    <div>${Number(cat.spent_amount) || 0}</div>
                                                    <div className={Number(cat.remaining_amount) < 0 ? "text-red-500" : "text-green-500"}>
                                                        ${Number(cat.remaining_amount) || 0}
                                                    </div>
                                                    <Progress value={Number(cat.percentage_used) || 0} className="h-1" />
                                                    <div>{cat.over_budget ? "Over Budget" : "On Track"}</div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="text-gray-400">No categories available</div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="text-gray-400">No budgets found</div>
                            )}
                        </CardContent>
                    </Card>
                </div>
                <div>
                    {/* Filter */}
                    <div className="mb-6 p-4 bg-[#121212] border border-gray-700 rounded-lg flex flex-wrap gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Budget Type</label>
                            <select
                                name="budget_type"
                                value={filters.budget_type}
                                onChange={handleFilterChange}
                                className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                            >
                                <option value="monthly">Monthly</option>
                                <option value="weekly">Weekly</option>
                                <option value="daily">Daily</option>
                            </select>
                        </div>

                        {/* <div>
                            <label className="block text-sm font-medium mb-1">Active</label>
                            <input
                                type="checkbox"
                                name="is_active"
                                checked={filters.is_active}
                                onChange={handleFilterChange}
                                className="px-3 py-2 rounded bg-[#121212] border border-gray-700"
                            />
                        </div> */}

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
                                    <p>Loading...</p>
                                ) : budgets.length === 0 ? (
                                    <p>No budgets found.</p>
                                ) : (

                                    budgets.map((b) => (
                                        <tr key={b.BudgetID} className="text-center">
                                            <td className="px-4 py-2 border">{b.budget_name}</td>
                                            <td className="px-4 py-2 border">{b.budget_type}</td>
                                            <td className="px-4 py-2 border">{b.amount}</td>
                                            <td className="px-4 py-2 border">{b.period_start}</td>
                                            <td className="px-4 py-2 border">{b.period_end}</td>
                                            <td className="px-4 py-2 border">{b.total_spent}</td>
                                            <td className="px-4 py-2 border">{b.is_active ? "Yes" : "No"}</td>
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
