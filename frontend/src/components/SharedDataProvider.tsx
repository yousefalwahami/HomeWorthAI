import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ChatResponse {
  chat_id: number;
  context: string;
  item: string;
  message: string;
  message_id: number;
  type: string;
  user_id: number;
}

interface ImageResponse {
  image_id: number;
  items: string;
  type: string;
  user_id: number;
}

interface SharedDataContextProps {
  relatedContent: string | null;
  chatResponses: ChatResponse[];
  imageResponses: ImageResponse[];
  setRelatedContent: (content: string) => void;
  setChatResponses: (responses: ChatResponse[]) => void;
  setImageResponses: (responses: ImageResponse[]) => void;
}

const SharedDataContext = createContext<SharedDataContextProps | undefined>(undefined);

export const SharedDataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [relatedContent, setRelatedContent] = useState<string | null>(null);
  const [chatResponses, setChatResponses] = useState<ChatResponse[]>([]);
  const [imageResponses, setImageResponses] = useState<ImageResponse[]>([]);


  return (
    <SharedDataContext.Provider
      value={{
        relatedContent,
        chatResponses,
        imageResponses,
        setRelatedContent,
        setChatResponses,
        setImageResponses,
      }}
    >
      {children}
    </SharedDataContext.Provider>
  );

};

export const useSharedData = () => {
  const context = useContext(SharedDataContext);
  if (!context) {
    throw new Error('useSharedData must be used within a SharedDataProvider');
  }
  return context;
};
