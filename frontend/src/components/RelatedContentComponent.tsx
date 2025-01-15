import { Card, CardContent } from "@/components/ui/card";
import { useSharedData } from '@/components/SharedDataProvider';
import ImageComponent from './ImageComponent';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import Message from "./Message";
import { LoaderCircle } from "lucide-react";

const RelatedContentComponent: React.FC = () => {
  const { chatResponses, imageResponses } = useSharedData();
  const [isCLOpen, setIsCLOpen] = useState(false);
  const [isIOpen, setIsIOpen] = useState(false);
  const [chatLog, setChatLog] = useState<string>(""); // State to store the fetched chatlog content
  const [imageUrl, setImageUrl] = useState<string>(""); // State to store the fetched chatlog content
  const [showScrollIndicator, setShowScrollIndicator] = useState(false); // State for scroll indicator
  const scrollRef = useRef<HTMLDivElement>(null);

  const handleOpenDialogText = async (chatId: number) => {
    setIsCLOpen(true);

    try {
      // Fetch data from the endpoint using Axios
      const response = await axios.get(`http://localhost:8000/api/chatlog_from_chatid/${chatId}`);
      if (response.data && Array.isArray(response.data.chatlog)) {
        // Map the array to extract messages and join them with line breaks
        const chatMessages = response.data.chatlog.map((entry: { sender: string; message: string; }) => `${entry.sender}: ${entry.message}`);
        setChatLog(chatMessages.join('\n'));
      } else {
        setChatLog("No chatlog available.");
      }
    } catch (error) {
      console.error("Error fetching chatlog:", error);
      setChatLog("Failed to fetch chatlog.");
    }
  };

  const handleOpenDialogImage = async (imageId: number) => {
    setIsIOpen(true);

    try {
      // Include the imageId directly in the URL path
      const response = await axios.get(`http://localhost:8000/api/get_image/${imageId}`, {
        responseType: 'blob', // Set the response type to 'blob' to handle image data
      });
      // Create an object URL for the image data and set it as the src
      const imageBlob = response.data;
      const imageObjectUrl = URL.createObjectURL(imageBlob);
      setImageUrl(imageObjectUrl);
    } catch (error) {
      console.error('Error fetching image:', error);
    }
  };

  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
      // Show indicator if there's more content to scroll
      setShowScrollIndicator(scrollHeight > clientHeight + scrollTop + 10);
    }
  };

  const handleOnOpenChange = () => {
    setIsIOpen(false);
    setImageUrl("");
  }

  useEffect(() => {
    if (scrollRef.current) {
      const { scrollHeight, clientHeight } = scrollRef.current;
      setShowScrollIndicator(scrollHeight > clientHeight);
    }
  }, [chatResponses, imageResponses]);

  return (
    <div>
      <Card className="w-full bg-white backdrop-blur-sm border-gray-200/20 max-w-[450px] max-h-[550px] min-h-[550px] pt-12">
        <CardContent className="">
          <div
            ref={scrollRef}
            onScroll={handleScroll}
            className="overflow-y-auto max-h-[450px] pr-4 hide-scrollbar text-left relative"
          >
            <h2 className="text-xl text-center font-semibold">Related Chat Responses</h2>
            {chatResponses.map((response, index) => (
              <div
                key={index}
                className="p-4 m-3 bg-green-100 rounded-lg shadow-md hover:-translate-y-2 transition-transform duration-300 cursor-pointer"
                onClick={() => handleOpenDialogText(response.chat_id)}
              >
                <p><strong>Context:</strong> {response.context.split(":")[1]}</p>
                <p><strong>Chat ID:</strong> {response.chat_id}</p>
                <p><strong>Item:</strong> {response.item.split(":")[1]}</p>
                <p><strong>Message:</strong> {response.message.split("]")[1]}</p>
              </div>
            ))}

            <h2 className="text-xl text-center font-semibold">Related Image Responses</h2>
            {imageResponses.map((response, index) => (
              <div
                key={index}
                className="p-4 m-3 bg-green-100 rounded-lg shadow-md hover:-translate-y-2 transition-transform duration-300 cursor-pointer flex flex-row justify-between"
                onClick={() => handleOpenDialogImage(response.image_id)}
              >
                <div>
                  <p><strong>Item(s): </strong> {Array.isArray(response.items) ? response.items.join(', ') : ''}</p>
                  <p><strong>Filename: </strong> {response.filename}</p>
                </div>

                <ImageComponent imageId={response.image_id} />
              </div>
            ))}

            {/* Scroll Indicator */}
            {showScrollIndicator && (
              <div className="sticky bottom-0 left-0 w-full flex justify-center pointer-events-none">
                <div className="animate-bounce bg-gray-100 rounded-full p-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                    stroke="currentColor"
                    className="w-6 h-6 text-green-700"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19.5 13.5l-7.5 7.5m0 0l-7.5-7.5m7.5 7.5V3"
                    />
                  </svg>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Dialog modal for chat logs*/}
      <Dialog open={isCLOpen} onOpenChange={setIsCLOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Full Chatlog</DialogTitle>
          </DialogHeader>
          <DialogDescription className="max-h-[60vh] overflow-y-auto hide-scrollbar">
            {chatLog.split('\n').map((message, index) => {
              const [sender, text] = message.split(': ');
              if (!text) return null; // Skip invalid messages
              return (
                <Message 
                  key={index} 
                  person={sender.toLowerCase() === 'user' ? 'You' : sender} 
                  text={text} 
                />
              );
            })}
          </DialogDescription>
        </DialogContent>
      </Dialog>

      {/* Dialog modal for images */}
      <Dialog open={isIOpen} onOpenChange={handleOnOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Bigger picture</DialogTitle>
          </DialogHeader>
          <DialogDescription className="max-h-[60vh] overflow-y-auto hide-scrollbar">
          { 
            imageUrl ? (
              <div>
                <img src={imageUrl} alt="Fetched Image" />
              </div>
            ) : (
              <div>
                <LoaderCircle className="animate-spin" />
              </div>
              
            )
          }
          </DialogDescription>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RelatedContentComponent;
