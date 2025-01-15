import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSharedData } from '@/components/SharedDataProvider';
import ImageComponent from './ImageComponent';  // Import ImageComponent

interface RelatedContentProps {
  title?: string;
  children: React.ReactNode;
  maxHeight?: string;
}

const RelatedContentComponent: React.FC = () => {
  const { chatResponses, imageResponses } = useSharedData();
  console.log(imageResponses);

  return (
    <Card className="w-full bg-white/10 backdrop-blur-sm border-gray-200/20">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{'relatedContent'}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-y-auto max-h-[500px] pr-4 hide-scrollbar">
          <h2 className="text-xl font-semibold">Related Chat Responses</h2>
          {chatResponses.map((response, index) => (
            <div key={index} className="p-4 bg-gray-100 rounded-lg shadow-md">
              <p><strong>Context:</strong> {response.context}</p>
              <p><strong>Item:</strong> {response.item}</p>
              <p><strong>Message:</strong> {response.message}</p>
            </div>
          ))}

          <h2 className="text-xl font-semibold">Related Image Responses</h2>
          {imageResponses.map((response, index) => (
            <div key={index} className="p-4 bg-gray-100 rounded-lg shadow-md flex items-center">
              <p><strong>Item: </strong> {response.items}</p>

              <ImageComponent imageId={response.image_id} />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default RelatedContentComponent;
