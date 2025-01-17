import React from 'react'
import AttendanceTable from '../components/AttandanceTable'

const Attendance = () => {
  const data = [
    {
      student_id: 1,
      student_name: 'Alice',
      student_surname: 'Marak',
      attendance: [true, true, null, null, null, null, null, null, null, null, null, null,null],
    },
    {
      student_id: 2,
      student_name: 'Bob',
      student_surname: 'Marak',
      attendance: [true, true, false, null, null, null, null, null, null, null, null, null,null],
    },
    {
      student_id: 3,
      student_name: 'Charlie',
      student_surname: 'Marak',
      attendance: [null, null, true, null, null, null, null, null, null, null, null, null,null],
    },
  ];
  return (
    <div className="">
      <AttendanceTable data={data} />
    </div>
  )
}

export default Attendance