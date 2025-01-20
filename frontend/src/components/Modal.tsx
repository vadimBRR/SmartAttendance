import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CustomDropdown from "./CustomDropdown";
import { useClassrooms, usePicoState, useChangeClassroom, useCurrentClassroom, useIsTest } from "../hooks/useApi";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const Modal = ({ isOpen, onClose }: ModalProps) => {
  const navigate = useNavigate();
  const {
    data: scannerState,
    isLoading: isPicoLoading,
    error: picoError,
  } = usePicoState();
  const { data: classrooms, isLoading, error } = useClassrooms();
  const { mutate: changeClassroom } = useChangeClassroom(); 
  const { data: isTest, isLoading: isTestLoading, error: testError } = useIsTest();
  
  const { data: currentClassroom, isLoading: isCurrentClassLoading } = useCurrentClassroom();

  const [selectedRoom, setSelectedRoom] = useState<number | null>(null); 
  const [isApplyVisible, setIsApplyVisible] = useState(false);

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

  useEffect(() => {
    if (currentClassroom) {
      setSelectedRoom(Number(currentClassroom.id)); 
    }
  }, [currentClassroom]);

  useEffect(() => {
    if (selectedRoom && selectedRoom !== Number(currentClassroom?.id)) {
      setIsApplyVisible(true);
    } else {
      setIsApplyVisible(false);
    }
  }, [selectedRoom, currentClassroom]);

  const handleRunScannerTest = () => {
    if (selectedRoom) {
      changeClassroom(selectedRoom.toString());
    }

    const now = new Date();
    const day = now.toLocaleDateString("en-GB", { weekday: "short" });
    const startTime = new Date(now.getTime() + 5 * 60 * 1000).toTimeString().slice(0, 5);
    const finishTime = new Date(now.getTime() + 16 * 60 * 1000).toTimeString().slice(0, 5);

    const courseId = 404;

    navigate(
      `/create-group?day=${day}&start_time=${startTime}&finish_time=${finishTime}&course_id=${courseId}&is_test=true`
    );

    onClose();
  };

  const handleApplyChanges = () => {
    if (selectedRoom) {
      changeClassroom(selectedRoom.toString()); // Застосовуємо зміни класу
      setIsApplyVisible(false); // Приховуємо кнопку після застосування
    }
  };

  const handleGoToTest = () => {
    navigate('/attendance_test');
    onClose();
  };

  if (isLoading || isPicoLoading || isCurrentClassLoading || isTestLoading) return <p>Loading...</p>;
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
              className={`w-6 h-6 rounded-full ${getStateColor(scannerState?.status || "offline")} mr-2`}
              title={scannerState ? scannerState.status : "offline"}
            ></div>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Select Room</h3>
          <CustomDropdown
            options={classrooms?.map((room) => ({
              id: room.id,
              label: room.label,
            }))}
            selectedOption={selectedRoom}
            onSelect={setSelectedRoom}
          />
        </div>

        {isApplyVisible && (
          <button
            onClick={handleApplyChanges}
            className="w-full py-2 px-4 bg-yellow-500 text-white font-semibold rounded shadow hover:bg-yellow-600 transition mb-4"
          >
            Apply
          </button>
        )}

        {/* {
          !isTest ? (
            <button
          onClick={handleRunScannerTest}
          className="w-full py-2 px-4 bg-[#2596be] text-white font-semibold rounded shadow hover:bg-[#197b9b] transition"
        >
          Run Scanner Test
        </button>
          ) : (
            <button
          onClick={handleGoToTest}
          className="w-full py-2 px-4 bg-[#2596be] text-white font-semibold rounded shadow hover:bg-[#197b9b] transition"
        >
          Go to Test
        </button>
          )
        } */}
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
