import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import CustomDropdown from '../../components/CustomDropdown';
import StickyAlert from '../../components/StickyAlert';
import { useAddLesson, useStudentsWithoutGroup, useCourses } from '../../hooks/useApi'; // Імпортуємо хук

// Типізація для курсу
interface Course {
  id: number;
  name: string;
  short_name?: string; // Якщо є скорочення
}

// Типізація для студента
interface Student {
  id: number;
  name: string;
}

const CreateGroup: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const addLessonMutation = useAddLesson(); // Використовуємо useAddLesson хук для додавання уроку

  const day = searchParams.get('day') || '';
  const start_time = searchParams.get('start_time') || '';
  const finish_time = searchParams.get('finish_time') || '';
  const teacher_id = 1; // Замінено статичним значенням
  const classroom_id = 1; // Замінено статичним значенням

  // Використання хука для отримання курсів
  const { data: courses, isLoading: isCoursesLoading, error: coursesError } = useCourses(teacher_id);

  // Використання хука для отримання студентів без групи
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const { data: students, isLoading: isStudentsLoading, error: studentsError } = useStudentsWithoutGroup(
    selectedCourseId || 0
  );

  const current_week = 5;

  const [selectedStudents, setSelectedStudents] = useState<number[]>([]);
  const [attendance, setAttendance] = useState<Record<number, (boolean | null)[]>>({});

  const [alertMessage, setAlertMessage] = useState<string | null>(null);

  // Коли обирається новий курс, оновлюємо студентів
  useEffect(() => {
    if (students) {
      setSelectedStudents(students.map((student: Student) => student.id));
      setAttendance(
        students.reduce((acc: Record<number, (boolean | null)[]>, student: Student) => {
          acc[student.id] = Array(current_week).fill(true);
          return acc;
        }, {} as Record<number, (boolean | null)[]>)
      );
    }
  }, [students]);

  const toggleStudentSelection = (id: number) => {
    setSelectedStudents((prev) =>
      prev.includes(id) ? prev.filter((studentId) => studentId !== id) : [...prev, id]
    );
  };

  const cycleAttendance = (studentId: number, weekIndex: number) => {
    setAttendance((prev) => ({
      ...prev,
      [studentId]: prev[studentId].map((value, index) => {
        if (index !== weekIndex) return value;
        if (value === true) return false;
        if (value === false) return null;
        return true;
      }),
    }));
  };

  const handleSubmit = () => {
    if (!selectedCourseId) {
      setAlertMessage('Please select a course before submitting.');
      return;
    }
    if (selectedStudents.length === 0) {
      setAlertMessage('Please select at least one student.');
      return;
    }
  
    const formatTime = (time: string): string => {
      const [hour, minute, second] = time.split(':');
      return `${hour.padStart(2, '0')}:${minute}:${second || '00'}`;
    };
  
    const fullDayNames = {
      Mon: 'Monday',
      Tue: 'Tuesday',
      Wed: 'Wednesday',
      Thu: 'Thursday',
      Fri: 'Friday',
      Sat: 'Saturday',
      Sun: 'Sunday',
    };
  
    const payload = {
      course_id: selectedCourseId,
      teacher_id,
      classroom_id,
      students: selectedStudents.map((id) => ({
        student_id: id,
        name: students.find((student: Student) => student.id === id)?.name,
        attendance: [
          {
            present: attendance[id],
            arrival_time: attendance[id].map(() => null), // Заповнюємо `arrival_time` значенням `null`
          },
        ],
      })),
      created_at: new Date().toISOString(),
      day_of_week: fullDayNames[day as keyof typeof fullDayNames] || day,
      start_time: formatTime(start_time),
      finish_time: formatTime(finish_time),
    };
  
    console.log(payload);
    addLessonMutation.mutate(payload, {
      onSuccess: () => {
        navigate('/');
      },
      onError: (error: any) => {
        setAlertMessage(error.message || 'Failed to add lesson.');
      },
    });
  };
  
  if (isCoursesLoading) {
    return <div>Loading courses...</div>;
  }

  if (coursesError) {
    return <div>Error loading courses: {coursesError.message}</div>;
  }

  return (
    <div className="p-6 relative">
      {alertMessage && (
        <StickyAlert message={alertMessage} onClose={() => setAlertMessage(null)} />
      )}

      <h1 className="text-3xl font-bold mb-6 text-[#2596be]">Create Group</h1>
      <div className="space-y-6">
        <div className="bg-gray-100 p-4 rounded shadow">
          <p className="text-lg">
            <strong>Day:</strong> {day}
          </p>
          <p className="text-lg">
            <strong>Start Time:</strong> {start_time}
          </p>
          <p className="text-lg">
            <strong>Finish Time:</strong> {finish_time}
          </p>
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-2 text-[#2596be]">Select Course</h2>
          <CustomDropdown
            options={courses?.map((course: Course) => ({
              id: course.id,
              label: course.name,
            })) || []}
            selectedOption={selectedCourseId}
            onSelect={setSelectedCourseId}
          />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4 text-[#2596be]">Select Students</h2>
          <div className="space-y-4">
            {students?.map((student: Student, index: number) => (
              <div
                key={student.id}
                className={`p-4 rounded shadow flex items-center justify-between transition cursor-pointer ${
                  selectedStudents.includes(student.id)
                    ? 'bg-[#2596be] text-white'
                    : 'bg-gray-100'
                }`}
                onClick={() => toggleStudentSelection(student.id)}
              >
                <span className="font-semibold">
                  {index + 1}. {student.name}
                </span>
              </div>
            ))}
          </div>
        </div>

        {selectedStudents.length > 0 && (
          <div>
            <h2 className="text-2xl font-semibold mb-4 text-[#2596be]">Set Attendance</h2>
            <div className="space-y-6">
              {selectedStudents.map((studentId) => (
                <div
                  key={studentId}
                  className="p-6 rounded shadow bg-gray-50 flex flex-col gap-4"
                >
                  <h3 className="font-bold text-lg text-gray-800">
                    {students.find((student: Student) => student.id === studentId)?.name}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {[...Array(current_week)].map((_, weekIndex) => (
                      <div
                        key={weekIndex}
                        className={`w-12 h-12 flex items-center justify-center rounded-lg cursor-pointer transition ${
                          attendance[studentId][weekIndex] === true
                            ? 'bg-green-500 text-white'
                            : attendance[studentId][weekIndex] === false
                            ? 'bg-red-500 text-white'
                            : 'bg-gray-200 text-gray-700'
                        }`}
                        onClick={() => cycleAttendance(studentId, weekIndex)}
                        title={`Week ${weekIndex + 1}`}
                      >
                        {weekIndex + 1}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-center">
          <button
            onClick={handleSubmit}
            disabled={addLessonMutation.isPending} // Блокуємо кнопку під час завантаження
            className={`px-6 py-3 font-semibold rounded shadow transition ${
              addLessonMutation.isPending
                ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                : 'bg-[#2596be] text-white hover:bg-[#197b9b]'
            }`}
          >
            {addLessonMutation.isPending ? 'Submitting...' : 'Submit'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateGroup;
