import React, { useState } from "react";
import Modal from "./Modal"; // Використовуємо Modal компонент
import CustomDropdown from "./CustomDropdown"; // Кастомний випадаючий список

const ScannerModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState(true); // Для тесту зробіть true
  const [scannerState, setScannerState] = useState<"online" | "offline" | "sleep">("online");
  const [selectedRoom, setSelectedRoom] = useState<number | null>(null);

  const rooms = [
    { id: 1, label: "Endor (18)" },
    { id: 2, label: "Meridian (20)" },
    { id: 3, label: "Romulus (22)" },
    { id: 4, label: "Hyperion (30)" },
  ];

  const getStateColor = (state: "online" | "offline" | "sleep") => {
    if (state === "online") return "bg-green-500";
    if (state === "offline") return "bg-red-500";
    return "bg-gray-500";
  };

  return (
    <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
      <div>
        {/* Стан сканера */}
        <div className="flex items-center mb-4">
          <span className="text-lg font-semibold mr-3">Scanner Status:</span>
          <div
            className={`w-4 h-4 rounded-full ${getStateColor(scannerState)} mr-2`}
            title={scannerState}
          ></div>
          <span className="capitalize">{scannerState}</span>
        </div>

        {/* Вибір кабінету */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">Select Room</h2>
          <CustomDropdown
            options={rooms}
            selectedOption={selectedRoom}
            onSelect={setSelectedRoom}
          />
        </div>
      </div>
    </Modal>
  );
};

export default ScannerModal;
