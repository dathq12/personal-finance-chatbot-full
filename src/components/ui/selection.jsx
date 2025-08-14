import React from "react";

const Select = ({ options = [], value, onChange, className = "" }) => {
  return (
    <select
      value={value}
      onChange={onChange}
      className={`px-3 py-2 w-full rounded bg-[#121212] border border-gray-700 text-white appearance-none
                  focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    >
      {options.map((option, index) => (
        <option key={index} value={option.value} className="text-black">
          {option.label}
        </option>
      ))}
    </select>
  );
};

export default Select;
