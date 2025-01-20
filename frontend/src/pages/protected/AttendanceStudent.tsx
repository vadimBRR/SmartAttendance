import React from 'react';
import { useParams } from 'react-router-dom';
import AttendanceTable from '../../components/AttandanceTable';
import {
  useAddLessonAttendance,
  useCurrentWeek,
  useLessonAttendanceByStudent,
} from '../../hooks/useApi';
import { useAuth } from '../../providers/AuthProvider';
import AttendanceTableStudent from '../../components/AttandanceTableStudent'

const AttendanceStudent = () => {
  const { id: lessonId } = useParams<{ id: string }>();
  const { data: weekNumber, isLoading: isWeekLoading, error: weekError } = useCurrentWeek();
  const { userId } = useAuth();

  if (!lessonId) return <div>No lesson ID provided</div>;
  if (!userId) return <div>No user ID provided</div>;

  const { data, isLoading, error } = useLessonAttendanceByStudent(
    parseInt(lessonId),
    userId
  );

  const { mutate: addAttendance } = useAddLessonAttendance(parseInt(lessonId));
  const short_course_name = data ? data[0].short_course_name : ''
  const course_name = data ? data[0].course_name : ''

  if (isLoading || isWeekLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {(error as Error).message}</div>;
  if (weekError) return <div>Error: {(weekError as Error).message}</div>;

  return (
    <div className="mx-2">
      <h1 className="text-3xl font-bold mb-6 text-[#2596be]">Attendance for Lesson: {course_name} ({short_course_name})</h1>
      <AttendanceTableStudent
        data={data || []} 
        lessonId={parseInt(lessonId)}
        addAttendance={addAttendance}
        weekNumber={weekNumber || 0}
      />
    </div>
  );
};

export default AttendanceStudent;
