import React, { useState, useContext } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { authApi } from '../api';
import { useAuth } from './AuthContext';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const from = location.state?.from || "/";

    const { login } = useAuth();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Вызываем ОДНУ функцию из контекста
            await login(email, password);

            // Если не вылетела ошибка, значит всё успешно
            navigate(from, { replace: true });
        } catch (error) {
            // Ошибка может прийти и от логина, и от getMe
            const message = error.response?.data?.detail || 'Ошибка входа';
            alert(typeof message === 'object' ? JSON.stringify(message) : message);
        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>С возвращением</h2>
                <form className="auth-form" onSubmit={handleLogin}>
                    <div className="input-group">
                        <label>Email</label>
                        <input
                            type="email"
                            placeholder="example@mail.com"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div className="input-group">
                        <label>Пароль</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button type="submit" className="auth-button" disabled={loading}>
                        {loading ? 'Вход...' : 'Войти'}
                    </button>
                </form>
                <div className="auth-footer">
                    Нет аккаунта? <Link to="/register">Создать профиль</Link>
                </div>
            </div>
        </div>
    );
};

export default Login;