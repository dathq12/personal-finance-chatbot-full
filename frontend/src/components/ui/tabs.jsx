import React, { useState } from 'react';
import clsx from 'clsx';

export function Tabs({ defaultValue, children, className }) {
  const [value, setValue] = useState(defaultValue);
  return (
    <div className={className}>
      {React.Children.map(children, child =>
        React.cloneElement(child, { value, setValue })
      )}
    </div>
  );
}

export function TabsList({ children, value, setValue }) {
  return (
    <div className="inline-flex items-center border rounded-md overflow-hidden mb-4">
      {React.Children.map(children, child =>
        React.cloneElement(child, { value, setValue })
      )}
    </div>
  );
}

export function TabsTrigger({ children, value: triggerValue, value, setValue }) {
  const isActive = value === triggerValue;
  return (
    <button
      className={clsx(
        "px-4 py-2 text-sm font-medium",
        isActive ? "bg-blue-600 text-white" : "bg-white text-gray-600 hover:bg-gray-100"
      )}
      onClick={() => setValue(triggerValue)}
    >
      {children}
    </button>
  );
}