import React, { useState } from 'react';
import GroupItem from '../../components/Group/GroupItem';
import EmptyGroupItem from '../../components/Group/EmptyGroupItem';
import Modal from '../../components/Modal'; 
import { LogOut } from 'lucide-react'; 
import { useLessons, useLessonsByStudent } from '../../hooks/useApi';
import { useAuth } from '../../providers/AuthProvider';

const time = ['7:30', '9:10', '10:50', '13:30', '15:10'];
const finished_time = ['9:00', '10:40', '12:20', '15:00', '16:40']; // Додано масив finished_time

const week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const fullDayNames = {
  Mon: 'Monday',
  Tue: 'Tuesday',
  Wed: 'Wednesday',
  Thu: 'Thursday',
  Fri: 'Friday',
  Sat: 'Saturday',
  Sun: 'Sunday',
  Monday: 'Monday',
  Tuesday: 'Tuesday',
  Wednesday: 'Wednesday',
  Thursday: 'Thursday',
  Friday: 'Friday',
  Saturday: 'Saturday',
  Sunday: 'Sunday',
};

const normalizeDay = (day: string): string => {
  return fullDayNames[day as keyof typeof fullDayNames] || day;
};

const formatTime = (timeStr: string) => {
  const [hours, minutes] = timeStr.split(':');
  return `${parseInt(hours)}:${minutes}`;
};

const GroupsForStudent = () => {
  const courseId = '1';
  const teacherId = useAuth().userId || '-1';
  const { data, isLoading, error } = useLessonsByStudent(teacherId);
  const { logout, email } = useAuth(); 
  console.log(email);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {(error as Error).message}</p>;

  const lessons: Record<string, any> = data?.lessons || {};

  let idCounter = 1;

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="mb-6 text-center relative">
        <h1 className="text-4xl font-bold text-[#2596be] mb-2">SmartAttendance - Student</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          This project is powered by <strong>Raspberry Pi Pico</strong>, serving as an advanced scanner for <strong>ISIC</strong> cards. 
          It helps teachers track student attendance during lessons in real-time, while students can view their attendance records.
          Stay organized and ensure attendance accuracy!
        </p>
        
        <div className="absolute top-0 right-0 flex flex-col gap-4">
          <button
            className="bg-[#f44336] text-white p-2 rounded shadow hover:bg-[#d32f2f] transition"
            onClick={logout} 
            title="Log Out"
          >
            <LogOut size={24} />
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-2 bg-white rounded shadow pb-2">
        <div
          className="grid gap-x-4"
          style={{ gridTemplateColumns: `100px repeat(${time.length}, 1fr)` }}
        >
          <div></div>
          {time.map((t, index) => (
            <div
              key={index}
              className="text-center font-bold text-gray-800 border-b"
            >
              {t}
            </div>
          ))}
        </div>

        {week_days.map((day, rowIndex) => (
          <div
            key={rowIndex}
            className="grid gap-x-4 mr-3"
            style={{ gridTemplateColumns: `100px repeat(${time.length}, 1fr)` }}
          >
            <div className="text-center font-bold text-gray-800 border-r flex items-center justify-center ">
              {day}
            </div>

            {time.map((t, colIndex) => {
              const lessonEntry = Object.entries(lessons || {}).find(
                ([id, l]: [string, any]) =>
                  normalizeDay(l.day_of_week) === normalizeDay(day) &&
                  formatTime(l.start_time) === t
              );

              const id = lessonEntry ? parseInt(lessonEntry[0]) : null;
              const lesson = lessonEntry ? lessonEntry[1] : null;
              const finishTime = finished_time[colIndex]; // Тепер використовуємо finished_time з масиву

              return lesson ? (
                <GroupItem
                  key={`${rowIndex}-${colIndex}`}
                  id={id}
                  group={{
                    start_time: lesson.start_time,
                    finish_time: finishTime, // Використовуємо finished_time
                    short_course_name: lesson.short_course_name,
                  }}
                />
              ) : (
                <EmptyGroupItem
                  key={`${rowIndex}-${colIndex}`}
                  day={day}
                  start_time={time[colIndex]}
                  finish_time={finishTime} // Використовуємо finishTime з масиву finished_time
                  course_id={parseInt(courseId!)}
                />
              );
            })}
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-gray-100 rounded shadow">
        <h2 className="text-lg font-semibold text-gray-800 mb-2">Legend:</h2>
        <ul className="list-disc list-inside text-gray-600">
          <li>
            <span className="text-green-500 font-bold">Green</span>: Scheduled lessons
          </li>
          <li>
            <span className="text-gray-400 font-bold">Gray</span>: Free time slots
          </li>
        </ul>
      </div>
    </div>
  );
};

export default GroupsForStudent;
