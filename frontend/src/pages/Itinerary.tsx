import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import axios from '@/lib/axios';
import { LoaderCircle } from 'lucide-react';

const ItineraryPage: React.FC = () => {
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const user_id = Number(localStorage.getItem("user_id"));
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

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
      // Make API GET request to /generate_report
      const response = await axios.get('/api/generate_report', {
        params: { user_id }, // Pass user_id as query parameter
        responseType: 'blob' // Expecting a PDF file
      });

      // Create a blob URL for the PDF
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      setPdfUrl(url);

      // Optional: Automatically download the PDF after generation
      const link = document.createElement('a');
      link.href = url;
      link.download = `${title.replace(/\s+/g, '_')}_report.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
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

            <Button
              onClick={handleGeneratePDF}
              disabled={loading || !title}
              className="w-full bg-green-600 text-white hover:bg-green-700"
            >
              {loading ? (
                <>
                  <LoaderCircle className="animate-spin" /> Generating...
                </>
              ) : (
                'Generate PDF'
              )}
            </Button>
          </CardContent>
        </Card>

        {pdfUrl && (
          <Card>
            <CardHeader>
              <CardTitle>Download Your PDF</CardTitle>
            </CardHeader>
            <CardContent>
              <a
                href={pdfUrl}
                download={`${title.replace(/\s+/g, '_')}_report.pdf`}
                className="block"
              >
                <Button className="w-full bg-green-600 text-white hover:bg-green-700">
                  Download PDF
                </Button>
              </a>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ItineraryPage;
