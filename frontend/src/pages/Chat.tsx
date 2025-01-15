import React from 'react';
import ChatComponent from '@/components/ChatComponent';
import RelatedContentComponent from '@/components/RelatedContentComponent';
import { SharedDataProvider } from '@/components/SharedDataProvider';

const ChatPage: React.FC = () => {
  const user_id = Number(localStorage.getItem("user_id"));

  return (
    <SharedDataProvider>
      <div className="min-h-[calc(100vh-90px)] bg-gray-100 flex items-center justify-center">
        <div className="w-full max-w-3xl p-4">
          <h1 className="text-3xl font-semibold text-center bg-gradient-to-r from-green-500 via-green-600 to-green-700 text-transparent bg-clip-text mb-8">
            Related Content
          </h1>

          <RelatedContentComponent />
        </div>
        <div className="w-full max-w-3xl p-4">
          <h1 className="text-3xl font-semibold text-center bg-gradient-to-r from-green-500 via-green-600 to-green-700 text-transparent bg-clip-text mb-8">
            Talk about what you last remember..
          </h1>

          <ChatComponent user_id={user_id} />
        </div>
      </div>
    </SharedDataProvider>
  );
};

export default ChatPage;
