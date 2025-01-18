import React from 'react';

interface CustomCheckboxProps {
  checked: boolean;
  onChange: () => void;
}

const CustomCheckbox: React.FC<CustomCheckboxProps> = ({ checked, onChange }) => {
  return (
    <div
      className={`w-6 h-6 flex items-center justify-center rounded-full cursor-pointer transition-all ${
        checked ? 'bg-[#2596be] text-white shadow-md scale-105' : 'bg-gray-200'
      }`}
      onClick={onChange}
    >
      <div
        className={`w-3 h-3 rounded-full transition-all ${
          checked ? 'bg-white' : 'bg-transparent'
        }`}
      ></div>
    </div>
  );
};

export default CustomCheckbox;
