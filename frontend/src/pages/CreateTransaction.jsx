import React, { useState } from "react";
import { CalendarDays } from "lucide-react";
import Layout from "../components/Layout/Layout";
import API from "../services/api";

export default function CreateTransactionForm() {
  const [form, setForm] = useState({
    transaction_type: "",
    amount: "",
    description: "",
    transaction_date: "",
    transaction_time: "",
    payment_method: "cash",
    location: "",
    notes: "",
    created_by: "manual",
    category_display_name: ""
  });

  const handleChange = (e) => {
    console.log("handleChange", e.target.name, e.target.value);
    setForm({ ...form, [e.target.name]: e.target.value });
  };

const handleSubmit = async (e) => {
  e.preventDefault();

  const now = new Date();
  const utcTime = now.toISOString().split("T")[1];

  const formData = {
    ...form,
    transaction_time: utcTime,
  };

  const token = sessionStorage.getItem("token");

  try {
    const res = await API.post("/transactions/", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    // Axios trả về status và data, không có res.ok
    if (res.status !== 200 && res.status !== 201) {
      throw new Error("Failed to create transaction");
    }

    console.log("Success:", res.data);
  } catch (err) {
    console.error(err);
  }
};

  const [activeTab, setActiveTab] = useState(0);

  return (
    <Layout>
      <form onSubmit={handleSubmit}>
        <div className="flex h-screen bg-[#0f0f0f] text-white">
          <div className="flex-1 flex flex-col">
            <header className="p-4 flex justify-between items-center border-b border-gray-700">
              <h2 className="text-2xl font-bold">Add New Transaction</h2>
              <button type="button" className="px-4 py-2 border border-gray-500 rounded hover:bg-gray-700">Cancel</button>
            </header>

            <div className="p-6">
              <p className="text-gray-400 mb-4">Record a new income or expense transaction</p>

              {/* Tabs */}
              <div className="flex border-b border-gray-700 mb-6">
                {["Basic Info", "Details", "Advanced"].map((tab, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setActiveTab(i)}
                    className={`px-4 py-2 border-t border-l border-r border-gray-700 
                      ${activeTab === i ? "bg-[#1f1f1f] text-white" : "text-gray-400 hover:text-white"}`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {activeTab === 0 && (
                <div className="rounded-lg border border-gray-700 bg-[#1a1a1a] p-6 space-y-4">
                  <h3 className="text-lg font-semibold">Transaction Type & Amount</h3>
                  <p className="text-sm text-gray-400">Choose whether this is income or an expense</p>

                  <div className="flex gap-6 mt-2">
                    <label className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="transaction_type"
                        value="income"
                        checked={form.transaction_type === "income"}
                        onChange={handleChange}
                      />
                      Income
                    </label>
                    <label className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="transaction_type"
                        value="expense"
                        checked={form.transaction_type === "expense"}
                        onChange={handleChange}
                      />
                      Expense
                    </label>
                  </div>

                  {/* Amount */}
                  <div>
                    <label className="block text-sm mb-1">Amount</label>
                    <input
                      type="number"
                      name="amount"
                      value={form.amount}
                      onChange={handleChange}
                      className="w-full bg-[#0f0f0f] border border-gray-700 rounded p-2"
                      placeholder="0.00"
                    />
                    <div className="flex gap-2 mt-2">
                      {[10, 25, 50, 100].map((val) => (
                        <button
                          key={val}
                          type="button"
                          onClick={() => setForm({ ...form, amount: val })}
                          className="px-3 py-1 bg-[#2a2a2a] rounded hover:bg-[#3a3a3a]"
                        >
                          ${val}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm mb-1">Description</label>
                    <input
                      type="text"
                      name="description"
                      value={form.description}
                      onChange={handleChange}
                      className="w-full bg-[#0f0f0f] border border-gray-700 rounded p-2"
                      placeholder="What was this transaction for?"
                    />
                  </div>

                  {/* Date */}
                  <div>
                    <label className="block text-sm mb-1">Date</label>
                    <div className="relative">
                      <input
                        type="date"
                        name="transaction_date"
                        value={form.transaction_date}
                        onChange={handleChange}
                        className="w-full bg-[#0f0f0f] border border-gray-700 rounded p-2 pl-10"
                      />
                      <CalendarDays className="absolute left-2 top-2 text-gray-400" size={20} />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 1 && (
                <div className="mt-2 space-y-6">
                  <div className="rounded-lg border border-gray-700 bg-[#1a1a1a] text-white shadow-sm">
                    <div className="flex flex-col space-y-1.5 p-6">
                      <h3 className="text-2xl font-semibold leading-none tracking-tight">
                        Category & Classification
                      </h3>
                      <p className="text-sm text-gray-400">
                        Organize your transaction for better tracking
                      </p>
                    </div>

                    <div className="p-6 pt-0 space-y-6">
                      {/* Category */}
                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                          <label htmlFor="category_display_name" className="text-sm font-medium">
                            Category
                          </label>
                          <select
                            id="category_display_name"
                            name="category_display_name"
                            value={form.category_display_name}
                            onChange={handleChange}
                            className="flex h-10 w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm"
                          >
                            <option value="">Select category</option>
                            <option value="Thu nhập">Thu nhập</option>
                            <option value="Transportation">Transportation</option>
                            <option value="Entertainment">Entertainment</option>
                            <option value="Utilities">Utilities</option>
                            <option value="Housing">Housing</option>
                            <option value="Healthcare">Healthcare</option>
                            <option value="Shopping">Shopping</option>
                            <option value="Education">Education</option>
                            <option value="Insurance">Insurance</option>
                            <option value="Other">Other</option>
                          </select>
                        </div>
                      </div>

                      {/* Payment Method */}
                      <div className="space-y-2">
                        <label htmlFor="payment_method" className="text-sm font-medium">
                          Payment Method
                        </label>
                        <select
                          id="payment_method"
                          name="payment_method"
                          value={form.payment_method}
                          onChange={handleChange}
                          className="flex h-10 w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm"
                        >
                          <option value="cash">Cash</option>
                          <option value="credit">Credit Card</option>
                          <option value="debit">Debit Card</option>
                          <option value="bank_transfer">Bank Transfer</option>
                          <option value="check">Check</option>
                          <option value="digital_wallet">Digital Wallet</option>
                        </select>
                      </div>

                      {/* Location */}
                      <div className="space-y-2">
                        <label htmlFor="location" className="text-sm font-medium">
                          Location (Optional)
                        </label>
                        <input
                          id="location"
                          name="location"
                          value={form.location}
                          onChange={handleChange}
                          placeholder="Where did this transaction occur?"
                          className="flex h-10 w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm"
                        />
                      </div>

                      {/* Notes */}
                      <div className="space-y-2">
                        <label htmlFor="notes" className="text-sm font-medium">
                          Notes (Optional)
                        </label>
                        <textarea
                          id="notes"
                          name="notes"
                          rows="3"
                          value={form.notes}
                          onChange={handleChange}
                          placeholder="Add any additional details..."
                          className="flex min-h-[80px] w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm"
                        ></textarea>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 2 && (
                <div className="mt-2 space-y-6">
                  <div className="rounded-lg border border-gray-700 bg-[#1a1a1a] text-white shadow-sm">
                    <div className="flex flex-col space-y-1.5 p-6">
                      <h3 className="text-2xl font-semibold leading-none tracking-tight">
                        Advanced Options
                      </h3>
                      <p className="text-sm text-gray-400">
                        Set up recurring transactions and tags
                      </p>
                    </div>

                    <div className="p-6 pt-0 space-y-6">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="recurring"
                          className="h-4 w-4 rounded-sm border border-gray-500 bg-transparent text-white focus:ring-2 focus:ring-blue-500"
                        />
                        <label htmlFor="recurring" className="text-sm font-medium">
                          This is a recurring transaction
                        </label>
                      </div>

                      <div className="space-y-2">
                        <label className="text-sm font-medium">Tags</label>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            placeholder="Add a tag"
                            className="flex h-10 w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm"
                          />
                          <button
                            type="button"
                            className="h-10 px-4 rounded-md border border-gray-700 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-sm font-medium"
                          >
                            Add
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="p-6">
              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  className="h-10 px-4 py-2 rounded-md border border-gray-700 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-sm font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="h-10 px-4 py-2 rounded-md bg-white text-black hover:bg-gray-200 text-sm font-medium"
                >
                  Add Transaction
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </Layout>
  );
}
