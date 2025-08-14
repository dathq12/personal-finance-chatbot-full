import logo from '../../assets/images/logo.png';

const LogoIcon = () => (
  <div className="h-10 w-10 bg-[#1e1e1e] rounded-lg">
    <img
      src={logo}
      alt="Logo"
      className="h-10 w-10 rounded-lg object-cover select-none"
      draggable="false"
      onContextMenu={(e) => e.preventDefault()}
    />
  </div>
);


export default LogoIcon;
