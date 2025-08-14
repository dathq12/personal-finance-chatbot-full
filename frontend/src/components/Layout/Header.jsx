import { FiUser, FiBell } from 'react-icons/fi';
import LogoIcon from '../ui/LogoIcon';
import { Link } from 'react-router-dom';

const Header = () => (
  <div className="bg-[#1e1e1e] text-white flex items-center justify-between px-6 py-4 shadow-sm">
    <div className="h-10 w-10 bg-[#1e1e1e] rounded-lg"> 
      <Link to="/dashboard">
        <LogoIcon/>
      </Link>
      
    </div>
    <h1 className="text-lg text-white font-bold">AI Finance Magement</h1>
    <div className="flex items-center gap-4">
      {/* <div className="flex items-center space-x-2">
        <FiBell className="text-black" size={20} />
      </div> */}
      {/* <div className="flex items-center space-x-2">
        <Link to="/account">
          <FiUser className="text-white" size={20}/>
        </Link>
      </div> */}
    </div>
  </div>
);

export default Header;
