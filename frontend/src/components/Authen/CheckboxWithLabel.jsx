const CheckboxWithLabel = ({ label, checked, onChange }) => (
  <label className="flex items-center space-x-2">
    <input type="checkbox" checked={checked} onChange={onChange} className="form-checkbox" />
    <span className="text-sm text-gray-600">{label}</span>
  </label>
);

export default CheckboxWithLabel;
