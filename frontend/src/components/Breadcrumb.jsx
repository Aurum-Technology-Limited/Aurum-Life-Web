import React from 'react';
import { ChevronRight } from 'lucide-react';

const Breadcrumb = ({ items = [] }) => {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <nav className="flex items-center space-x-2 text-sm mb-6">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <ChevronRight size={16} className="text-gray-500" />
          )}
          <span
            className={`${
              item.href && item.onClick
                ? 'text-yellow-400 hover:text-yellow-300 cursor-pointer transition-colors'
                : index === items.length - 1
                ? 'text-gray-300 font-medium'
                : 'text-gray-400'
            }`}
            onClick={item.onClick || undefined}
          >
            {item.name}
          </span>
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumb;