import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type User = {
    email: string,
    token: string
}

type UserState = {
    user: User | null
}

const initialState:UserState = {
    user: null
};

export const UserSlice = createSlice({
    name: "user",
    initialState,
    reducers: {
        addUser: (state, action: PayloadAction<{email: string, token: string}>) =>{
            state.user = action.payload;
        },
        removeUser: (state)=>{
            state.user = null;
        }
    }
})

export default UserSlice.reducer;
export const {addUser, removeUser} = UserSlice.actions;