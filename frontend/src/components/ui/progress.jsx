import React from 'react';
import clsx from 'clsx';

export function Progress({ value, className }) {
  return (
    <div className={clsx("w-full h-2 bg-gray-200 rounded-full", className)}>
      <div
        className="h-full bg-blue-600 rounded-full transition-all"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}
