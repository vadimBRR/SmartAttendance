import React from 'react';

interface AttendanceRecord {
  present: boolean | null;
  arrival_time: string | null;
}

interface AttendanceTableProps {
  data: AttendanceRecord[]; // Дані про відвідуваність одного студента
  lessonId: number;
  addAttendance: (args: {
    lessonId: number;
    weekNumber: number;
    studentId: number;
    present: boolean | null;
  }) => void;
  weekNumber: number; // Поточний тиждень
}

const AttendanceTableStudent = ({
  data,
  lessonId,
  addAttendance,
  weekNumber,
}: AttendanceTableProps) => {
  const weeks = Array.from({ length: 13 }, (_, i) => i + 1);

  const toggleAttendance = (week: number, currentStatus: boolean | null) => {
    // Наступний статус у циклі: true -> false -> null -> true
    const newStatus =
      currentStatus === true ? false : currentStatus === false ? null : true;

    addAttendance({
      lessonId,
      weekNumber: week,
      studentId: 1, // Фіксований ID студента (оскільки один студент)
      present: newStatus,
    });
  };

  return (
    <div className="relative">
      <table className="table-auto border-collapse border border-gray-300 w-full text-gray-800">
        <thead>
          <tr>
            <th className="border border-gray-300 p-4 bg-gray-100 text-gray-800 text-center">
              Week
            </th>
            <th className="border border-gray-300 p-4 bg-gray-100 text-gray-800 text-center">
              Attendance
            </th>
          </tr>
        </thead>
        <tbody>
          {weeks.map((week) => (
            <tr key={week}>
              <td className="border border-gray-300 p-4 text-center text-xl">{week}</td>
              <td
                className="border border-gray-300 p-4 text-center"
                title={
                  data[week - 1]?.arrival_time
                    ? `Arrival time: ${new Date(
                        data[week - 1].arrival_time!
                      ).toLocaleString()}`
                    : 'No arrival time'
                }
              >
                <div
                  className={`w-10 h-10 mx-auto rounded cursor-pointer transform transition-transform duration-200 ${
                    data[week - 1]?.present === true
                      ? 'bg-green-500'
                      : data[week - 1]?.present === false
                      ? 'bg-red-500'
                      : 'bg-gray-300'
                  } hover:scale-110`}
                  onClick={() =>
                    toggleAttendance(week, data[week - 1]?.present || null)
                  }
                ></div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AttendanceTableStudent;
