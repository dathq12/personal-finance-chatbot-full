import { useState, useEffect, useRef } from 'react';
import Layout from '../components/Layout/Layout';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Xin chào! Tôi là trợ lý tài chính thông minh 🤖. Tôi có thể giúp bạn ghi nhận thu/chi, tư vấn ngân sách, hoặc trả lời câu hỏi tài chính.' },
    { type: 'user', text: 'Tôi nhận lương 10 triệu' },
    { type: 'bot', text: 'Ghi nhận thu 10 triệu vào danh mục: Lương?' },
  ]);
  const [input, setInput] = useState('');
  const messageEndRef = useRef(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { type: 'user', text: input }]);
    setInput('');

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { type: 'user', text: input },
        { type: 'bot', text: `Tôi đã ghi nhận: "${input}"` },
      ]);
    }, 600);
  };

  return (
    <Layout>
  <div className="min-h-screen bg-[#121212] text-white p-6 space-y-6 flex w-full h-dvh overflow-hidden">
      
        <div className="flex-1 flex flex-col h-full max-h-dvh">
          {/* Khu vực tin nhắn */}
          <div className="flex-1 overflow-y-auto py-4 px-6 space-y-4 flex flex-col w-full mx-auto overflow-x-hidden" style={{ scrollbarGutter: 'stable' }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`px-4 py-2 rounded-xl text-sm whitespace-pre-wrap w-fit max-w-[80%] ${
                  msg.type === 'bot'
                    ? 'bg-gray-100 text-gray-800 self-start text-left'
                    : 'bg-blue-600 text-white self-end text-right'
                }`}
              >
                {msg.text}
              </div>
            ))}
            <div ref={messageEndRef} />
          </div>

          {/* Input nhập tin nhắn */}
          <div className="border-t border-t-gray-700 p-4 flex items-center sticky bottom-0 z-10">
            <input
              type="text"
              placeholder="Nhập tin nhắn..."
              className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button
              onClick={handleSend}
              className="ml-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              ➤
            </button>
          </div>
        </div>
        </div>
</Layout>
  );
};

export default Chatbot;
