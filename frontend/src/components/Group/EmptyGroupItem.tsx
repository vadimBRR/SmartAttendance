import React from 'react';
import { useNavigate } from 'react-router-dom';

interface EmptyGroupItemProps {
  day: string;
  start_time: string;
  finish_time: string;
  course_id: number;
}

const EmptyGroupItem: React.FC<EmptyGroupItemProps> = ({
  day,
  start_time,
  finish_time,
  course_id,
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(
      `/create-group?day=${day}&start_time=${start_time}&finish_time=${finish_time}&course_id=${course_id}`
    );
  };

  return (
    <div
      className={`h-14 border bg-gray-200 flex items-center justify-center cursor-pointer transition-transform transform hover:scale-110 hover:bg-gray-300 relative`}
      onClick={handleClick}
      title={`Create group for ${day} from ${start_time} to ${finish_time}`}
    >
      <div className='absolute inset-0 flex items-center justify-center text-gray-500 text-xl opacity-0 hover:opacity-100 transition-opacity z-10'>
        +
      </div>
    </div>
  );
};

export default EmptyGroupItem;
