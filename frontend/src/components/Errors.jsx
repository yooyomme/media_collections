import React from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';

export const Forbidden = () => {
    const navigate = useNavigate();
    return (
        <div className="error-page-container">
            <h1 className="error-code" style={{ fontSize: '5rem' }}>403 ERROR</h1>
            <h2 className="error-title">Доступ ограничен</h2>
            <p className="error-message">
                У вас недостаточно прав для просмотра этой страницы. Вернитесь на главную или попробуйте авторизоваться.
            </p>
            <button onClick={() => navigate('/')} className="btn-primary">
                Вернуться на главную
            </button>
        </div>
    );
};

export const Unauthorized = () => {
    const navigate = useNavigate();
    const location = useLocation();


    const handleLogin = () => {
        navigate('/login', { state: { from: location.pathname } });
    };

    const handleRegister = () => {
        navigate('/register', { state: { from: location.pathname } });
    };

    return (
        <div className="error-page-container">
            <h1 className="error-code">401 ERROR</h1>
            <h2 className="error-title">Требуется авторизация</h2>
            <p className="error-message">
                Чтобы просматривать этот контент, вам необходимо войти в свой аккаунт или создать новый.
            </p>
            <div className="error-actions">
                <button onClick={handleLogin} className="btn-primary">Войти</button>
                <button onClick={handleRegister} className="btn-secondary">Регистрация</button>
            </div>
        </div>
    );
};

export const NotFound = () => (
    <div className="error-page-container">
        <h1 className="error-code">404 ERROR</h1>
        <h2 className="error-title">Страница не найдена</h2>
        <p className="error-message">
            Похоже, вы зашли в тупик. Страница, которую вы ищете, не существует или была перемещена.
        </p>
        <Link to="/" className="btn-primary">Вернуться на главную</Link>
    </div>
);