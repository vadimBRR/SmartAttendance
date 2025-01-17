import React from "react";
import { useNavigate } from 'react-router-dom'

interface GroupItemProps {
  group?: { id: number };
}

const GroupItem: React.FC<GroupItemProps> = ({ group }) => {
  
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/attendance/${group?.id}`);
  };
  return (
    <div
      className={`h-14 border ${
        group ? "bg-green-600 text-white cursor-pointer hover:bg-green-700 transition hover:scale-105" : "bg-gray-200"
      } flex items-center justify-center `} onClick={handleClick}
    >
      {group ? `Group ${group.id}` : ""}
    </div>
  );
};

export default GroupItem;
