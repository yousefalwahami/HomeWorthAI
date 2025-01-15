import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LoaderCircle } from 'lucide-react';

interface ImageComponentProps {
  imageId: number;
}

const ImageComponent: React.FC<ImageComponentProps> = ({ imageId }) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  useEffect(() => {
    const fetchImage = async () => {
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

    fetchImage();
  }, [imageId]);

  return imageUrl ? (
    <div>
      <img src={imageUrl} alt="Fetched Image" className="w-20 h-20 object-cover" />
    </div>
  ) : (
    <div>
      <LoaderCircle className="animate-spin" />
    </div>
    
  );
};

export default ImageComponent;
