import React, { useState, useEffect } from 'react';

const ThemeToggle = () => {
    const [isLight, setIsLight] = useState(false);

    const toggleTheme = () => {
        setIsLight(!isLight);
    };

    useEffect(() => {
        if (isLight) {
            document.body.classList.add('light-theme');
        } else {
            document.body.classList.remove('light-theme');
        }
    }, [isLight]);

    return (
        <button onClick={toggleTheme} className="theme-toggle-button">
            {isLight ? 'Темная тема' : 'Светлая тема'}
        </button>
    );
};

export default ThemeToggle;