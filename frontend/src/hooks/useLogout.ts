import { useAppDispatch } from "@/redux/store";
import { removeUser } from "@/redux/features/userSlice";
import api from "@/lib/axios";

export type LogoutHook = {
    logout: () => void
}

export const useLogout = (): LogoutHook =>{
    const dispatch = useAppDispatch();

    const logout = async () =>{
        try{
            await api.post('/api/user/logout');
            dispatch(removeUser());
        } catch(error){
            console.error('Logout failed', error);
        }
        
    }

    return {logout};
}
