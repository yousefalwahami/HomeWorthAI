import { Button } from "@/components/ui/button";
import { CardFooter } from "@/components/ui/card";
import { NavigateFunction, useNavigate } from "react-router-dom";

function HomePage() {
  const navigate: NavigateFunction = useNavigate();

  const handleClick = async () =>{
    navigate('/chat');
  }
  const handleChatlogNav = async () =>{
    navigate('/');
  }

  return (
    <div className="text-white">
      <div className="flex justify-center align-middle">
        <a>test 123</a>
      </div>
      <CardFooter>
        <Button className="w-full" onClick={handleChatlogNav}>Upload chatlog</Button>
        <Button className="w-full" onClick={handleClick}>Chat with RAG</Button>
      </CardFooter>
    </div>
  );
}

export default HomePage;
