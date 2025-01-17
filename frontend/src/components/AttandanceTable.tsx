import React, { useState } from 'react';

interface AttendanceRecord {
  present: boolean | null;
  arrival_time: string | null;
}

interface StudentAttendance {
  student_id: number;
  student_name: string;
  attendance: AttendanceRecord[];
}

interface AttendanceTableProps {
  data: StudentAttendance[];
}

const AttendanceTable: React.FC<AttendanceTableProps> = ({ data }) => {
  const weeks = Array.from({ length: 13 }, (_, i) => i + 1);
  const [selected, setSelected] = useState<{
    student_id: number;
    student_name: string;
    week: number;
  } | null>(null);

  const [attendanceData, setAttendanceData] = useState(data);

  const updateAttendance = (
    student_id: number,
    week: number,
    newStatus: boolean | null
  ) => {
    setAttendanceData((prevData) =>
      prevData.map((student) =>
        student.student_id === student_id
          ? {
              ...student,
              attendance: student.attendance.map((record, index) =>
                index === week ? { ...record, present: newStatus } : record
              ),
            }
          : student
      )
    );
    setSelected(null);
    console.log(
      `Updated attendance for Student ID: ${student_id}, Week: ${
        week + 1
      }, New Status: ${newStatus}`
    );
  };

  return (
    <div className="relative">
      <table className="table-auto border-collapse border border-gray-300 w-full text-gray-800">
        <thead>
          <tr>
            <th className="border border-gray-300 p-4 bg-gray-100 text-gray-800">
              Student
            </th>
            {weeks.map((week) => (
              <th
                key={week}
                className="border border-gray-300 p-4 bg-gray-100 text-gray-800 text-center"
              >
                Week {week}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {attendanceData.map((student) => (
            <tr key={student.student_id}>
              <td className="border border-gray-300 p-4 text-gray-800">
                {student.student_name}
              </td>
              {student.attendance.map((record, index) => (
                <td
                  key={index}
                  className="border border-gray-300 p-4 text-center"
                  title={
                    record.arrival_time
                      ? `Arrival time: ${new Date(record.arrival_time).toLocaleString()}`
                      : 'No arrival time'
                  }
                >
                  <div
                    className={`w-10 h-10 mx-auto rounded cursor-pointer transform transition-transform duration-200 ${
                      record.present === true
                        ? 'bg-green-500'
                        : record.present === false
                        ? 'bg-red-500'
                        : 'bg-gray-300'
                    } hover:scale-110`}
                    onClick={() =>
                      setSelected({
                        student_id: student.student_id,
                        student_name: student.student_name,
                        week: index,
                      })
                    }
                  ></div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {selected && (
        <div
          className="fixed inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center z-50"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-white p-8 rounded shadow-lg text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-xl font-bold mb-4 text-gray-800">
              Update Attendance
            </h2>
            <p className="mb-4 text-gray-600">
              {selected.student_name} - Week {selected.week + 1}
            </p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() =>
                  updateAttendance(selected.student_id, selected.week, true)
                }
                className="w-16 h-16 bg-green-500 hover:bg-green-600 rounded transform transition-transform duration-200 hover:scale-110"
              ></button>
              <button
                onClick={() =>
                  updateAttendance(selected.student_id, selected.week, false)
                }
                className="w-16 h-16 bg-red-500 hover:bg-red-600 rounded transform transition-transform duration-200 hover:scale-110"
              ></button>
              <button
                onClick={() =>
                  updateAttendance(selected.student_id, selected.week, null)
                }
                className="w-16 h-16 bg-gray-300 hover:bg-gray-400 rounded transform transition-transform duration-200 hover:scale-110"
              ></button>
            </div>
            <button
              onClick={() => setSelected(null)}
              className="mt-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AttendanceTable;
