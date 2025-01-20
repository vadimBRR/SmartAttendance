import React, { useState } from 'react';

interface AttendanceTrackerProps {
  weeks: number;
  currentAttendance: Set<number>;
  onToggle: (week: number) => void;
}

const AttendanceTracker = ({
  weeks,
  currentAttendance,
  onToggle,
}: AttendanceTrackerProps) => {
  return (
    <div className="flex gap-2">
      {[...Array(weeks)].map((_, weekIndex) => (
        <div
          key={weekIndex}
          className={`w-10 h-10 flex items-center justify-center rounded-full cursor-pointer transition ${
            currentAttendance.has(weekIndex)
              ? 'bg-[#2596be] text-white shadow'
              : 'bg-gray-200 text-gray-700'
          }`}
          onClick={() => onToggle(weekIndex)}
          title={`Week ${weekIndex + 1}`}
        >
          {weekIndex + 1}
        </div>
      ))}
    </div>
  );
};

export default AttendanceTracker;
