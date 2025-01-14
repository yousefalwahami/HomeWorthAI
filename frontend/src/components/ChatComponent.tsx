import React, { useState, ChangeEvent, FormEvent, useEffect } from 'react';
import axios from 'axios';
import { Button } from "./ui/button";
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

interface ChatComponentProps {
  user_id: number;
}

const ChatComponent: React.FC<ChatComponentProps> = ({ user_id }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [searchChat, setSearchChat] = useState(false);
  const [searchImage, setSearchImages] = useState(false);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInputText(e.target.value);
  };

  const handleCheckboxChange = (setState: React.Dispatch<React.SetStateAction<boolean>>) => {
    setState((prevState) => !prevState);
  };

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();

    if (!inputText) {
      alert('Please enter a message.');
      return;
    }

    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'user', text: inputText },
    ]);

    const payload = {
      prompt: inputText,
      user_id,
      messages,
      searchChat,
      searchImage,
    };

    setInputText('');

    try {
      const response = await axios.post('http://localhost:8000/api/nebius-chat', payload, {
        headers: { 'Content-Type': 'application/json' },
      });

      const botMessage: Message = {
        sender: 'bot',
        text: response.data.response.choices[0].message.content || 'No response from bot.',
      };

      setMessages((prevMessages) => [...prevMessages, botMessage]);
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
      <div className="space-y-4 mb-6 max-h-[500px] overflow-y-scroll hide-scrollbar">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg text-black flex items-center ${
              message.sender === 'user' ? 'bg-teal-500 text-right flex-row-reverse' : 'bg-gray-300 text-left flex-row'
            }`}
          >
            <img
              src={message.sender === 'user' ? '/assets/user.png' : '/assets/sender.png'}
              alt="Avatar"
              className="w-8 h-8 rounded-full mr-2"
            />
            <p>{message.text}</p>
          </div>
        ))}
      </div>

      <form onSubmit={sendMessage} className="space-y-4">
        <Input
          type="text"
          value={inputText}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="w-full p-4 rounded-lg border border-gray-300"
        />

        <div className="w-full flex flex-row justify-start gap-8">
          <Button type="submit" className="py-3 bg-black text-white rounded-lg hover:bg-gray-800">
            Send
          </Button>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="imageSearch"
              onClick={(e) => handleCheckboxChange(setSearchImages)}
            />
            <label htmlFor="imageSearch" className="text-sm font-medium">
              AI Image Search
            </label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="chatSearch"
              onClick={(e) => handleCheckboxChange(setSearchChat)}
            />
            <label htmlFor="chatSearch" className="text-sm font-medium">
              AI Chat Log Search
            </label>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ChatComponent;
