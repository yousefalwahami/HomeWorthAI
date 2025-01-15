import React, { useState } from "react";
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose } from "@/components/ui/dialog";

const DialogModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const handleOpenDialog = () => {
    setIsOpen(true);
  };

  const handleCloseDialog = () => {
    setIsOpen(false);
  };

  return (
    <div>
      {/* Trigger Button */}
      <button onClick={handleOpenDialog} className="px-4 py-2 bg-blue-500 text-white rounded">
        Open Dialog
      </button>

      {/* Dialog Component */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Dialog Title</DialogTitle>
            <DialogDescription>
              This is a sample dialog. You can add more content here.
            </DialogDescription>
          </DialogHeader>
          <div>
            <p>Some content inside the dialog...</p>
          </div>
          <DialogClose asChild>
            <button onClick={handleCloseDialog} className="mt-4 px-4 py-2 bg-gray-500 text-white rounded">
              Close
            </button>
          </DialogClose>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DialogModal;
