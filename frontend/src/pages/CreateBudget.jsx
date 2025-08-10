import React, { useState } from "react";
import Layout from "../components/Layout/Layout"

export default function CreateBudget() {
  const [formData, setFormData] = useState({
    budgetName: "",
    budgetPeriod: "Monthly",
    totalAmount: 0,
    startDate: "",
    endDate: "",
    description: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
<Layout>
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-3xl mx-auto">
        {/* Title */}
        <h1 className="text-2xl font-bold">Create New Budget</h1>
        <p className="text-gray-400 mb-8">
          Set up a budget to track your spending goals
        </p>

        {/* Steps */}
        <div className="flex justify-between mb-6">
          {["Basic Info", "Categories", "Settings", "Review"].map(
            (label, i) => (
              <div
                key={i}
                className="flex flex-col items-center flex-1"
              >
                <div
                  className={`w-8 h-8 flex items-center justify-center rounded-full border ${
                    i === 0
                      ? "bg-white text-black"
                      : "border-gray-600 text-gray-500"
                  }`}
                >
                  {i + 1}
                </div>
                <span
                  className={`mt-2 text-sm ${
                    i === 0 ? "text-white" : "text-gray-500"
                  }`}
                >
                  {label}
                </span>
              </div>
            )
          )}
        </div>

        {/* Form */}
        <div className="bg-[#111] p-6 rounded-lg">
          <h2 className="text-lg font-semibold mb-4">Budget Basics</h2>

          {/* Budget Name + Period */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm mb-1">Budget Name</label>
              <input
                type="text"
                name="budgetName"
                placeholder="e.g., Monthly Budget 2025"
                value={formData.budgetName}
                onChange={handleChange}
                className="w-full bg-black border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500"
              />
            </div>
            <div>
              <label className="block text-sm mb-1">Budget Period</label>
              <select
                name="budgetPeriod"
                value={formData.budgetPeriod}
                onChange={handleChange}
                className="w-full bg-black border border-gray-600 rounded px-3 py-2"
              >
                <option>Monthly</option>
                <option>Weekly</option>
                <option>Yearly</option>
              </select>
            </div>
          </div>

          {/* Total Amount */}
          <div className="mb-4">
            <label className="block text-sm mb-1">Total Budget Amount</label>
            <div className="flex items-center">
              <span className="bg-gray-800 px-3 border border-gray-600 border-r-0 rounded-l">$</span>
              <input
                type="number"
                name="totalAmount"
                value={formData.totalAmount}
                onChange={handleChange}
                className="flex-1 bg-black border border-gray-600 rounded-r px-3 py-2"
              />
            </div>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm mb-1">Start Date</label>
              <input
                type="date"
                name="startDate"
                value={formData.startDate}
                onChange={handleChange}
                className="w-full bg-black border border-gray-600 rounded px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm mb-1">End Date (Optional)</label>
              <input
                type="date"
                name="endDate"
                value={formData.endDate}
                onChange={handleChange}
                className="w-full bg-black border border-gray-600 rounded px-3 py-2"
              />
            </div>
          </div>

          {/* Description */}
          <div className="mb-6">
            <label className="block text-sm mb-1">Description (Optional)</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe the purpose of this budget..."
              className="w-full bg-black border border-gray-600 rounded px-3 py-2 h-20 placeholder-gray-500"
            />
          </div>

          {/* Quick Start Templates */}
          <div>
            <h3 className="text-sm font-medium mb-3">Quick Start Templates</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                {
                  title: "50/30/20 Rule",
                  desc: "50% needs, 30% wants, 20% savings",
                  cats: "3 categories",
                },
                {
                  title: "Zero-Based Budget",
                  desc: "Every dollar has a purpose",
                  cats: "3 categories",
                },
                {
                  title: "Envelope Method",
                  desc: "Allocate specific amounts to categories",
                  cats: "6 categories",
                },
              ].map((t, idx) => (
                <div
                  key={idx}
                  className="bg-black border border-gray-600 rounded p-3 hover:border-gray-400 cursor-pointer"
                >
                  <h4 className="font-medium">{t.title}</h4>
                  <p className="text-gray-400 text-sm">{t.desc}</p>
                  <span className="text-gray-500 text-xs">{t.cats}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-between mt-6">
          <button className="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700">
            Previous
          </button>
          <div className="flex gap-3">
            <button className="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700">
              Cancel
            </button>
            <button className="px-4 py-2 rounded bg-white text-black hover:bg-gray-200">
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
</Layout>
  );
}
