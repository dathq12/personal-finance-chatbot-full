const AuthFooter = ({ question, linkText, linkHref }) => (
  <p className="text-center text-sm text-gray-600 mt-6">
    {question}{' '}
    <a href={linkHref} className="text-blue-600 hover:underline">
      {linkText}
    </a>
  </p>
);

export default AuthFooter;
