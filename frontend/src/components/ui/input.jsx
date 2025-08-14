import React from "react";

const Input = React.forwardRef((props, ref) => {
  const { className = "", type = "text", ...rest } = props;

  return (
    <input
      ref={ref}
      type={type}
      className={`px-3 py-2 w-full p-2 rounded bg-[#121212] border border-gray-700 text-white ${className}`}
      {...rest}
    />
    
  );
});

Input.displayName = "Input";

export { Input };
