import React, { useRef, useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { collectionApi, authApi, pictureBaseUrl } from '../api';
import { useAuth } from './AuthContext';
import { useScroll } from './useScroll';

const Profile = () => {
    const { user, logout, setUser } = useAuth();
    const [editData, setEditData] = useState({ username: '', email: '', avatar_url: ''});
    const [previewUrl, setPreviewUrl] = useState(user.avatar_url || null);
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);
    const [shouldDeleteAvatar, setShouldDeleteAvatar] = useState(false);

    const [collections, setCollections] = useState([]);
    const [membershipCollections, setMembershipCollections] = useState([]);

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const myCollectionsScroll = useScroll();
    const memberCollectionsScroll = useScroll();

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const [userRes, collRes, membershipCollRes] = await Promise.all([
                authApi.getUserById(user.id),
                authApi.getUserCollections(user.id),
                authApi.getUserMemberCollections(user.id)
            ]);
            setEditData({ username: userRes.data.username, email: userRes.data.email, avatar_url: userRes.data.avatar_url });
            if (userRes.data.avatar_url) {
                setPreviewUrl(userRes.data.avatar_url);
            }
            setUser(userRes.data);
            setCollections(collRes.data);
            setMembershipCollections(membershipCollRes.data);
        } catch (error) {
            console.error("Ошибка загрузки профиля", error);
        } finally {
            setLoading(false);
        }
    };

    const getAvatarSrc = (url) => {
        if (!url) return null;
        if (url.startsWith('blob:')) return url;
        if (url.startsWith('http')) return url;
        return `${pictureBaseUrl}${url}`;
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            let updatedUser = user;
            if (editData.username !== user.username || editData.email !== user.email) {
                const textResponse = await authApi.updateUser(user.id, {
                    username: editData.username,
                    email: editData.email
                });
                updatedUser = textResponse.data;
            }
            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                const avatarResponse = await authApi.uploadAvatar(user.id, formData);
                updatedUser = avatarResponse.data;
            }
            else if (shouldDeleteAvatar && user.avatar_url) {
                const deleteResponse = await authApi.deleteAvatar(user.id);
                updatedUser = deleteResponse.data;
                window.location.reload();
            }
            setUser(updatedUser);
            setEditData({
                username: updatedUser.username,
                email: updatedUser.email,
                avatar_url: updatedUser.avatar_url
            });
            setPreviewUrl(updatedUser.avatar_url);
            setSelectedFile(null);
            setShouldDeleteAvatar(false);
            setIsModalOpen(false);
        } catch (error) {
            console.error("Ошибка при сохранении:", error.response?.data || error.message);
            alert("Ошибка: " + (error.response?.data?.detail || "Не удалось сохранить данные"));
        }
    };

    const removeAvatar = () => {
        setPreviewUrl(null);
        setSelectedFile(null);
        setShouldDeleteAvatar(true);
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
            setShouldDeleteAvatar(false);
        }
    };

    const handleDeleteAccount = async () => {
        if (window.confirm("Вы уверены, что хотите удалить аккаунт? Это действие необратимо.")) {
            try {
                await authApi.deleteUser(user.id);
                window.location.href = '/login';
            } catch (error) {
                console.error("Ошибка при удалении", error);
            }
        }
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

    if (loading) return <div className="error-page-container"><div className="error-title">Загрузка...</div></div>;
    if (!user) return <div className="error-page-container"><div className="error-title">Пользователь не найден</div></div>;

    return (
        <div className="profile-container">
            <header className="profile-header">
                <div className="profile-info-main">
                    <div className="profile-avatar">
                        {previewUrl ? (
                            <img src={getAvatarSrc(previewUrl)} alt="Preview" className="avatar-img" />
                        ) : (
                            <span>{user.username ? user.username[0].toUpperCase() : user.email[0].toUpperCase()}</span>
                        )}
                    </div>
                    <div className="profile-text">
                        <h1>{user.username ? user.username : "Аноним"}</h1>
                        <p>{user.email}</p>
                    </div>
                </div>

                <div className="profile-actions">
                    <button className="btn-settings" onClick={() => setIsModalOpen(true)}>
                        ⚙️ Настройки
                    </button>
                    <button className="btn-delete" onClick={handleDeleteAccount}>
                        Удалить аккаунт
                    </button>
                </div>
            </header>

            <section className="feed-section">
                <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2>Мои коллекции</h2>
                    {collections.length > 0 && (
                        <button className="btn-create-small" onClick={confirmCreation}>
                            + Создать
                        </button>
                    )}
                </div>
                {collections.length > 0 ? (
                    <div
                        className="horizontal-scroll"
                        ref={myCollectionsScroll.ref}
                        {...myCollectionsScroll.events}
                    >
                        {collections.map(list => (
                            <div key={list.id} className="list-card">
                                <div className="card-image">
                                {list.cover_image && (
                                    <img src={getAvatarSrc(list.cover_image)} alt="Preview" className="avatar-img" />
                                )}
                                </div>
                                <div className="card-content">
                                    <Link to={`/collections/${list.id}`} className="link-without-line">
                                        <h3>{list.title}</h3>
                                    </Link>
                                    <div className="card-footer">
                                        <span className="items-count">♡ {list.likes || 0}   🎞 {list.item_associations?.length || 0}</span>
                                        {list.is_public ?
                                            <div className="private-badge" title="Публичная">
                                                <span>🌐</span>
                                                </div>
                                            :
                                            <div className="private-badge" title="Приватная">
                                                <span>🔒</span>
                                            </div>
                                        }
                                    </div>


                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="empty-collections-placeholder">
                        <div className="placeholder-icon">📂</div>
                        <p className="secondary-text">У вас пока нет ни одной коллекции.</p>
                        <button className="btn-create" onClick={confirmCreation}>
                            Создать свой первый список
                        </button>
                    </div>
                )}
            </section>

            {membershipCollections.length > 0 && (
            <section className="feed-section">
                <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2>Коллекции в соавторстве</h2>
                </div>
                    <div
                        className="horizontal-scroll"
                        ref={memberCollectionsScroll.ref}
                        {...memberCollectionsScroll.events}
                    >
                        {membershipCollections.map(list => (
                            <div key={list.id} className="list-card">
                                <div className="card-image">


                                </div>
                                <div className="card-content">
                                    <Link to={`/collections/${list.id}`} className="link-without-line">
                                        <h3>{list.title}</h3>
                                    </Link>
                                    <div className="card-footer">
                                        <span className="items-count">♡ {list.likes || 0}   🎞 {list.item_associations?.length || 0}</span>
                                        {list.is_public ?
                                            <div className="private-badge" title="Публичная">
                                                <span>🌐</span>
                                                </div>
                                            :
                                            <div className="private-badge" title="Приватная">
                                                <span>🔒</span>
                                            </div>
                                        }
                                    </div>
                            </div>
                            </div>
                        ))}
                    </div>
            </section>)}

            {isModalOpen && (
                <div className="modal-overlay">
                <div className="modal-content profile-edit-modal">
                    <h3>Редактировать профиль</h3>
                    <form onSubmit={handleUpdate}>
                        <div className="avatar-edit-section">
                            <div className="profile-avatar big-avatar">
                                {previewUrl ? (
                                    <img src={previewUrl.startsWith('blob') ? previewUrl : `http://localhost:8000${previewUrl}`} alt="Preview" className="avatar-img" />
                                ) : (
                                    <span>{user.username ? user.username[0].toUpperCase() : user.email[0].toUpperCase()}</span>
                                )}
                            </div>
                            <div className="avatar-controls">
                                <button type="button" className="btn-secondary" onClick={() => fileInputRef.current.click()}>
                                    Изменить фото
                                </button>
                                {previewUrl && (
                                    <button type="button" className="btn-delete-text" onClick={removeAvatar}>
                                        Удалить
                                    </button>
                                )}
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label>Имя пользователя</label>
                            <input
                                type="text"
                                value={editData.username}
                                onChange={(e) => setEditData({...editData, username: e.target.value})}
                            />
                        </div>
                        <div className="form-group">
                            <label>Email</label>
                            <input
                                type="email"
                                value={editData.email}
                                onChange={(e) => setEditData({...editData, email: e.target.value})}
                            />
                        </div>
                        <div className="modal-buttons">
                            <button type="submit" className="btn-save">Сохранить</button>
                            <button type="button" className="btn-cancel" onClick={() => setIsModalOpen(false)}>Отмена</button>
                        </div>
                    </form>
                </div>
                </div>
            )}
        </div>
    );
};

export default Profile;