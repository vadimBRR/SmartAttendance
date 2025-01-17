import React from 'react';
import AttendanceTable from '../../components/AttandanceTable';
import { useLessonAttendance } from '../../hooks/useApi';
import { useParams } from 'react-router-dom'

const Attendance = () => {
  const { id: lessonId } = useParams<{ id: string }>();
  // const lessonId = 1; // Змініть на динамічний ID, якщо потрібно
  if (!lessonId) return <div>No lesson ID provided</div>;
  const { data, isLoading, error } = useLessonAttendance(parseInt(lessonId!));

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {(error as Error).message}</div>;

  return (
    <div className=''>
      <AttendanceTable data={data.students || []} />
    </div>
  );
};

export default Attendance;
