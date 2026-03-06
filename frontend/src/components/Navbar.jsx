import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';
import { useAuth } from './AuthContext';
import { pictureBaseUrl } from '../api';

const Navbar = () => {
    const { user, logout } = useAuth();

    const getAvatarSrc = (url) => {
        if (!url) return null;
        if (url.startsWith('blob:')) return url;
        if (url.startsWith('http')) return url;
        return `${pictureBaseUrl}${url}`;
    };


    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="link-without-line">
                    <div className="logo">Media Collections</div>
                </Link>

                <div className="nav-menu">
                    <ThemeToggle />

                    {user ? (
                        <div className="user-profile">
                            <Link to="/profile" className="login-link">{user.username ? user.username : "Аноним"}</Link>
                            <Link to="/profile" className="link-without-line">
                              {user.avatar_url ? (
                                <img src={getAvatarSrc(user.avatar_url)} alt="Avatar" className="avatar" />
                              ) : (
                                <div className="avatar">
                                    {user.username ? user.username[0].toUpperCase() : user.email[0].toUpperCase()}
                                </div>
                              )}
                            </Link>

                            <button onClick={logout} className="btn-create">Выйти</button>
                        </div>
                    ) : (
                        <nav style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                            <Link to="/login" className="login-link">Войти</Link>
                            <Link to="/register" className="btn-create" style={{padding: '8px 15px'}}>Регистрация</Link>
                        </nav>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;