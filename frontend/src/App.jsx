import React, { createContext, useState, useEffect, useContext } from 'react';
import { BrowserRouter, Routes, Route, useParams } from 'react-router-dom';
import Collection from './components/Collection';
import Home from './components/Home';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import { AuthProvider } from './components/AuthContext';
import { Forbidden, Unauthorized, NotFound } from './components/Errors'
import './components/styles.css';


function App() {
    const [isLightTheme, setIsLightTheme] = useState(false);
    const toggleTheme = () => setIsLightTheme(!isLightTheme);

    return (
        <AuthProvider>
            <BrowserRouter>
                <div className={isLightTheme ? 'light-mode' : 'dark-mode'} style={{ minHeight: '100vh' }}>
                    <Navbar isLightTheme={isLightTheme} toggleTheme={toggleTheme} />
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/collections/:id" element={<Collection />} />
                        <Route path="/profile" element={<Profile />} />
                        <Route path="/401" element={<Unauthorized />} />
                        <Route path="/403" element={<Forbidden />} />

                        <Route path="*" element={<NotFound />} />
                    </Routes>
                </div>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;