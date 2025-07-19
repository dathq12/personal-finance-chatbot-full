import logo from '../../assets/images/logo.png';

const LogoIcon = () => (
  <img
    src={logo}
    alt="Logo"
    className="h-10 w-10 rounded-lg object-cover select-none"
    draggable="false"
    onContextMenu={(e) => e.preventDefault()}
  />
);


export default LogoIcon;
