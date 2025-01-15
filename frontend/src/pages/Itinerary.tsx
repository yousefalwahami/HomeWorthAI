import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import axios from '@/lib/axios';
import { LoaderCircle } from 'lucide-react';

interface Message {
  sender: string;
  text: string;
  timestamp?: string;
}

const ItineraryPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [images, setImages] = useState<string[]>([]);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value);
  };

  const handleGeneratePDF = async () => {
    if (!title) {
      alert('Please enter a title for your itinerary');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('/api/generate-itinerary', {
        title,
        messages,
        images
      }, {
        responseType: 'blob'
      });

      // Create a blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${title.replace(/\s+/g, '_')}_itinerary.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error generating PDF:', error);
      // alert('Failed to generate PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-90px)] bg-gray-100 p-8">
      <h1 className="text-3xl font-semibold text-center bg-gradient-to-r from-green-500 via-green-600 to-green-700 text-transparent bg-clip-text mb-8">
        Generate Itinerary
      </h1>

      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Create PDF Itinerary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="title" className="text-sm font-medium">
                Itinerary Title
              </label>
              <Input
                id="title"
                placeholder="Enter itinerary title..."
                value={title}
                onChange={handleTitleChange}
              />
            </div>

            {messages.length > 0 && (
              <div className="space-y-2">
                <h3 className="font-medium">Preview:</h3>
                <div className="max-h-60 overflow-y-auto border rounded-md p-4">
                  {messages.map((msg, index) => (
                    <div key={index} className="mb-2">
                      <span className="font-bold">{msg.sender}: </span>
                      <span>{msg.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <Button
              onClick={handleGeneratePDF}
              disabled={loading || !title}
              className="w-full bg-green-600 text-white hover:bg-green-700"
            >
              {loading ? <> <LoaderCircle className="animate-spin" /> Generating... </> : 'Generate PDF'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ItineraryPage;
