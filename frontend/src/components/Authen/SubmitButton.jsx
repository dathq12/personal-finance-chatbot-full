const SubmitButton = ({ label }) => (
  <button
    type="submit"
    className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-200"
  >
    {label}
  </button>
);

export default SubmitButton;
