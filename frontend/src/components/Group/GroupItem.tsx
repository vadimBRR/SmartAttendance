import React from "react";
import { useNavigate } from 'react-router-dom'

interface GroupItemProps {
  id: number | null;
  group?: {
    start_time: string;
    finish_time: string;
    short_course_name: string;
    
  };
  
}

const GroupItem = ({ id, group, }: GroupItemProps) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (id) {
      navigate(`/attendance/${id}`);
    }
  };

  const tooltipText = group
    ? `Start: ${group.start_time}, End: ${group.finish_time}`
    : "";

  return (
    <div
      className={`h-14 border ${
        group
          ? "bg-green-600 text-white cursor-pointer hover:bg-green-700 transition hover:scale-105"
          : "bg-gray-200"
      } flex items-center justify-center`}
      onClick={handleClick}
      title={tooltipText} 
    >
      {group ? group.short_course_name + " - " + id : ""}
    </div>
  );
};

export default GroupItem;
