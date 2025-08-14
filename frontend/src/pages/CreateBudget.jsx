import React, { useState, useEffect } from "react";
import Layout from "../components/Layout/Layout";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

export default function CreateBudget() {
  const steps = ["Basic Info", "Categories"];
  const [currentStep, setCurrentStep] = useState(0);


  const navigate = useNavigate();


  const [formData, setFormData] = useState({
    budget_name: "",
    budget_type: "monthly",
    amount: "",
    period_start: "",
    period_end: ""
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   if (currentStep < steps.length - 1) {
  //     setCurrentStep((prev) => prev + 1);
  //     return;
  //   }
  //   try {
  //     const token = sessionStorage.getItem("token");
  //     const res = await API.post("/budgets/", formData, {
  //       headers: {
  //         Accept: "application/json",
  //         Authorization: `Bearer ${token}`,
  //       }
  //     });
  //     console.log("Kết quả API:", res.data);
  //     handleSubmit2();
  //     setFormData({
  //       budget_name: "",
  //       budget_type: "monthly",
  //       amount: "",
  //       period_start: "",
  //       period_end: "",
  //     });
  //     setCurrentStep(0);
  //   } catch (err) {
  //     console.error("Lỗi API:", err);
  //   }
  // };

  const [entries, setEntries] = useState([]);

  const fetchCategory = async () => {
    try {
      const token = sessionStorage.getItem("token");

      // Build query params từ filters
      const params = {
        skip: 0,
        limit: 99,
        is_active: true,
        sort_order: "desc"
      };
      // if (form.transaction_type) params.category_type = form.transaction_type;
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


      const res = await API.get(`/categories/my-categories?category_type=expense`, {
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

  const [entries2, setEntries2] = useState([]);

  const [formData2, setFormData2] = useState({
    display_name: "",
    user_category_id: "",
    amount: ""
  });

  const handleAddCategory = () => {
    if (!formData2.display_name) {
      console.warn("[handleAddCategory] Thiếu dữ liệu => Không thêm");
      return;
    }

    setEntries2((prev) => [
      ...prev,
      {
        display_name: formData2.display_name,
        user_category_id: formData2.user_category_id,
        amount: parseFloat(formData2.amount) || 0
      }
    ]);

    setFormData2({ display_name: "", user_category_id: "", amount: "" }); // reset form
  };

  const handleDelete = (index) => {
    setEntries2((prev) => prev.filter((_, i) => i !== index));
  };

  const handleChangeCategory = (e) => {
    const { name, value } = e.target; // lấy cả name và value
    console.log("[handleChangeCategory] name:", name, "value:", value);

    if (name === "user_category_id") {
      const selected = entries.find(
        (item) => String(item.user_category_id) === String(value)
      );
      setFormData2((prev) => ({
        ...prev,
        user_category_id: value,
        display_name: selected?.display_name || ""
      }));
    } else {
      setFormData2((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  // const handleSubmit2 = async (e) => {
  //   // e.preventDefault();
  //   // if (currentStep < steps.length - 1) {
  //   //   setCurrentStep((prev) => prev + 1);
  //   //   return;
  //   // }

  //   // const params = {};
  // const payload = {
  //   user_category_id: formData2.user_category_id,
  //   allocated_amount: formData2.amount,
  // };

  //   try {
  //     const token = sessionStorage.getItem("token");
  //     const res = await API.post(`/budgets/${data.BudgetID}`, payload, {
  //       headers: {
  //         Accept: "application/json",
  //         Authorization: `Bearer ${token}`,
  //       }
  //       // ,params: params
  //     });
  //     console.log("Kết quả API:", res.data);
  //     setCurrentStep(0);
  //   } catch (err) {
  //     console.error("Lỗi API:", err);
  //   }
  // };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (currentStep < steps.length - 1) {
      setCurrentStep((prev) => prev + 1);
      return;
    }

    try {
      const token = sessionStorage.getItem("token");

      // 1️⃣ Tạo budget
      const res = await API.post("/budgets/", formData, {
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        }
      });

      console.log("Budget created:", res.data);
      const budgetId = res.data?.BudgetID;

      if (!budgetId) {
        console.error("Không tìm thấy BudgetID trong response");
        return;
      }

      // 2️⃣ Gửi từng category
      let allSuccess = true;

      for (const cat of entries2) {
        const payload = {
          category_display_name: cat.display_name,
          allocated_amount: cat.amount
        };

        try {
          const res2 = await API.post(`/budgets/${budgetId}/categories`, payload, {
            headers: {
              Accept: "application/json",
              Authorization: `Bearer ${token}`,
            }
          });
          console.log(`Category ${cat.display_name} added:`, res2.data);
        } catch (err) {
          allSuccess = false;
          console.error(`Lỗi khi thêm category ${cat.display_name}:`, err);
        }
      }

      // 3️⃣ Reset form
      setFormData({
        budget_name: "",
        budget_type: "monthly",
        amount: "",
        period_start: "",
        period_end: "",
      });
      setEntries2([]);
      setCurrentStep(0);

      // 4️⃣ Thông báo thành công
      if (allSuccess) {
        alert("✅ Budget đã được tạo thành công!");
        navigate("/budget"); 
      } else {
        alert("⚠ Budget tạo thành công nhưng một số category bị lỗi.");
        navigate("/budget"); 
      }

    } catch (err) {
      console.error("Lỗi tạo budget:", err);
      alert("❌ Không thể tạo Budget. Vui lòng thử lại.");
    }
  };

  const totalBudget = parseFloat(formData.amount) || 0;
  const allocated = entries2.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0);
  const remaining = totalBudget - allocated;

  useEffect(() => {
    if (currentStep === 1) {
      fetchCategory();
    }
  }, [currentStep]);



  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="bg-[#111] p-6 rounded-lg">
            <h2 className="text-lg font-semibold mb-4">Budget Basics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm mb-1">Budget Name</label>
                <input
                  type="text"
                  name="budget_name"
                  placeholder="e.g., Monthly Budget 2025"
                  value={formData.budget_name}
                  onChange={handleChange}
                  className="w-full bg-black border border-gray-600 rounded px-3 py-2 text-white placeholder-gray-500"
                />
              </div>
              <div>
                <label className="block text-sm mb-1">Budget Period</label>
                <select
                  name="budget_type"
                  value={formData.budget_type}
                  onChange={handleChange}
                  className="w-full bg-black border border-gray-600 rounded px-3 py-2"
                >
                  <option value="monthly">Monthly</option>
                  <option value="weekly">Weekly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-sm mb-1">Total Budget Amount</label>
              <div className="flex items-center">
                <span className="bg-gray-800 px-3 border border-gray-600 border-r-0 rounded-l">VNĐ</span>
                <input
                  type="number"
                  name="amount"
                  value={formData.amount}
                  onChange={handleChange}
                  className="flex-1 bg-black border border-gray-600 rounded-r px-3 py-2"
                />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm mb-1">Start Date</label>
                <input
                  type="date"
                  name="period_start"
                  value={formData.period_start}
                  onChange={handleChange}
                  className="w-full bg-black border border-gray-600 rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm mb-1">End Date (Optional)</label>
                <input
                  type="date"
                  name="period_end"
                  value={formData.period_end}
                  onChange={handleChange}
                  className="w-full bg-black border border-gray-600 rounded px-3 py-2"
                />
              </div>
            </div>
          </div>
        );
      case 1:
        return (
          <div className="rounded-lg border bg-card text-card-foreground shadow-2xs">
            {/* <!-- Header --> */}
            <div className="flex flex-col space-y-1.5 p-6">
              <h3 className="text-2xl font-semibold leading-none tracking-tight flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                  <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                </svg>
                Budget Categories
              </h3>
              <p className="text-sm text-muted-foreground">Allocate your budget across different spending categories</p>
            </div>

            {/* <!-- Content --> */}
            <div className="p-6 pt-0 space-y-6">
              {/* <!-- Budget Overview --> */}
              <div className="p-4 bg-muted/50 rounded-lg">
                <div className="grid gap-4 md:grid-cols-3 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{totalBudget.toLocaleString()} VNĐ</div>
                    <div className="text-sm text-muted-foreground">Total Budget</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{allocated.toLocaleString()} VNĐ</div>
                    <div className="text-sm text-muted-foreground">Allocated</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{remaining.toLocaleString()} VNĐ</div>
                    <div className="text-sm text-muted-foreground">Remaining</div>
                  </div>
                </div>

                {/* <!-- Progress bar --> */}
                <div className="relative w-full overflow-hidden rounded-full bg-secondary h-2">
                  <div
                    className="h-full bg-green-500 transition-all"
                    style={{ width: `${totalBudget > 0 ? (allocated / totalBudget) * 100 : 0}%` }}
                  ></div>
                </div>
                <div className="text-center text-sm text-muted-foreground mt-2">{totalBudget > 0
                  ? Math.floor((allocated / totalBudget) * 100)
                  : 0}%</div>
              </div>
              {/* Current Categories */}
              <div>
                <h4 className="font-medium mb-2">Current Categories</h4>
                {entries2.map((entry, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center border rounded-md p-3 mb-2"
                  >
                    <div>
                      <div className="font-semibold">{entry.display_name}</div>
                      <div className="text-sm text-gray-500">
                        {totalBudget > 0 ? ((entry.amount / totalBudget) * 100).toFixed(1) : 0}% of budget
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-3 py-1 border rounded-md">{entry.amount}</span>
                      <button
                        onClick={() => handleDelete(idx)}
                        type="button"
                        className="text-red-500 hover:text-red-700"
                      >
                        🗑
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              {/* <!-- Add New Category --> */}
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-4">
                <h4 className="font-medium mb-4">Add New Category</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  {/* <!-- Category Name --> */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none">Category Name</label>
                    <select
                      name="user_category_id"
                      value={formData2.user_category_id}
                      onChange={handleChangeCategory}
                      className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm text-black"
                    >
                      <option value="">-- Choose category --</option>
                      {entries.length === 0 ? (
                        <option disabled>No category found. Add new category!</option>
                      ) : (
                        entries.map((entry) => (
                          <option
                            key={entry.user_category_id}
                            value={entry.user_category_id}
                          >
                            {entry.display_name}
                          </option>
                        ))
                      )}
                    </select>
                    {/* <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor"> */}
                    {/* <path d="m6 9 6 6 6-6"></path>
                    </svg> */}
                  </div>

                  {/* <!-- Amount --> */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none">Amount</label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm font-medium text-gray-600">
                        VNĐ
                      </span>
                      <input
                        type="number"
                        step="0.01"
                        name="amount"
                        value={formData2.amount}
                        onChange={handleChangeCategory}
                        placeholder="0.00"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 pl-20 text-sm text-black"
                      />
                    </div>
                  </div>

                </div>

                <div className="mt-4 flex justify-end">
                  <button
                    onClick={handleAddCategory}
                    type="button"
                    className="bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path d="M5 12h14"></path>
                      <path d="M12 5v14"></path>
                    </svg>
                    Add Category
                  </button>
                </div>
              </div>
              
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Layout>
      <div className="h-dvh bg-black text-white p-8">
        <div className="max-w-3xl mx-auto">
          {/* Title */}
          <h1 className="text-2xl font-bold">Create New Budget</h1>
          <p className="text-gray-400 mb-8">
            Set up a budget to track your spending goals
          </p>

          {/* Steps */}
          <div className="flex justify-between mb-6">
            {steps.map((label, i) => (
              <div key={i} className="flex flex-col items-center flex-1">
                <div
                  className={`w-8 h-8 flex items-center justify-center rounded-full border ${i === currentStep
                    ? "bg-white text-black"
                    : "border-gray-600 text-gray-500"
                    }`}
                >
                  {i + 1}
                </div>
                <span
                  className={`mt-2 text-sm ${i === currentStep ? "text-white" : "text-gray-500"
                    }`}
                >
                  {label}
                </span>
              </div>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            {renderStepContent()}

            {/* Actions */}
            <div className="flex justify-between mt-6">
              <button
                type="button"
                onClick={() => setCurrentStep((prev) => Math.max(prev - 1, 0))}
                disabled={currentStep === 0}
                className="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700 disabled:opacity-50"
              >
                Previous
              </button>
              <div className="flex gap-3">
                <button
                  type="button"
                  setCurrentStep
                  onClick={() => {
                    navigate("/budget");
                    console.log("Button Cancel clicked");
                  }}
                  className="px-4 py-2 rounded bg-gray-800 hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-white text-black hover:bg-gray-200"
                >
                  {currentStep === steps.length - 1 ? "Submit" : "Next"}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}
