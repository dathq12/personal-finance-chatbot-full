import Sidebar from './Sidebar';
import Header from './Header';

const Layout = ({ children }) => (
  <div className="min-h-screen bg-[#121212] text-white h-dvh flex flex-col bg-gray-50">
    <Header />

    <div className="flex flex-1 min-h-0">
      <Sidebar />

      <main className="flex-1 flex flex-col min-h-0">
        {children}
      </main>
    </div>
  </div>
);

export default Layout;
