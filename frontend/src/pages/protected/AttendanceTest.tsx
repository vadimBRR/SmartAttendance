import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import AttendanceTable from '../../components/AttandanceTable';
import { useAddLessonAttendance, useCurrentWeek, useDeleteTestLesson, useTestLesson } from '../../hooks/useApi';
import { CircleStop, Pause } from 'lucide-react'

const AttendanceTest = () => {
  const navigate = useNavigate();
  const { data, isLoading, error } = useTestLesson();
  const weekNumber = 1


  const short_course_name = data?.students[0]?.short_course_name || '';
  const course_name = data?.students[0]?.course_name || '';
  
  const { mutate: addAttendance } = useAddLessonAttendance(data?.students[0]?.lesson_id!, true);
  const { mutate: deleteTestLesson } = useDeleteTestLesson();

  const handleDelete = () => {
    deleteTestLesson()
    navigate('/');

  }


  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {(error as Error).message}</div>;
  return (
    <div className="mx-2">
      <div className='flex flex-row justify-between'>
        <h1 className="text-3xl font-bold mb-6 text-[#2596be]">
          Attendance for Lesson: {course_name} ({short_course_name})
        </h1>
        <div>

          <button
              className="bg-[#2596be] text-white p-2 rounded shadow hover:bg-[#197b9b] transition"
              onClick={handleDelete}
              title="Stop Test Lesson"
            >
              <CircleStop size={24} />
            </button>
        </div>
      </div>
      <AttendanceTable
        data={data?.students || []}
        lessonId={data?.students[0]?.lesson_id || 0}
        addAttendance={addAttendance}
        weekNumber={weekNumber.data || 0}
      />
    </div>
  );
};

export default AttendanceTest;
