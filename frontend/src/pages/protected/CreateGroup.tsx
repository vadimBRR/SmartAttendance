import React from 'react';
import { useSearchParams } from 'react-router-dom';

const CreateGroup: React.FC = () => {
  const [searchParams] = useSearchParams();
  const day = searchParams.get('day');
  const start_time = searchParams.get('start_time');
  const finish_time = searchParams.get('finish_time');
  const course_id = searchParams.get('course_id');

  return (
    <div className='p-4'>
      <h1 className='text-2xl font-bold mb-4'>Create Group</h1>
      <p>Day: {day}</p>
      <p>Start Time: {start_time}</p>
      <p>Finish Time: {finish_time}</p>
      <p>Course ID: {course_id}</p>

      {/* Форма або інші елементи для створення групи */}
    </div>
  );
};

export default CreateGroup;
