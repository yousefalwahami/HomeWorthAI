import { Button } from "./ui/button";
import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuIndicator,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger,
    NavigationMenuViewport,
    navigationMenuTriggerStyle
  } from "./ui/navigation-menu";

import { Link, NavigateFunction, useLocation } from "react-router-dom";
import { useAppSelector } from "@/redux/store";
import { User } from "@/redux/features/userSlice";
import { useLogout, LogoutHook } from "@/hooks/useLogout";
import { useNavigate } from "react-router-dom";

export default function Navbar(): JSX.Element{
    const user: User | null = useAppSelector<User | null>(state=>state.user.user);
    const {logout}: LogoutHook = useLogout();
    const navigate: NavigateFunction = useNavigate();
    const location = useLocation();

    function handleClick(e: React.SyntheticEvent<HTMLButtonElement>): void {
        e.preventDefault();
        logout();
        navigate('/');
    }

    const hideNavbarRoutes = ['/chat', '/upload-chat', '/home'];
    console.log(location.pathname)
    const shouldShowNavbar = hideNavbarRoutes.includes(location.pathname);

    return(
        <div>
            <nav className='w-full flex flex-row justify-between items-center px-10 py-6 font-Montserrat'>
                <Link to="/" className="flex flex-row items-center">
                    <p className="text-2xl font-bold leading-10 text-center bg-gradient-to-r from-green-500 to-green-700 to-black text-transparent bg-clip-text">
                        HomeWorthAI
                    </p>
                    <img src='/logo-cropped.svg' className="pl-2 h-5 mb-1"/>
                </Link>
                
                <div className="flex flex-row items-center">
                    <NavigationMenu className="flex">
                        {shouldShowNavbar && <NavigationMenuList>
                            <NavigationMenuItem >
                            <NavigationMenuTrigger className="bg-gray-100">Options</NavigationMenuTrigger>
                            <NavigationMenuContent>
                                <Link to="/home" >
                                    <NavigationMenuLink className={navigationMenuTriggerStyle()}>Home</NavigationMenuLink>
                                </Link>
                                <Link to="/upload-chat" >
                                    <NavigationMenuLink className={navigationMenuTriggerStyle()}>Upload chats</NavigationMenuLink>
                                </Link>
                                <Link to="/chat" >
                                    <NavigationMenuLink className={navigationMenuTriggerStyle()}>Chat with bot</NavigationMenuLink>
                                </Link>
                            </NavigationMenuContent>
                            </NavigationMenuItem>
                        </NavigationMenuList>}
                    </NavigationMenu>
                    { user ? (<Button onClick={handleClick} variant = "ghost" className="text-lg h-[40px] hidden md:flex ">Log Out</Button>) : (<><Link to='/login'><Button variant = "ghost" className="text-lg h-[40px] hidden md:flex ">Log In</Button></Link><Link to="/signup"><Button variant = "outline" className="dark:text-white text-md mx-5 rounded-md h-[40px] hover:opacity-90 md:w-[84px] hidden md:flex">Sign up</Button></Link></>)}
                </div>
            </nav>
        </div>
    )
};

//                    