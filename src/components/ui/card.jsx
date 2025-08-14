import React from 'react';
import clsx from 'clsx';

export function Card({ className, children }) {
  return (
    <div className={clsx("rounded-xl bg-[#121212] border border-gray-700 text-white shadow", className)}>
      {children}
    </div>
  );
}

export function CardContent({ className, children }) {
  return (
    <div className={clsx("p-6", className)}>
      {children}
    </div>
  );
}
