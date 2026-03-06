import React, { useRef, useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { collectionApi, authApi } from '../api';
import { useAuth } from './AuthContext';
import { useScroll } from './useScroll';
import ThemeToggle from './ThemeToggle';

const Home = () => {
    const scrollRef = useRef(null);
    const [isDown, setIsDown] = useState(false);
    const [startX, setStartX] = useState(0);
    const [scrollLeft, setScrollLeft] = useState(0);

    // заглушка для вида сайта с пустой базой данных
    // после реализации публичных коллекций и лайков заменить популярными за неделю/месяц коллекциями
    const lists = [
        { id: 1, title: "Топ хорроров 2025", likes: 120, items: 15 },
        { id: 2, title: "Ламповое аниме", likes: 450, items: 42 },
        { id: 3, title: "Классика HBO", likes: 89, items: 10 },
        { id: 4, title: "Сериалы на выходные", likes: 230, items: 8 },
        { id: 5, title: "Киберпанк подборка", likes: 600, items: 25 },
    ];


    const navigate = useNavigate();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const location = useLocation();

    const collectionsScroll = useScroll();

    const { user, logout } = useAuth();

    const handleCreateClick = () => {
        setIsModalOpen(true);
    };

    const confirmCreation = async () => {
        setLoading(true);
        try {
            const response = await collectionApi.createCollection({
                title: "Коллекция",
                is_public: false,
                description: "",
                media_items_id: [],
                user_id: user.id
            });

            const newCollectionId = response.data.id;
            setIsModalOpen(false);
            navigate(`/collections/${newCollectionId}`);
        } catch (error) {
            console.error("Ошибка при создании коллекции:", error);
            alert("Не удалось создать коллекцию. Попробуйте позже.");
        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="home-container">
            <section className="feed-section">
                <header className="home-hero">
                    <div className="hero-content">
                        <h1>Что посмотреть этим вечером?</h1>
                        <p>Создавайте совместные коллекции и голосуйте за интересное, исследуйте популярные подборки и делитесь своими.</p>
                        <button className="btn-create-main" onClick={handleCreateClick} disabled={loading}>
                            <span className="plus-icon">+</span> Создать коллекцию
                        </button>
                    </div>
                </header>

                {isModalOpen && (
                    <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
                        <div className="modal-content" onClick={e => e.stopPropagation()}>
                            {user ? (
                                <div className="auth-confirmed">
                                    <h2>Создать новую коллекцию?</h2>
                                    <div className="modal-actions">
                                        <button className="btn-confirm" onClick={confirmCreation}>Да, создать</button>
                                        <button className="btn-cancel" onClick={() => setIsModalOpen(false)}>Отмена</button>
                                    </div>
                                </div>
                            ) : (
                                <div className="auth-required">
                                    <h2>Нужна авторизация</h2>
                                    <p>Войдите в аккаунт, чтобы создавать свои списки и делиться ими с друзьями!</p>
                                    <div className="modal-actions">
                                        <Link to="/login" className="btn-confirm">Войти</Link>
                                        <Link to="/register" className="btn-secondary">Создать аккаунт</Link>
                                    </div>
                                </div>
                            )}
                            <button className="modal-close-x" onClick={() => setIsModalOpen(false)}>×</button>
                        </div>
                    </div>
                )}


                <h2>Популярные коллекции</h2>
                <div
                    className="horizontal-scroll"
                    ref={collectionsScroll.ref}
                        {...collectionsScroll.events}
                >
                    {lists.map(list => (
                        <div key={list.id} className="list-card">
                            <div className="card-image"></div>
                            <div className="card-content">
                                <h3>{list.title}</h3>
                                <div className="card-footer">
                                    <span>♡ {list.likes}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default Home;
