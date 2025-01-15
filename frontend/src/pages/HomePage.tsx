import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { NavigateFunction, useNavigate } from "react-router-dom";

function HomePage() {
  const navigate: NavigateFunction = useNavigate();

  const handleChatNav = () => {
    navigate('/chat');
  }
  
  const handleChatlogNav = () => {
    navigate('/upload-chat');
  }

  const handleHomeNav = () => {
    navigate('/home');
  }

  return (
    <div className="text-black p-8">
      <h1 className="text-3xl font-semibold text-center bg-gradient-to-r from-green-500 via-green-600 to-green-700 text-transparent bg-clip-text mb-8">
        Welcome to HomeWorthAI
      </h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-1 justify-items-center">
        <Card className="hover:shadow-lg transition-shadow flex flex-col h-[300px] max-w-[300px]">
          <CardHeader>
            <CardTitle>Chat with AI</CardTitle>
            <CardDescription>Start a conversation with our AI assistant</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow">
            <p>Ask questions and get intelligent responses about your property</p>
          </CardContent>
          <CardFooter className="mt-auto">
            <Button className="w-full py-3 text-black rounded-lg hover:bg-green-400 bg-green-600" onClick={handleChatNav}>Start Chat</Button>
          </CardFooter>
        </Card>

        <Card className="hover:shadow-lg transition-shadow flex flex-col h-[300px] max-w-[300px]">
          <CardHeader>
            <CardTitle>Upload Chatlog</CardTitle>
            <CardDescription>Share your conversation history</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow">
            <p>Upload and analyze your previous chat conversations</p>
          </CardContent>
          <CardFooter className="mt-auto">
            <Button className="w-full py-3 text-black rounded-lg hover:bg-green-400 bg-green-600" onClick={handleChatlogNav}>Upload Now</Button>
          </CardFooter>
        </Card>

        <Card className="hover:shadow-lg transition-shadow flex flex-col h-[300px] max-w-[300px]">
          <CardHeader>
            <CardTitle>Dashboard</CardTitle>
            <CardDescription>View your property insights</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow">
            <p>Access detailed analytics and property information</p>
          </CardContent>
          <CardFooter className="mt-auto">
            <Button className="w-full py-3 text-black rounded-lg hover:bg-green-400 bg-green-600" onClick={handleHomeNav}>View Dashboard</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

export default HomePage;
