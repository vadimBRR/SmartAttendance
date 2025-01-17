import React from "react";
import { useNavigate } from "react-router-dom";

interface EmptyGroupItemProps {
  day: string; 
  time: string; 
}

const EmptyGroupItem: React.FC<EmptyGroupItemProps> = ({ day, time }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/create-group?day=${day}&time=${time}`);
  };

  return (
    <div
      className={`h-14 border bg-gray-200 flex items-center justify-center cursor-pointer transition-transform transform hover:scale-110 hover:bg-gray-300 relative`}
      onClick={handleClick}
      title={`Create group for ${day} at ${time}`}
    >
      <div
        className="absolute inset-0 flex items-center justify-center text-gray-500 text-xl opacity-0 hover:opacity-100 transition-opacity z-10"
      >
        +
      </div>
    </div>
  );
};

export default EmptyGroupItem;
