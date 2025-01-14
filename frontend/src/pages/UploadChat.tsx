import React, { useState } from 'react';
import api from '@/lib/axios'; // Import your Axios instance if you need to upload to the backend

const ChatPage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [serverResponse, setServerResponse] = useState<string | null>(null); // State for server response
  const user_id = 1; // You can pass the user_id dynamically, for now, it's a fixed value

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage("No file selected. Please choose a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("user_id", user_id.toString());  // Assuming user_id is a number
    console.log('help: ', formData);

    /*
    const payload = {
      file: selectedFile,
      user_id: user_id,
    };
    */

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
        
        <div className="flex flex-col items-center">
          <input
            type="file"
            accept=".txt,.json" // Adjust accepted file types as needed
            onChange={handleFileChange}
            className="mb-4"
          />
          <button
            onClick={handleUpload}
            className="bg-teal-600 text-white px-4 py-2 rounded hover:bg-teal-700 transition"
          >
            Upload File
          </button>
          {uploadMessage && (
            <p className="mt-4 text-center text-sm text-gray-700">{uploadMessage}</p>
          )}
        </div>
        {serverResponse}
      </div>
    </div>
  );
};

export default ChatPage;
