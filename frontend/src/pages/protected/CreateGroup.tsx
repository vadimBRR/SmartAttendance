import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import CustomDropdown from '../../components/CustomDropdown';
import StickyAlert from '../../components/StickyAlert';

const CreateGroup: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const day = searchParams.get('day') || '';
  const start_time = searchParams.get('start_time') || '';
  const finish_time = searchParams.get('finish_time') || '';
  const course_id = searchParams.get('course_id') || '';

  const courses = [
    { id: 1, label: 'Internet vecí a chytré zariadenia' },
    { id: 2, label: 'Programovanie' },
  ];

  const students = [
    { id: 1231231, name: 'Vadym Brovych' },
    { id: 1231341, name: 'Valeriia Buhaiova' },
    { id: 1231243, name: 'Oleh Klymenko' },
    { id: 1231346, name: 'Svitlana Hrytsenko' },
  ];

  const current_week = 5;

  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [selectedStudents, setSelectedStudents] = useState<number[]>(
    students.map((student) => student.id)
  );
  const [attendance, setAttendance] = useState<Record<number, (boolean | null)[]>>(
    students.reduce((acc, student) => {
      acc[student.id] = Array(current_week).fill(true);
      return acc;
    }, {} as Record<number, (boolean | null)[]>)
  );

  const [alertMessage, setAlertMessage] = useState<string | null>(null);

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

    const payload = {
      course_id: selectedCourseId,
      students: selectedStudents.map((id) => ({
        student_id: id,
        name: students.find((student) => student.id === id)?.name,
        attendance: attendance[id],
      })),
      created_at: new Date().toISOString(),
      day_of_week: day,
      start_time,
      finish_time,
    };

    console.log('Submit Payload:', payload);
    navigate('/');
  };

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
            options={courses}
            selectedOption={selectedCourseId}
            onSelect={setSelectedCourseId}
          />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4 text-[#2596be]">Select Students</h2>
          <div className="space-y-4">
            {students.map((student, index) => (
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
                    {students.find((student) => student.id === studentId)?.name}
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
            className="px-6 py-3 bg-[#2596be] text-white font-semibold rounded shadow hover:bg-[#197b9b] transition"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateGroup;
