import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSharedData } from '@/components/SharedDataProvider';
import ImageComponent from './ImageComponent';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose } from "@/components/ui/dialog";
import { useState, useEffect } from "react";
import axios from "axios";

interface RelatedContentProps {
  title?: string;
  children: React.ReactNode;
  maxHeight?: string;
}

const RelatedContentComponent: React.FC = () => {
  const { chatResponses, imageResponses } = useSharedData();
  const [isOpen, setIsOpen] = useState(false);
  const [chatLog, setChatLog] = useState<string>(""); // State to store the fetched chatlog content
  
  const handleOpenDialog = async (chatId: number) => {
    setIsOpen(true);
  
    try {
      // Fetch data from the endpoint using Axios
      const response = await axios.get(`http://localhost:8000/api/chatlog_from_chatid/${chatId}`);
      console.log('abc:', response);
      if (response.data && Array.isArray(response.data.chatlog)) {
        // If chatlog is an array, set it to the state
        setChatLog(response.data.chatlog.join('\n'));  // Join array into a string if needed
      } else {
        setChatLog("No chatlog available.");
      }
    } catch (error) {
      console.error("Error fetching chatlog:", error);
      setChatLog("Failed to fetch chatlog.");
    }
  };

  const handleCloseDialog = () => {
    setIsOpen(false);
  };

  return (
    <div>
      <Card className="w-full bg-white backdrop-blur-sm border-gray-200/20 max-w-[450px] max-h-[550px] min-h-[550px]">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">{'relatedContent'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-y-auto max-h-[450px] pr-4 hide-scrollbar text-left">
            <h2 className="text-xl text-center font-semibold">Related Chat Responses</h2>
            {chatResponses.map((response, index) => (
              <div
                key={index}
                className="p-4 m-3 bg-green-100 rounded-lg shadow-md hover:-translate-y-2 transition-transform duration-300 cursor-pointer"
                onClick={() => handleOpenDialog(response.chat_id)}
              >
                <p><strong>Context:</strong> {response.context.split(":")[1]}</p>
                <p><strong>Context:</strong> {response.chat_id}</p>
                <p><strong>Item:</strong> {response.item.split(":")[1]}</p>
                <p><strong>Message:</strong> {response.message.split("]")[1]}</p>
              </div>
            ))}

            <h2 className="text-xl text-center font-semibold">Related Image Responses</h2>
            {imageResponses.map((response, index) => (
              <div key={index} className="p-4 m-3 bg-green-100 rounded-lg shadow-md flex items-center">
                <p><strong>Item: </strong> {response.items}</p>
                <p><strong>Filename: </strong> {response.filename}</p>

                <ImageComponent imageId={response.image_id} />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dialog Modal */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Full Chatlog</DialogTitle>
          </DialogHeader>
          <DialogDescription>
            {/* Display fetched chatlog content */}
            <p>{chatLog}</p> {/* This will display the chatlog content inside the dialog */}
          </DialogDescription>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RelatedContentComponent;
