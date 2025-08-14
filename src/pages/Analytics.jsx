import React from "react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import Layout from "../components/Layout/Layout";
import Select from "../components/ui/selection";


export default function Analytics() {
    return (
        <Layout>
            <div className="p-6 bg-black text-white min-h-screen space-y-6">
                <h1 className="text-3xl font-bold">Analytics</h1>

                {/* Filters */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <div>
                        <label className="text-sm">Date Range</label>
                        <Input type="date" defaultValue="2025-07-01" className="text-black" />
                    </div>
                    <div>
                        <label className="text-sm text-white mb-1 block">Period</label>
                        <Select
                            className="w-full"
                            value={"monthly"}
                            onChange={() => { }}
                            options={[
                                { value: "monthly", label: "Monthly" }
                            ]}
                        />
                    </div>

                    <div>
                        <label className="text-sm text-white mb-1 block">Category</label>
                        <Select
                            className="w-full"
                            value={"all"}
                            onChange={() => { }}
                            options={[
                                { value: "all", label: "All Categories" }
                            ]}
                        />
                    </div>
                    <Button className="bg-white text-black">Apply Filters</Button>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card className="bg-[#111] text-green-400">
                        <CardContent className="p-4">
                            <p>Total Income</p>
                            <p className="text-xl font-bold">$4,500.00</p>
                            <p className="text-xs text-green-300">+12.5% from last period</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-[#111] text-red-400">
                        <CardContent className="p-4">
                            <p>Total Expenses</p>
                            <p className="text-xl font-bold">$2,847.50</p>
                            <p className="text-xs text-red-300">-8.2% from last period</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-[#111] text-green-400">
                        <CardContent className="p-4">
                            <p>Net Income</p>
                            <p className="text-xl font-bold">$1,652.50</p>
                            <p className="text-xs text-green-300">+24.1% from last period</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-[#111] text-white">
                        <CardContent className="p-4">
                            <p>Savings Rate</p>
                            <p className="text-xl font-bold">36.7%</p>
                            <div className="w-full bg-gray-700 h-2 rounded mt-2">
                                <div className="h-2 bg-green-400 rounded" style={{ width: '36.7%' }}></div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Budget Utilization & Insights */}
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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                    </Card>

                    {/* Category Trends */}
                    <Card className="bg-[#111]">
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
                </div>

                <div className="flex justify-end space-x-4">
                    <Button variant="outline" className="bg-gray-700 text-white">Refresh</Button>
                    <Button className="bg-white text-black">Export</Button>
                </div>
            </div>
        </Layout>
    );
}
