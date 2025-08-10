import { useState } from 'react';
import Layout from '../components/Layout/Layout';
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs.jsx";
import { ArrowUpRight, Plus, Download, AlertTriangle } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Budget = () => {
    const navigate = useNavigate();
    const handleSave = () => {
    navigate("/create/budget");
  };


    return (
        <Layout>
            <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6">
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

                <div className="flex space-x-4">
                    <select className="bg-zinc-900 text-white px-4 py-2 rounded-md">
                        <option>Monthly</option>
                    </select>
                    <select className="bg-zinc-900 text-white px-4 py-2 rounded-md">
                        <option>July 2025</option>
                    </select>
                </div>

                {/* Budget Alerts */}
                <div className="space-y-4">
                    <Card className="bg-zinc-900 border-yellow-500 border">
                        <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                                <div className="flex items-center gap-2 text-yellow-400">
                                    <AlertTriangle className="w-5 h-5" />
                                    Entertainment Budget Alert
                                </div>
                                <div className="text-white">$180.25 / $200.00</div>
                            </div>
                            <Progress value={90} className="bg-yellow-500 h-2 mt-2" />
                        </CardContent>
                    </Card>

                    <Card className="bg-zinc-900 border-red-500 border">
                        <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                                <div className="flex items-center gap-2 text-red-500">
                                    <AlertTriangle className="w-5 h-5" />
                                    Utilities Budget Alert
                                </div>
                                <div className="text-white">$245.80 / $250.00</div>
                            </div>
                            <Progress value={98} className="bg-red-500 h-2 mt-2" />
                        </CardContent>
                    </Card>

                    <Card className="bg-zinc-900 border-green-500 border">
                        <CardContent className="p-4">
                            <div className="flex justify-between items-center">
                                <div className="flex items-center gap-2 text-green-500">
                                    <AlertTriangle className="w-5 h-5" />
                                    Transportation Budget Alert
                                </div>
                                <div className="text-white">$210.50 / $300.00</div>
                            </div>
                            <Progress value={70} className="bg-green-500 h-2 mt-2" />
                        </CardContent>
                    </Card>
                </div>

                {/* Overview Cards */}
                <div className="grid grid-cols-4 gap-4 text-sm pt6">
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <div>Total Budget</div>
                            <div className="text-2xl font-semibold">$3,500.00</div>
                            <div className="text-xs text-muted-foreground">This month</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <div>Total Spent</div>
                            <div className="text-2xl font-semibold">$2,847.50</div>
                            <Progress value={81} className="h-2 mt-2" />
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <div>Remaining</div>
                            <div className="text-2xl font-semibold text-green-500">$652.50</div>
                            <div className="text-xs text-muted-foreground">19% left</div>
                        </CardContent>
                    </Card>
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <div>Categories</div>
                            <div className="text-2xl font-semibold">4</div>
                            <div className="text-xs text-muted-foreground">Active budgets</div>
                        </CardContent>
                    </Card>
                </div>

                {/* Tabs */}
                <Tabs defaultValue="overview" className="mt-6">
                    <TabsList>
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="categories">Categories</TabsTrigger>
                        <TabsTrigger value="analytics">Analytics</TabsTrigger>
                    </TabsList>
                </Tabs>

                <div className="grid grid-cols-2 gap-6">
                    {/* Budget Overview */}
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <h3 className="font-semibold mb-4">Budget Overview</h3>
                            <div className="space-y-2">
                                <div>
                                    <div className="text-sm">Food</div>
                                    <div className="text-xs text-muted-foreground">$450.75 of $600.00</div>
                                    <Progress value={75} className="bg-blue-500 h-2" />
                                </div>
                                <div>
                                    <div className="text-sm">Transportation</div>
                                    <div className="text-xs text-muted-foreground">$210.50 of $300.00</div>
                                    <Progress value={70} className="bg-green-500 h-2" />
                                </div>
                                <div>
                                    <div className="text-sm">Entertainment</div>
                                    <div className="text-xs text-muted-foreground">$180.25 of $200.00</div>
                                    <Progress value={90} className="bg-purple-500 h-2" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Budget vs Actual */}
                    <Card className="bg-zinc-900">
                        <CardContent className="p-4">
                            <h3 className="font-semibold mb-4">Budget vs Actual</h3>
                            <div className="space-y-2 text-xs">
                                <div className="grid grid-cols-6 font-semibold text-muted-foreground">
                                    <div>Category</div>
                                    <div>Budgeted</div>
                                    <div>Spent</div>
                                    <div>Remaining</div>
                                    <div>Progress</div>
                                    <div>Status</div>
                                </div>
                                <div className="grid grid-cols-6 items-center">
                                    <div>Food</div>
                                    <div>$400.00</div>
                                    <div>$320.45</div>
                                    <div className="text-green-500">$79.55</div>
                                    <Progress value={80} className="h-1" />
                                    <div>On Track</div>
                                </div>
                                <div className="grid grid-cols-6 items-center">
                                    <div>Food</div>
                                    <div>$200.00</div>
                                    <div>$130.30</div>
                                    <div className="text-green-500">$69.70</div>
                                    <Progress value={65} className="h-1" />
                                    <div>Under Budget</div>
                                </div>
                                <div className="grid grid-cols-6 items-center">
                                    <div>Transportation</div>
                                    <div>$120.00</div>
                                    <div>$85.00</div>
                                    <div className="text-green-500">$35.00</div>
                                    <Progress value={71} className="h-1" />
                                    <div>Under Budget</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

        </Layout>
    )
}

export default Budget