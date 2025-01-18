import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CustomDropdown from "./CustomDropdown";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [scannerState] = useState<"online" | "offline" | "sleep">("online");
  const [selectedRoom, setSelectedRoom] = useState<number | null>(null);

  const rooms = [
    { id: 1, label: "Endor" },
    { id: 2, label: "Meridian" },
    { id: 3, label: "Kronos" },
    { id: 4, label: "Vulcan" },
    { id: 5, label: "Caprica" },
    { id: 6, label: "Abydos" },
    { id: 7, label: "Dune" },
    { id: 8, label: "Mirek" },
    { id: 9, label: "Romulus" },
    { id: 10, label: "Solaris" },
    { id: 11, label: "Hyperion" },
  ];

  const getStateColor = (state: "online" | "offline" | "sleep") => {
    if (state === "online") return "bg-green-500";
    if (state === "offline") return "bg-red-500";
    return "bg-gray-500";
  };

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "auto";
    }
    return () => {
      document.body.style.overflow = "auto";
    };
  }, [isOpen]);

  const handleRunScannerTest = () => {
    const now = new Date();
    const day = now.toLocaleDateString("en-GB", { weekday: "short" }); 
    const startTime = new Date(now.getTime() + 5 * 60 * 1000)
      .toTimeString()
      .slice(0, 5); 
    const finishTime = new Date(now.getTime() + 16 * 60 * 1000) 
      .toTimeString()
      .slice(0, 5);

    const courseId = 404; 

    navigate(
      `/create-group?day=${day}&start_time=${startTime}&finish_time=${finishTime}&course_id=${courseId}`
    );

    onClose(); 
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white p-6 rounded shadow-lg relative max-w-lg w-full"
        onClick={(e) => e.stopPropagation()} 
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Configuration Pico</h2>
          <button
            className="text-gray-500 hover:text-gray-800 text-2xl"
            onClick={onClose}
          >
            &times;
          </button>
        </div>

        <div className="flex items-center justify-between mb-6">
          <span className="text-lg font-semibold mr-3">Status:</span>
          <div className="flex items-center gap-2">
            <div
              className={`w-6 h-6 rounded-full ${getStateColor(scannerState)} mr-2`}
              title={scannerState}
            ></div>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Select Room</h3>
          <CustomDropdown
            options={rooms}
            selectedOption={selectedRoom}
            onSelect={setSelectedRoom}
          />
        </div>

        <button
          onClick={handleRunScannerTest}
          className="w-full py-2 px-4 bg-[#2596be] text-white font-semibold rounded shadow hover:bg-[#197b9b] transition"
        >
          Run Scanner Test
        </button>
      </div>
    </div>
  );
};

export default Modal;
