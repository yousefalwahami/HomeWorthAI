import React, { useState, useRef } from 'react';
import api from '@/lib/axios'; // Import your Axios instance if you need to upload to the backend
import { Button } from "@/components/ui/button"; // Replace with your actual button component
import { Input } from "@/components/ui/input"; // Replace with your input component


const UploadChatPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [serverResponse, setServerResponse] = useState<string | null>(null); // State for server response
  const user_id = Number(localStorage.getItem("user_id"));
  const [isDragging, setIsDragging] = useState(false); // Track drag-and-drop state
  const fileInputRef = useRef<HTMLInputElement>(null);

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      setSelectedFile(event.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage("No file selected. Please choose a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("user_id", user_id.toString());
    console.log('help: ', formData);


    try {
      const response = await api.post('/api/process_chatlog', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadMessage("File uploaded successfully!");
      setServerResponse(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadMessage("Failed to upload file. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="w-full max-w-3xl p-4">
        <h1 className="text-3xl font-semibold text-center text-teal-600 mb-8">
          Upload chat fam
        </h1>

        <div
          className={`flex flex-col items-center justify-center w-full h-40 border-2 ${
            isDragging ? "border-teal-600 bg-teal-50" : "border-gray-300"
          } border-dashed rounded-md p-4`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <p className="text-gray-600 mb-2">
            Drag & drop your file here or click to select.
          </p>
          <Input
            type="file"
            accept=".txt,.json" // Adjust accepted file types as needed
            onChange={handleFileChange}
            className="hidden" // Hide the default input
          />
          <Button
            variant="outline"
            onClick={() => {
              const fileInput = document.querySelector("input[type='file']") as HTMLInputElement;
              fileInput?.click();
            }}
          >
            Browse File
          </Button>
        </div>

        {selectedFile && (
          <p className="mt-4 text-gray-700">
            Selected File: <strong>{selectedFile.name}</strong>
          </p>
        )}

        <Button
          onClick={handleUpload}
          className="mt-4 bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700 transition"
        >
          Upload File
        </Button>

        {uploadMessage && (
          <p className="mt-4 text-center text-sm text-gray-700">{uploadMessage}</p>
        )}

        {serverResponse && (
          <pre className="mt-4 bg-gray-200 p-4 rounded text-sm">
            {serverResponse}
          </pre>
        )}
      </div>
    </div>
  );
};

export default UploadChatPage;
