import React, { useState, useEffect } from "react";
import { CalendarDays } from "lucide-react";
import Layout from "../components/Layout/Layout";
import API from "../services/api"
import { useNavigate } from "react-router-dom";



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
    const { name, value } = e.target;
    console.log("handleChange", name, value);
    setForm({ ...form, [name]: value });

    // if (name === "transaction_type") {
    //   fetchCategory(); // gọi hàm fetchCategory khi chọn radio
    // }
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
      alert("✅ Transaction đã được tạo thành công!");
      navigate("/manual-input"); 

    } catch (err) {
      console.error(err);
      alert("❌ Không thể tạo Transaction. Vui lòng thử lại.");
      navigate("/manual-input"); 
    }
  };

  const [activeTab, setActiveTab] = useState(0);
  const navigate = useNavigate();

  const [entries, setEntries] = useState([]);

  //Get category
  const fetchCategory = async () => {
    try {
      const token = sessionStorage.getItem("token");

      // Build query params từ filters
      const params = {};
      if (form.transaction_type) params.category_type = form.transaction_type;
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
      // params.append('skip', '0');
      // params.append('limit', '99');
      // params.append('is_active', 'true');
      // params.append('sort_order', 'desc');


      const res = await API.get(`/categories/my-categories`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json',
        },
        params: params
      });
      const data = res.data;
      console.log("API data:", data);

      // Giả sử API trả về mảng data
      setEntries(res.data.display_categories || []);
      console.log('Entries set:', res.data.display_categories);
    } catch (error) {
      console.error("Failed to fetch display_categories:", error);
      setEntries([]);
    }
  }

  const [isOpen, setIsOpen] = useState(false);
  const [custom_name, setName] = useState("");
  const [category_type, setType] = useState("income");

  const handleCreateCategory = async () => {
    if (!custom_name?.trim()) {
      alert("Vui lòng nhập tên category");
      return;
    }

    try {
      const token = sessionStorage.getItem("token");
      const payload = { custom_name: custom_name, category_type: category_type }; // hoặc { name, type } tùy backend

      const res = await API.post("/categories/user-categories/", payload, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      });

      // axios trả về res.status / res.data
      if (res.status !== 200 && res.status !== 201) {
        throw new Error("Tạo category thất bại");
      }


      alert("Tạo category thành công");
      setIsOpen(false);
      setName("");
      setType("income");
      // gọi lại fetch danh sách category nếu cần:
      fetchCategory();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || err.message || "Đã có lỗi");
    }
  };


  useEffect(() => {
    fetchCategory();
  }, [form.transaction_type]);


  return (
    <Layout>
      <form onSubmit={handleSubmit}>
        <div className="flex h-screen bg-[#0f0f0f] text-white">
          <div className="flex-1 flex flex-col">
            <header className="p-4 flex justify-between items-center border-b border-gray-700">
              <h2 className="text-2xl font-bold">Add New Transaction</h2>
            </header>

            <div className="p-6">
              <p className="text-gray-400 mb-4">Record a new income or expense transaction</p>

              {/* Tabs */}
              <div className="flex border-b border-gray-700 mb-6">
                {[
                  "Basic Info",
                  "Details"
                  //  ,"Advanced"
                ].map((tab, i) => (
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
                      {[100000, 250000, 500000, 1000000].map((val) => (
                        <button
                          key={val}
                          type="button"
                          onClick={() => setForm({ ...form, amount: val })}
                          className="px-3 py-1 bg-[#2a2a2a] rounded hover:bg-[#3a3a3a]"
                        >
                          {val} VNĐ
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
                      <div className="grid gap-4 md:grid-cols-1">
                        <div className="space-y-2">
                          <label htmlFor="category_display_name" className="text-sm font-medium">
                            Category
                          </label>
                          <div className="flex justify-center items-cente gap-4">
                            <select
                              name="category_display_name"
                              value={form.category_display_name}
                              onChange={handleChange}
                              className="flex h-10 w-full rounded-md border border-gray-700 bg-[#0f0f0f] px-3 py-2 text-sm"
                            >
                              <option value="" disabled>
                                {entries.length === 0 ? "No category found. Add new category!" : "Select category"}
                              </option>
                              {entries.map((entry) => (
                                <option key={entry.id || entry.display_name} value={entry.display_name}>
                                  {entry.display_name}
                                </option>
                              ))}
                            </select>


                            <button
                              type="button"
                              onClick={() => setIsOpen(true)}
                              className="w-1/3 w-full h-10 rounded-md bg-yellow-500 hover:bg-yellow-600 text-black font-semibold py-2 text-sm transition-colors duration-200  px-3 py-2 "
                            >
                              + Tạo category mới
                            </button>
                            {/* Popup */}
                            {isOpen && (
                              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                                <div className="bg-[#0f0f0f] p-6 rounded-lg w-96 shadow-lg">
                                  <h2 className="text-lg font-bold mb-4">Tạo category mới</h2>

                                  {/* Tên category */}
                                  <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">
                                      Tên category
                                    </label>
                                    <input
                                      type="text"
                                      value={custom_name}
                                      onChange={(e) => setName(e.target.value)}
                                      className="w-full bg-[#0f0f0f] border border-gray-700 rounded p-2"
                                    />
                                  </div>

                                  {/* Loại category */}
                                  <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">
                                      Loại category
                                    </label>
                                    <select
                                      value={category_type}
                                      onChange={(e) => setType(e.target.value)}
                                      className="w-full bg-[#0f0f0f] border border-gray-700 rounded p-2"
                                    >
                                      <option value="income">Income</option>
                                      <option value="expense">Expense</option>
                                    </select>
                                  </div>

                                  {/* Nút hành động */}
                                  <div className="flex justify-end gap-3">
                                    <button
                                      onClick={() => setIsOpen(false)}
                                      className="h-10 px-4 py-2 rounded-md border border-gray-700 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-sm font-medium"
                                    >
                                      Hủy
                                    </button>
                                    <button
                                      onClick={handleCreateCategory}
                                      className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-black font-semibold rounded"
                                    >
                                      Tạo
                                    </button>
                                  </div>
                                </div>
                              </div>
                            )}

                          </div>
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

              {/* {activeTab === 2 && (
                
              )} */}
            </div>

            {/* Buttons */}
            {/* Buttons */}
            <div className="p-6">
              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  className="h-10 px-4 py-2 rounded-md border border-gray-700 bg-[#2a2a2a] hover:bg-[#3a3a3a] text-sm font-medium"
                  onClick={() => {
                    navigate("/manual-input");
                    console.log("Button Cancel clicked");
                  }}
                >
                  Cancel
                </button>

                {activeTab === 0 && (
                  <button
                    type="button"
                    className="h-10 px-4 py-2 rounded-md bg-white text-black hover:bg-gray-200 text-sm font-medium"
                    onClick={() => setActiveTab(1)}
                  >
                    Next
                  </button>
                )}

                {activeTab === 1 && (
                  <button
                    type="submit"
                    className="h-10 px-4 py-2 rounded-md bg-white text-black hover:bg-gray-200 text-sm font-medium"
                  >
                    Submit
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </form>
    </Layout>
  );
}
