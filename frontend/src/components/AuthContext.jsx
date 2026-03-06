import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi, setAuthHeader } from '../api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [accessToken, setAccessToken] = useState(null);
    const [loading, setLoading] = useState(true);

    const refreshSession = useCallback(async () => {
        try {
            const response = await authApi.refresh();
            const { access_token } = response.data;

            setAccessToken(access_token);
            setAuthHeader(access_token);

            const userRes = await authApi.getMe();
            setUser(userRes.data);

            return access_token;
        } catch (error) {
            setAccessToken(null);
            setUser(null);
            setAuthHeader(null);
            return null;
        }
    }, []);

    useEffect(() => {
        const init = async () => {
            setLoading(true);
            await refreshSession();
            setLoading(false);
        };
        init();
    }, [refreshSession]);


   const login = async (email, password) => {
       const response = await authApi.login(email, password);
       const { access_token } = response.data;

       setAccessToken(access_token);
       setAuthHeader(access_token);

       try {
           const userRes = await authApi.getMe();
           setUser(userRes.data);
           return true;
       } catch (error) {
           console.error("Ошибка при получении данных профиля", error);
           logout();
           throw error;
           }
       };

       const logout = async () => {
           try {
               await authApi.logout();
           } finally {
               setUser(null);
               setAccessToken(null);
               setAuthHeader(null);
           }
       };

   return (
       <AuthContext.Provider value={{
           user,
           setUser,
           accessToken,
           login,
           logout,
           loading,
           refreshSession
       }}>
   {!loading && children}
       </AuthContext.Provider>
   );
};

export const useAuth = () => useContext(AuthContext);
