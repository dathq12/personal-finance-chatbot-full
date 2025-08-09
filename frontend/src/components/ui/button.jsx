import React from 'react';
import clsx from 'clsx';

export function Button({ className, variant = 'default', size = 'md', ...props }) {
  const base = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  const variants = {
    default: 'bg-blue-600 text-black hover:bg-blue-700',
    outline: 'border border-gray-300 hover:bg-gray-100',
  };
  const sizes = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4 text-sm',
    lg: 'h-12 px-6 text-base',
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className || ''}`}
      {...props}
    />
  );
}

