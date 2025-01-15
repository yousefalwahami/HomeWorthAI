const Message = ({ person, text }: { person: string, text: string }) => {
    return (
      <>
        <div
          className={`relative w-[90%] h-fit z-20 mb-2 flex flex-col p-4 rounded-3xl ${
            person == "user"
              ? "self-end items-end bg-green-300"
              : person === "bot" 
                ? "self-start items-start bg-green-200"
                : "relative w-[100%] items-start bg-green-300"
          }`}
        >
          {/* Triangle behind the message */}
          <div
            className={`absolute bottom-0 ${
              person === "user" ? "right-0" : "left-0"
            } w-10 h-10 ${
              person === "user" ? "bg-green-300" : person === "bot" ? "bg-green-200" : "bg-transparent"
            }`}
            // {person === "user" ? "You" : person === "bot" ? "Helper" : person}
          ></div>
  
          <p
            className={`font-bold text-md mb-2 w-fit ${
              person == "user"
                ? "text-end text-black"
                : person === "bot" ?
                  "text-start bg-gradient-to-r from-green-500 via-green-600 to-green-700 text-transparent bg-clip-text"
                  : "text-start text-black"
            }`}
          >
            {person === "user" ? "You" : person === "bot" ? "Helper" : person}
          </p>
          <p
            className={`relative text-sm w-full ${
              person == "user" ? "text-end text-black" 
              : person === "bot" ?
                  "text-start text-green-800"
                  : "text-start text-black"
            }`}
          >
            {text}
          </p>
        </div>
      </>
    );
  };
  
  export default Message;
  