import React, { useState } from 'react';

interface Option {
  id: number;
  label: string;
}

interface CustomDropdownProps {
  options: Option[];
  selectedOption: number | null;
  onSelect: (id: number) => void;
}

const CustomDropdown = ({
  options,
  selectedOption,
  onSelect,
}: CustomDropdownProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full p-3 bg-white border rounded shadow-sm text-left focus:outline-none focus:ring-2 focus:ring-[#2596be]"
      >
        {selectedOption
          ? options.find((option) => option.id === selectedOption)?.label
          : 'Select a course'}
        <span className="absolute right-3 top-3 text-[#2596be]">▼</span>
      </button>
      {isOpen && (
        <div
          className="absolute z-10 mt-1 w-full bg-white border rounded shadow-md custom-scrollbar"
          style={{ maxHeight: '160px', overflowY: 'auto' }}
        >
          {options.map((option) => (
            <div
              key={option.id}
              onClick={() => {
                onSelect(option.id);
                setIsOpen(false);
              }}
              className="p-3 hover:bg-[#2596be] hover:text-white cursor-pointer"
            >
              {option.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CustomDropdown;
