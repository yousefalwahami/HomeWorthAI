const Message = ({ person, text }: { person: string, text: string }) => {
    return (
      <>
        <div
          className={`relative w-[90%] h-fit z-20 mb-2 flex flex-col p-4 rounded-3xl ${
            person == "user"
              ? "self-end items-end bg-green-300"
              : "self-start items-start bg-green-200"
          }`}
        >
          {/* Triangle behind the message */}
          <div
            className={`absolute bottom-0 ${
              person === "user" ? "right-0" : "left-0"
            } w-10 h-10 ${
              person === "user" ? "bg-green-300" : "bg-green-200"
            }`}
          ></div>
  
          <p
            className={`font-bold text-md mb-2 w-fit ${
              person == "user"
                ? "text-end text-black"
                : "text-start bg-gradient-to-r from-green-500 via-green-600 to-green-700 text-transparent bg-clip-text"
            }`}
          >
            {person == "user" ? "You" : "Helper"}
          </p>
          <p
            className={`relative text-sm w-full ${
              person == "user" ? "text-end text-black" : "text-start text-green-800"
            }`}
          >
            {text}
          </p>
        </div>
      </>
    );
  };
  
  export default Message;
  