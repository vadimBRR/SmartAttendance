import React from 'react';
import { useParams } from 'react-router-dom';
import AttendanceTable from '../../components/AttandanceTable';
import { useAddLessonAttendance, useLessonAttendance } from '../../hooks/useApi';

const Attendance = () => {
  const { id: lessonId } = useParams<{ id: string }>();
  if (!lessonId) return <div>No lesson ID provided</div>;

  // Отримуємо дані про відвідуваність
  const { data, isLoading, error } = useLessonAttendance(parseInt(lessonId));

  // Використовуємо мутацію для оновлення відвідуваності
  const { mutate: addAttendance } = useAddLessonAttendance(parseInt(lessonId));

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {(error as Error).message}</div>;

  return (
    <div className="attendance-page">
      <AttendanceTable
        data={data?.students || []}
        lessonId={parseInt(lessonId)}
        addAttendance={addAttendance} // Передаємо мутацію для оновлення відвідуваності
      />
    </div>
  );
};

export default Attendance;
