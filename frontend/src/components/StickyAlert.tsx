import React from 'react';

interface StickyAlertProps {
  message: string;
  onClose: () => void;
}

const StickyAlert: React.FC<StickyAlertProps> = ({ message, onClose }) => {
  return (
    <div
      className="fixed bottom-5 left-1/2 transform -translate-x-1/2 w-4/5 bg-red-500 text-white p-4 shadow-md z-50 flex justify-between items-center rounded"
    >
      <span>{message}</span>
      <button
        onClick={onClose}
        className="text-lg font-bold px-2 hover:bg-red-600 rounded"
      >
        &times;
      </button>
    </div>
  );
};

export default StickyAlert;
