import React from 'react';
import { LogOut, Monitor } from 'lucide-react';
import { useAuth } from '../../providers/AuthProvider';

const GroupsForUnknown = () => {
  const { logout } = useAuth();

  return (
    <div className="p-6 bg-gray-50 min-h-screen flex flex-col justify-center items-center relative">
      <div className="absolute top-0 right-0 flex flex-col gap-4">
        <button
          className="bg-[#f44336] text-white p-2 rounded shadow hover:bg-[#d32f2f] transition"
          onClick={logout} 
          title="Log Out"
        >
          <LogOut size={24} />
        </button>
        
      </div>

      <div className="text-center mb-6">
        <h1 className="text-4xl font-bold text-[#2596be] mb-4">SmartAttendance</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          This project is powered by <strong>Raspberry Pi Pico</strong>, serving as an advanced scanner for <strong>ISIC</strong> cards. 
          It helps teachers track student attendance during lessons in real-time, while students can view their attendance records. 
          Stay organized and ensure attendance accuracy!
        </p>
      </div>

      <div className="bg-red-100 text-red-800 p-4 rounded shadow-md max-w-lg text-center">
        <p className="text-lg">
          Unfortunately, we couldn't find your email in our database. <br />
          Please ensure you are using the correct email, or contact the administrator for assistance.
        </p>
      </div>
    </div>
  );
};

export default GroupsForUnknown;
