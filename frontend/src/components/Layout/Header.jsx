import { FiUser, FiBell } from 'react-icons/fi';
import LogoIcon from '../Authen/LogoIcon';
import { Link } from 'react-router-dom';

const Header = () => (
  <div className="flex items-center justify-between px-6 py-4 border-b bg-white shadow-sm">
    <div className="h-10 w-10 bg-gray-300 rounded-lg"> 
      <Link to="/dashboard">
        <LogoIcon/>
      </Link>
    </div>
    <h1 className="text-lg text-black font-bold">TRỢ LÝ TÀI CHÍNH THÔNG MINH</h1>
    <div className="flex items-center gap-4">
      {/* <div className="flex items-center space-x-2">
        <FiBell className="text-black" size={20} />
      </div> */}
      <div className="flex items-center space-x-2">
        <Link to="/account">
          <FiUser className="text-black" size={20}/>
        </Link>
      </div>
    </div>
  </div>
);

export default Header;
