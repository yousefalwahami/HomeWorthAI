import { Button } from "@/components/ui/button";
import { AlertDestructive } from "@/components/ui/AlertDestructive";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
  } from "@/components/ui/card"
import { Input } from "@/components/ui/input";
import { Label } from "@radix-ui/react-label";
import axios, { AxiosError, AxiosResponse } from "axios";
import { useState } from "react";
import { NavigateFunction, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "@/redux/store";
import {addUser} from '@/redux/features/userSlice';
import api from "@/lib/axios";
  
type formData = {
    email: string,
    password: string,
    passwordConfirm: string
}

type responseData = {
    email: string
}

type ErrorResponse = {
    error: string | null;
  };
  
function SignUp(): JSX.Element {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [passwordConfirm , setPasswordConfirm] = useState("");
    const [error, setError] = useState<string | null>(null);
    const navigate: NavigateFunction = useNavigate();
    const dispatch = useAppDispatch();
    const user = useAppSelector(state => state.user.user);

    if(user){
        navigate('/home');
    }

    const handleClick = async () =>{
        try{
            const formInput:formData = {email: email, password: password, passwordConfirm: passwordConfirm};

            const response: AxiosResponse = await api.post('/api/user/register', formInput);
            const dataFromAPI: responseData = response.data;
            
            dispatch(addUser({email: dataFromAPI.email, token: ''}));// no need to store the token in redux
            setEmail('');
            setPassword('');
            setError(null);
            navigate('/home');
        } catch(err: unknown){
            if(axios.isAxiosError(err)){
                const newError = err as AxiosError<ErrorResponse>;
                setError(newError.response?.data?.error ?? 'Unknown error');
            }else{
                console.log("idk");
            }
        }
    }
    
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) =>{
        if(e.key == 'Enter'){
            handleClick();
        }
    }

    //basically shadcn will give us the base of the component
    //then we have to add all the stuff we want on top
    return (
        <div className='flex flex-col items-center justify-center h-[calc(90vh-90px)] w-full'>
            <Card className="w-[400px]">
            <CardHeader>
                <CardTitle>Sign up</CardTitle>
                <CardDescription>This is a basic signup page</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="grid w-full gap-4">
                    <div className="flex flex-col items-start space-y-2">
                        <Label htmlFor="email" >
                            Email
                        </Label>
                        <Input id="email" onChange={e => setEmail(e.target.value)} onKeyDown={handleKeyDown} type="email" placeholder="m@example.com" value={email}/>
                    </div>
                    <div className="flex flex-col items-start space-y-2">
                        <Label htmlFor="password" >
                            Password
                        </Label>
                        <Input id="password" onChange={e => setPassword(e.target.value)} onKeyDown={handleKeyDown} type="password" value={password}/>
                    </div>
                    <div className="flex flex-col items-start space-y-2">
                        <Label htmlFor="password" >
                            Verify Password
                        </Label>
                        <Input id="passwordConfirm" onChange={e => setPasswordConfirm(e.target.value)} onKeyDown={handleKeyDown} type="password" value={passwordConfirm}/>
                    </div>
                </div>
                
            </CardContent>
            <CardFooter>
                <Button onClick={handleClick} className="w-full" value={[email, password, passwordConfirm]}>Create account</Button> 
            </CardFooter>
        </Card>
        {error && <AlertDestructive error={error}/>}
    </div>
    )
}

export default SignUp;
