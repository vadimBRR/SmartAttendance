import React from "react";
import GroupItem from "../../components/Group/GroupItem";
import EmptyGroupItem from "../../components/Group/EmptyGroupItem"; // Додано EmptyGroupItem
import { useLessons } from "../../hooks/useApi";
import { useParams } from "react-router-dom";

const time = ["7:30", "9:10", "10:50", "13:30", "15:10"];
const week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

// Функція для форматування часу
const formatTime = (timeStr: string) => {
  const [hours, minutes] = timeStr.split(":");
  return `${parseInt(hours)}:${minutes}`; // Видаляємо нулі попереду
};

const Groups = () => {
  const { id: courseId } = useParams<{ id: string }>(); // Отримуємо `courseId` з URL
  const teacherId = 1; // Змініть на динамічний ID, якщо потрібно
  const { data: lessons, isLoading, error } = useLessons(parseInt(courseId!), teacherId);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {(error as Error).message}</p>;

  let idCounter = 1; // Лічильник для унікальних ID

  return (
    <div className="flex flex-col gap-2 bg-white mr-2 rounded shadow">
      <div
        className="grid gap-x-4" // Додано горизонтальний розрив
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
          className="grid gap-x-4" // Додано горизонтальний розрив
          style={{ gridTemplateColumns: `100px repeat(${time.length}, 1fr)` }}
        >
          <div className="text-center font-bold text-gray-800 border-r flex items-center justify-center">
            {day}
          </div>

          {time.map((t, colIndex) => {
            const lesson = Object.values(lessons || {}).find(
              (l: any) =>
                l.day_of_week === day && formatTime(l.start_time) === t // Порівнюємо відформатований час
            );

            // Якщо знайдено урок, присвоюємо унікальний ID
            const id = lesson ? idCounter++ : null;

            return lesson ? (
              <GroupItem
                key={`${rowIndex}-${colIndex}`}
                id={id}
                group={lesson}
              />
            ) : (
              <EmptyGroupItem
                key={`${rowIndex}-${colIndex}`}
                day={day}
                time={t}
              />
            );
          })}
        </div>
      ))}
    </div>
  );
};

export default Groups;
