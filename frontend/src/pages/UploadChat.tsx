import React, { useState, useRef } from 'react';
import api from '@/lib/axios';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";

const UploadChatPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [serverResponse, setServerResponse] = useState<any>(null);
  const user_id = Number(localStorage.getItem("user_id"));
  const [isDragging, setIsDragging] = useState(false);
  const [isChatOrImage, setIsChatOrImage] = useState(false); // false = chat, true = image
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
    formData.append("type", isChatOrImage ? "image" : "chat");

    try {
      const endpoint = isChatOrImage
        ? '/api/detect_objects'
        : '/api/process_chatlog';

      const response = await api.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setUploadMessage("File uploaded successfully!");
      setServerResponse(response.data);
      console.log(response.data);
    } catch (error: any) {
      console.error("Error uploading file:", error);
      const errorMessage = error.response?.data?.detail || "Failed to upload file. Please try again.";
      setUploadMessage(errorMessage);
    }
  };

  const handleToggleUploadType = () => {
    setIsChatOrImage((prev) => !prev);
    setServerResponse(null); // Clear response data when switching modes
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="w-full max-w-3xl p-4">
        <h1 className="text-3xl font-semibold text-center text-teal-600 mb-8">
          {isChatOrImage ? "Upload Image" : "Upload Chat"}
        </h1>

        <div
          className={`flex flex-col items-center justify-center w-full h-40 border-2 ${
            isDragging ? "border-teal-600 bg-teal-50" : "border-gray-300"
          } border-dashed rounded-md p-4`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <p className="text-gray-600 mb-2">Drag & drop your file here or click to select.</p>
          <Input
            type="file"
            accept={isChatOrImage ? ".jpg,.jpeg,.png" : ".txt,.json"}
            onChange={handleFileChange}
            className="hidden"
            ref={fileInputRef}
          />
          <Button variant="outline" onClick={triggerFileInput}>
            Browse File
          </Button>
        </div>

        {selectedFile && (
          <p className="mt-4 text-gray-700">
            Selected File: <strong>{selectedFile.name}</strong>
          </p>
        )}

        <div className="flex items-center mt-4">
          <Button
            onClick={handleUpload}
            className="bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700 transition"
          >
            Upload File
          </Button>
          <div className="flex items-center ml-4">
            <Checkbox
              id="toggleUpload"
              onClick={handleToggleUploadType}
            />
            <label htmlFor="toggleUpload" className="ml-2 text-gray-700">
              {isChatOrImage ? "Switch to Chat" : "Switch to Image"}
            </label>
          </div>
        </div>

        {uploadMessage && (
          <p className={`mt-4 text-center text-sm ${uploadMessage.includes("successfully") ? "text-green-600" : "text-red-600"}`}>
            {uploadMessage}
          </p>
        )}

        {serverResponse && (
          <div className="mt-6 bg-gray-50 p-6 rounded shadow">
            <h2 className="text-2xl font-bold mb-6 text-teal-600">Response:</h2>

            {isChatOrImage ? (
              <>
                <div className="mt-4 bg-white p-4 rounded shadow">
                  <h3 className="text-xl font-bold mb-2">Detected Items in Image:</h3>
                  {serverResponse?.detections?.[0]?.metadata?.items?.map((item: string, index: number) => (
                    <div key={index} className="p-2 border rounded mb-2">
                      {item}
                    </div>
                  )) || <div>No items detected.</div>}
                </div>
                <div className="mt-4 bg-white p-4 rounded shadow">
                  <h3 className="text-xl font-bold mb-2">Image Metadata:</h3>
                  <p><strong>Filename:</strong> {serverResponse?.detections?.[0]?.metadata?.filename || "N/A"}</p>
                  <p><strong>Image ID:</strong> {serverResponse?.detections?.[0]?.metadata?.image_id || "N/A"}</p>
                </div>
              </>
            ) : (
              <>
                <div className="mt-4 bg-white p-4 rounded shadow">
                  <h3 className="text-xl font-bold mb-2">Items Found:</h3>
                  {serverResponse?.items?.map((item: string, index: number) => (
                    <div key={index} className="p-2 border rounded mb-2">
                      {item}
                    </div>
                  )) || <div>No items found.</div>}
                </div>
                <div className="mt-4 bg-white p-4 rounded shadow">
                  <h3 className="text-xl font-bold mb-2">Context:</h3>
                  {serverResponse?.context?.map((context: string, index: number) => (
                    <div key={index} className="p-2 border rounded mb-2">
                      {context}
                    </div>
                  )) || <div>No context provided.</div>}
                </div>
                <div className="mt-4 bg-white p-4 rounded shadow">
                  <h3 className="text-xl font-bold mb-2">Messages:</h3>
                  {serverResponse?.messages?.map((message: string, index: number) => (
                    <div key={index} className="p-2 border rounded mb-2">
                      {message}
                    </div>
                  )) || <div>No messages available.</div>}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadChatPage;