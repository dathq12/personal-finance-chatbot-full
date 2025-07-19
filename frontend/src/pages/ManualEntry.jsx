import { useState } from 'react';
import Layout from '../components/Layout/Layout';

const ManualEntry = () => {
  const [type, setType] = useState('Thu');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [note, setNote] = useState('');
  const [dateTime, setDateTime] = useState(new Date().toISOString().slice(0, 16)); // format YYYY-MM-DDTHH:mm

  const handleSave = () => {
    // TODO: Call API to save
    console.log({ type, amount, category, note, dateTime });
  };

  return (
    <Layout>
      <div className="flex w-full h-dvh overflow-hidden">
        <div className="flex-1 bg-white px-8 py-6 overflow-y-auto">
          <div className="text-sm">
          <h2 className="text-xl font-semibold mb-6">Nhập thu/chi thủ công</h2>

          <div className="space-y-5 max-w-md">
            {/* Loại */}
            <div>
              <label className="block font-medium mb-1">Loại</label>
              <select
                className="w-full border rounded-lg px-4 py-2"
                value={type}
                onChange={(e) => setType(e.target.value)}
              >
                <option value="Thu">Thu</option>
                <option value="Chi">Chi</option>
              </select>
            </div>

            {/* Số tiền */}
            <div>
              <label className="block font-medium mb-1">Số tiền</label>
              <input
                type="number"
                className="w-full border rounded-lg px-4 py-2"
                placeholder="₫"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>

            {/* Danh mục */}
            <div>
              <label className="block font-medium mb-1">Danh mục</label>
              <input
                type="text"
                className="w-full border rounded-lg px-4 py-2"
                placeholder="Chọn danh mục"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>

            {/* Lý do */}
            <div>
              <label className="block font-medium mb-1">Lý do</label>
              <input
                type="text"
                className="w-full border rounded-lg px-4 py-2"
                placeholder="Nhập lý do chi tiết"
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
            </div>

            {/* Thời gian */}
            <div>
              <label className="block font-medium mb-1">Thời gian</label>
              <input
                type="datetime-local"
                className="w-full border rounded-lg px-4 py-2"
                value={dateTime}
                onChange={(e) => setDateTime(e.target.value)}
              />
            </div>

            {/* Nút Lưu */}
            <div className="pt-4">
              <button
                onClick={handleSave}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Lưu
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </Layout>
  );
};

export default ManualEntry;
