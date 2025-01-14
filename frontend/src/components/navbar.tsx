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

import { Link, NavigateFunction } from "react-router-dom";
import { useAppSelector } from "@/redux/store";
import { User } from "@/redux/features/userSlice";
import { useLogout, LogoutHook } from "@/hooks/useLogout";
import { useNavigate } from "react-router-dom";

export default function Navbar(): JSX.Element{
    const user: User | null = useAppSelector<User | null>(state=>state.user.user);
    const {logout}: LogoutHook = useLogout();
    const navigate: NavigateFunction = useNavigate();

    function handleClick(e: React.SyntheticEvent<HTMLButtonElement>): void {
        e.preventDefault();
        logout();
        navigate('/');
    }

    return(
        <div>
            <nav className='w-full flex flex-row justify-between items-center px-10 py-6 font-Montserrat'>
                <Link to="/" className="flex flex-row items-center">
                    <p className="text-2xl font-bold leading-10">
                        HomeWorthAI
                    </p>
                </Link>
                
                <div className="flex flex-row items-center">
                    <NavigationMenu className="lg:hidden flex">
                        <NavigationMenuList>
                            <NavigationMenuItem>
                            <NavigationMenuTrigger>Details</NavigationMenuTrigger>
                            <NavigationMenuContent className="">
                                <Link to="/login" >
                                    <NavigationMenuLink className={navigationMenuTriggerStyle()}>Deets</NavigationMenuLink>
                                </Link>
                                <Link to="/login" >
                                    <NavigationMenuLink className={navigationMenuTriggerStyle()}>something else</NavigationMenuLink>
                                </Link>
                            </NavigationMenuContent>
                            </NavigationMenuItem>
                        </NavigationMenuList>
                    </NavigationMenu>
                    { user ? (<Button onClick={handleClick} variant = "ghost" className="text-lg h-[40px] hidden md:flex ">Log Out</Button>) : (<><Link to='/login'><Button variant = "ghost" className="text-lg h-[40px] hidden md:flex ">Log In</Button></Link><Link to="/signup"><Button variant = "outline" className="dark:text-white text-md mx-5 rounded-md h-[40px] hover:opacity-90 md:w-[84px] hidden md:flex">Sign up</Button></Link></>)}
                </div>
            </nav>
        </div>
    )
};

//                    