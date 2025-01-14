import React, { useState, ChangeEvent, FormEvent } from 'react';
import axios from 'axios';
import { Button } from "./ui/button";
import { Input } from './ui/input';
import { InputFile } from './ui/FileInput';

// Define types for message data
interface Message {
  sender: 'user' | 'bot';
  text: string;
}

interface ChatComponentProps {
  userId: number;
}

const ChatComponent: React.FC<ChatComponentProps> = ({ userId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);

  // Handle text input change
  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputText(e.target.value);
  };

  // Handle file input change
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const uploadedFile = e.target.files ? e.target.files[0] : null;
    if (uploadedFile) setFile(uploadedFile);
  };

  // Send a message and interact with the backend API
  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();  // Prevent form submission

    if (!inputText && !file) {
      alert('Please enter a message or upload a file.');
      return;
    }

    // Add user message to the chat
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'user', text: inputText || `File: ${file?.name}` },
    ]);

    /*
    // Prepare form data for sending
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (inputText) {
      formData.append('text', inputText);
    }
    formData.append('user_id', String(userId));
    */

    // Prepare the data for sending as JSON
    const payload = {
      user_id: userId,
      text: inputText || null,
      // Handle file sending if needed (for example, you can send a file URL or base64)
      file: file ? file.name : null,
    };

    // TODO: its not working fam .. im tried its 2am
    try {
      // Send the request to the backend API
      const response = await axios.post(
        'http://localhost:8000/api/nebius-chat',
        // formData,
        payload,
        {
          headers: { 'Content-Type': 'application/json' },
        }
      );

      // Add bot's response to the chat
      const botMessage: Message = {
        sender: 'bot',
        text: response.data.message || 'No response from bot.',
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]);

      // Clear the input
      setInputText('');
      setFile(null);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'bot', text: 'Error processing chat log.' },
      ]);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      {/* Display chat messages */}
      <div className="space-y-4 mb-6">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg text-white flex items-center ${
              message.sender === 'user' ? 'bg-teal-500 text-right flex-row-reverse' : 'bg-gray-300 text-left flex-row'
            }`}
          >
            {/* Image */}
            <img
              src={message.sender === 'user' ? '/assets/user.png' : '/assets/sender.png'}
              alt="Avatar"
              className="w-8 h-8 rounded-full mr-2" // Adjust image size and margin
            />
            {/* Message */}
            <p>{message.text}</p>
          </div>
        ))}
      </div>


      {/* Input and file upload form */}
      <form onSubmit={sendMessage} className="space-y-4">
        {/* Text input */}
        <Input
          type="text"
          value={inputText}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="w-full p-4 rounded-lg border border-gray-300"
        />

        {/* File input
        <InputFile
          onChange={handleFileChange}
          accept=".txt,.json,.pdf,.docx,.csv"
          className="w-full p-4 rounded-lg border border-gray-300"
        /> 
        */}

        {/* Send Button */}
        <Button
          type="submit"
          className="w-full py-3 bg-black text-white rounded-lg hover:bg-gray-800"
        >
          Send
        </Button>
      </form>
    </div>
  );
};

export default ChatComponent;
