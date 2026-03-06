import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authApi } from '../api';

const Register = () => {
    const navigate = useNavigate();

    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        username: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await authApi.register(
                formData.email,
                formData.password,
                formData.username
            );
            navigate('/login');
        } catch (error) {
            console.error("Ошибка регистрации", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Регистрация</h2>
                <form className="auth-form" onSubmit={handleSubmit}>
                    <div className="input-group">
                        <label>Email *</label>
                        <input
                            type="email"
                            placeholder="email@example.com"
                            required
                            onChange={(e) => setFormData({...formData, email: e.target.value})}
                        />
                    </div>
                    <div className="input-group">
                        <label>Имя пользователя</label>
                        <input
                            type="text"
                            placeholder="Ваш никнейм"
                            onChange={(e) => setFormData({...formData, username: e.target.value})}
                        />
                    </div>
                    <div className="input-group">
                        <label>Пароль *</label>
                        <input
                            type="password"
                            placeholder="Минимум 8 символов"
                            required
                            onChange={(e) => setFormData({...formData, password: e.target.value})}
                        />
                    </div>
                    <button type="submit" className="auth-button" disabled={loading}>
                        {loading ? 'Создание...' : 'Зарегистрироваться'}
                    </button>
                </form>
                <div className="auth-footer">
                    Уже есть аккаунт? <Link to="/login">Войти</Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
