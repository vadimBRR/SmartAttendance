import React from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import AttendanceTable from '../../components/AttandanceTable';
import { useAddLessonAttendance, useCurrentWeek, useDeleteTestLesson, useLessonAttendance } from '../../hooks/useApi';

const Attendance = () => {
  const [searchParams] = useSearchParams();
  const { id: lessonId } = useParams<{ id: string }>();
  const weekNumber = useCurrentWeek();
  



  if (!lessonId) return <div>No lesson ID provided</div>;

  const {
    data,
    isLoading,
    error,
  } = useLessonAttendance(parseInt(lessonId || '0'));
  
  console.log(data);
  const { mutate: addAttendance } = useAddLessonAttendance(parseInt(lessonId),false );
  const short_course_name = data ? data.students[0].short_course_name : ''
  const course_name = data ? data.students[0].course_name : ''
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {(error as Error).message}</div>;

  

  return (
    <div className="mx-2">
      <h1 className="text-3xl font-bold mb-6 text-[#2596be]">Attendance for Lesson: {course_name} ({short_course_name})</h1>
      <AttendanceTable
        data={data?.students || []}
        lessonId={parseInt(lessonId)}
        addAttendance={addAttendance} 
        weekNumber={weekNumber.data || 0}
      />
    </div>
  );
};

export default Attendance;
