import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import api, { collectionApi, authApi, pictureBaseUrl } from '../api';
import { useAuth } from './AuthContext';
import { Forbidden } from './Errors'
import AccessGuard from './AccessGuard';
import SearchBar  from './SearchBar'

const Collection = () => {
    const { id } = useParams();

    // для правильной последовательности аутентификации и загрузки коллекции функционал коллекций во внутреннем элементе
    return (
        <AccessGuard collectionId={id}>
            <CollectionContent id={id} />
        </AccessGuard>
    );
};


const CollectionContent = ({id}) => {
    const navigate = useNavigate();
    const location = useLocation();

    const [loading, setLoading] = useState(true);
    const { user, logout } = useAuth();

    const [collection, setCollection] = useState(null);
    const [votes, setVotes] = useState(null);
    const [activeMedia, setActiveMedia] = useState(null);

    const [showSettings, setShowSettings] = useState(false);
    const [editMode, setEditMode] = useState({ field: null, value: '' });
    const cancelEdit = () => setEditMode({ field: null });

    const [showCoverEditModal, setShowCoverEditModal] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [tempCoverPreviewUrl, setTempCoverPreviewUrl] = useState(null);
    const [isUploadingCover, setIsUploadingCover] = useState(false);

    const loadCollection = useCallback(async () => {
        try {
            const res = await collectionApi.getCollection(id);
            const userVotes = await collectionApi.getUserVotesInCollection(id);
            setCollection(res.data);
            setVotes(userVotes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        loadCollection();
    }, [id]);

    useEffect(() => {
        return () => {
            if (tempCoverPreviewUrl) {
                URL.revokeObjectURL(tempCoverPreviewUrl);
            }
        };
    }, [tempCoverPreviewUrl]);

    const handleFileSelect = (event) => {
        const file = event.target.files[0];
        if (file) {
            if (tempCoverPreviewUrl) {
                URL.revokeObjectURL(tempCoverPreviewUrl); // Освобождаем предыдущий URL
            }
            setSelectedFile(file);
            setTempCoverPreviewUrl(URL.createObjectURL(file));
        } else {
            setSelectedFile(null);
            if (tempCoverPreviewUrl) {
                URL.revokeObjectURL(tempCoverPreviewUrl);
            }
            setTempCoverPreviewUrl(null);
        }
    };

    const handleSaveCover = async () => {
        if (!selectedFile && !collection.cover_image) {
            handleCancelCoverEdit();
            return;
        }
        setIsUploadingCover(true);
        try {
            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                const coverResponse = await collectionApi.uploadCover(collection.id, formData);
                const updatedCollection = coverResponse.data;
                setCollection(updatedCollection);
                handleCancelCoverEdit();
            } else if (collection.cover_image && !selectedFile) {
                handleCancelCoverEdit();
                return;
            }
        } catch (error) {
            console.error('Ошибка сохранения обложки:', error);
        } finally {
            setIsUploadingCover(false);
        }
    };

    const handleRemoveCover = async () => {
        setIsUploadingCover(true);
        try {
            const deleteCoverResponse = await collectionApi.deleteCover(collection.id);
            const updatedCollection = deleteCoverResponse.data;

            setCollection(updatedCollection);
            handleCancelCoverEdit();
        } catch (error) {
            console.error('Ошибка удаления обложки:', error);
        } finally {
            setIsUploadingCover(false);
        }
    };

    const handleCancelCoverEdit = () => {
        setShowCoverEditModal(false);
        setSelectedFile(null);
        if (tempCoverPreviewUrl) {
            URL.revokeObjectURL(tempCoverPreviewUrl);
        }
        setTempCoverPreviewUrl(null);
    };

    const getCoverSrc = (url) => {
        if (!url) return null;
        if (url.startsWith('blob:')) return url;
        if (url.startsWith('http')) return url;
        return `${pictureBaseUrl}${url}`;
    };

    const handleSaveField = async () => {
        try {
            await collectionApi.updateCollection(id, { [editMode.field]: editMode.value, user_id: user.id });
            setCollection({ ...collection, [editMode.field]: editMode.value });
            setEditMode({ field: null, value: '' });
        } catch (err) {
            console.error("Ошибка сохранения:", err);
        }
    };

    useEffect(() => {
        const wsUrl = `ws://localhost:8000/websocket/collection/${id}`;
        const socket = new WebSocket(wsUrl);

        socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log("Пришло сообщение из сокета:", data);
          if (data.type === 'COLLECTION_UPDATED') {
            console.log("Данные обновлены пользователем:", data.actor);
            loadCollection();
          }
        };
        socket.onopen = () => {
            console.log("Connected");
        };
        socket.onerror = (error) => {
            console.error("WebSocket Error:", error);
        };

        return () => {
          if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
            socket.close();
          }
        };
      }, [id, loadCollection]);


    if (loading) return <div className="error-page-container"><div className="error-title">Загрузка...</div></div>;
    if (!collection) return <Forbidden></Forbidden>;

    return (
        <div className="collection-page">
            <header className="collection-modern-header">
                <div className="collection-cover-wrapper">
                        <div className="collection-cover-display">
                            {collection.cover_image ? (
                                <img src={getCoverSrc(collection.cover_image)} alt="Collection Cover" className="collection-cover-image" />
                            ) : (
                                <div className="collection-cover-placeholder">
                                    <span>🖼️</span>
                                </div>
                            )}
                        </div>
                        <button
                            className="change-cover-button"
                            onClick={() => setShowCoverEditModal(true)}
                        >
                            Изменить
                        </button>
                </div>
                <div className="header-glass-container">
                    <div className="header-main-row">
                        <div className="title-wrapper">
                            <div className="status-badge">
                                {collection.is_public ?
                                    <span className="icon-globe" title="Публичная">🌐</span> :
                                    <span className="icon-lock" title="Приватная">🔒</span>
                                }
                            </div>
                            {editMode.field === 'title' ? (
                                <div className="edit-group active">
                                    <input
                                        autoFocus
                                        className="edit-input-title"
                                        maxLength="100"
                                        value={editMode.value}
                                        onChange={(e) => setEditMode({...editMode, value: e.target.value})}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSaveField()}
                                    />
                                    <div className="edit-controls">
                                        <button className="btn-confirm" onClick={handleSaveField}>Сохранить</button>
                                        <button className="btn-cancel" onClick={cancelEdit}>Отмена</button>
                                    </div>
                                </div>
                            ) : (
                                <h1 className="display-title" onClick={() => setEditMode({field: 'title', value: collection.title})}>
                                    {collection.title || "Коллекция"}
                                    <span className="edit-icon-hover">✎</span>
                                </h1>
                            )}
                        </div>

                        <div className="header-meta">
                            {collection.user_id === user.id && (
                                <button className="icon-btn settings-btn" onClick={() => setShowSettings(true)}>
                                    <span className="gear-icon">⚙</span>
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="description-wrapper">
                        {editMode.field === 'description' ? (
                            <div className="edit-group active column">
                                <textarea
                                    autoFocus
                                    className="edit-input-desc"
                                    maxLength="250"
                                    value={editMode.value}
                                    onChange={(e) => setEditMode({...editMode, value: e.target.value})}
                                />
                                <div className="edit-controls right">
                                    <button className="btn-confirm" onClick={handleSaveField}>Готово</button>
                                    <button className="btn-cancel" onClick={cancelEdit}>Отмена</button>
                                </div>
                            </div>
                        ) : (
                            <p className="display-desc" onClick={() => setEditMode({field: 'description', value: collection.description})}>
                                {collection.description || "Добавьте описание для вашей коллекции..."}
                                <span className="edit-icon-hover">✎</span>
                            </p>
                        )}
                    </div>
                </div>

                {showCoverEditModal && (
                    <div className="modal-cover-overlay">
                        <div className="modal-cover-content">
                            <h2>{collection.cover_image ? "Изменить обложку" : "Добавить обложку"}</h2>

                            <div className="modal-cover-preview-section">
                                <h3>Предпросмотр:</h3>
                                <div className="modal-cover-preview">
                                    {tempCoverPreviewUrl ? (
                                        <img src={getCoverSrc(tempCoverPreviewUrl)} alt="Предпросмотр новой обложки" />
                                    ) : collection.cover_image ? (
                                        <img src={getCoverSrc(collection.cover_image)} alt="Текущая обложка" />
                                    ) : (
                                        <div className="modal-cover-preview-placeholder">
                                            <span>Нет обложки</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="file-input-wrapper">
                                <input type="file" accept="image/*" onChange={handleFileSelect} id="cover-upload-input" style={{ display: 'none' }} />
                                <label htmlFor="cover-upload-input" className="btn-save-file">
                                    {selectedFile ? "Выбрано: " + selectedFile.name : "Выбрать файл"}
                                </label>
                                {selectedFile && <span className="selected-file-name">{selectedFile.name}</span>}
                            </div>
                            <div className="modal-cover-buttons">
                                {collection.cover_image && (
                                    <button onClick={handleRemoveCover} className="btn-cancel" disabled={isUploadingCover}>
                                        Удалить обложку
                                    </button>
                                )}
                                <button className="btn-cancel" onClick={handleCancelCoverEdit} disabled={isUploadingCover}>Отмена</button>
                                <button className="btn-save" onClick={handleSaveCover} disabled={isUploadingCover || (!selectedFile && !collection.cover_image)}>
                                    {isUploadingCover ? 'Загрузка...' : 'Сохранить'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </header>

            <SearchBar
                collectionId={collection.id}
                onAdded={loadCollection}
            />

            <div className="media-list">
                <div className="list-labels">
                    <span className="col-num">#</span>
                    <span className="col-title">Название</span>
                    <span className="col-rating">Интерес</span>
                    <span className="col-title">Удалить</span>
                </div>
                {collection.item_associations && collection.item_associations.map((association, index) => {
                    const userVoteValue = votes ? (votes[association.id] || 0) : 0;
                    const item = {
                        ...association,
                        user_vote: userVoteValue
                    };
                    return (
                        <MediaRow
                            key={item.id}
                            item={item}
                            index={index + 1}
                            collectionId={id}
                            onInfoClick={() => setActiveMedia(item)}
                            onUpdate={loadCollection}
                        />
                    );
                })}
            </div>

            {activeMedia && (
                <div className="modal-overlay" onClick={() => setActiveMedia(null)}>
                    <div className="media-modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-poster">
                            <img src={`https://simkl.in/posters/${activeMedia.poster}_ca.jpg`} alt="poster" />
                        </div>
                        <div className="modal-info">
                            <h2>{activeMedia.title_en}</h2>

                            <div className="meta-grid">
                                <span>Год выпуска: {activeMedia.year}</span>
                            </div>
                            <button className="btn-escape" onClick={() => setActiveMedia(null)}>Закрыть</button>
                        </div>
                    </div>
                </div>
            )}

            {showSettings && (
                <SettingsModal
                    collection={collection}
                    onClose={() => setShowSettings(false)}
                    onUpdate={loadCollection}
                />
            )}
        </div>
    );
};


const MediaRow = ({ item, index, collectionId, onInfoClick, onUpdate}) => {
    const [userRating, setUserRating] = useState(item.user_vote || 0);
    const [isRated, setIsRated] = useState(!!item.user_vote);
    const [hoverRating, setHoverRating] = useState(0);

    const handleRate = async (val) => {
        try {
            const data = await collectionApi.rateMediaItem(collectionId, item.id, val);
            setUserRating(data.user_rate);
            setIsRated(true);
        } catch (err) {
            console.error("Ошибка при оценке:", err);
        }
    };

    const confirmDeleteItem = async (item) => {
        await collectionApi.deleteMediaItem(item.id, collectionId);
        onUpdate();
    };

    return (
        <div className="media-row">
            <div className="row-left">
                <span className="row-index">{index}</span>
                <div className="row-main-info">
                    <span className="row-title-en">{item.title_en}</span>
                    <span className="row-year">{item.year}</span>
                </div>
                <button className="info-btn" onClick={onInfoClick}>ℹ</button>
            </div>
            <div>
                <div className="rating-block">
                    <div className="rating-info">
                        <span className="avg-label">Общий рейтинг:</span>
                        <span className={`avg-value ${item.average_rating > 3.5 ? '' : 'disabled'}`}>{Number(item.average_rating).toFixed(1)}</span>
                    </div>

                    <div className="user-rating-zone">
                        <span className="user-rating-label">
                            {userRating > 0 ? 'Ваша оценка:' : 'Оценить:'}
                        </span>
                        <div className="five-step-slider" onMouseLeave={() => setHoverRating(0)}>
                            {[1, 2, 3, 4, 5].map(star => (
                                <div
                                    key={star}
                                    className={`rating-step ${
                                        (hoverRating || userRating) >= star ? 'active' : ''
                                    } ${hoverRating >= star ? 'hover' : ''}`}
                                    onMouseEnter={() => setHoverRating(star)}
                                    onClick={() => handleRate(star)}
                                />
                            ))}
                        </div>
                    </div>

                </div>
            </div>
            <div className="row-right">
                <button className="row-remove-item" onClick={() => confirmDeleteItem(item)}>✕</button>
            </div>
        </div>
    );
};


const SettingsModal = ({ collection, onClose, onUpdate }) => {
    const location = useLocation();

    const [activeTab, setActiveTab] = useState('general');
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isUpdating, setIsUpdating] = useState(false);

    const [members, setMembers] = useState([]);
    const [showMembers, setShowMembers] = useState(false);

    const [privacyValue, setPrivacyValue] = useState('private');
    const [hasExistingPassword] = useState(!!collection.has_password);

    const [isListOpen, setIsListOpen] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);
    const dropdownRef = useRef(null);
    const privacyListRef = useRef(null);

    const { user, logout } = useAuth();

    const privacyList = [
        {value: "private", label: "Приватный режим. Доступно только вам и текущим участникам"},
        {value: "password", label: "Доступ по паролю"},
        {value: "link", label: "Доступ по специальной ссылке"},
        {value: "link_and_password", label: "Доступ по специальной ссылке и паролю"},
        ]

    const [privacySettings, setPrivacySettings] = useState({
        access_type: collection?.access_type || 'private',
        password: '',
        token: '',
        shouldResetToken: false,
        shouldRemoveMembers: false
    });

    useEffect(() => {
        if (collection) {
            setPrivacySettings(prev => ({
                ...prev,
                access_type: collection.access_type || 'private'
            }));
        }
    }, [collection]);

    const handleSavePrivacy = async () => {
        try {
            await collectionApi.updatePrivacy(collection.id, {
                access_type: privacySettings.access_type,
                password: privacySettings.password
            });

            if (onUpdate) {
                await onUpdate();
            }
            onClose()
        } catch (err) {
            console.error(err);
        }
    };

    const handleGetLink = async () => {
        try {
            const response = await collectionApi.getInviteToken(collection.id)
            const shareableUrl = `${ window.location.origin }/collections/${collection.id}/?invite_token=${response.data.invite_token}`;
            await navigator.clipboard.writeText(shareableUrl);
        } catch (err) {
            console.error("Ошибка при получении ссылки:", err);
        }
    };

    const handleResetLink = async () => {
        try {
            const res = await collectionApi.resetInviteToken(collection.id);
            setCollection(prev => ({ ...prev, invite_token: res.data.invite_token }));
        } catch (err) {
            console.error("Ошибка сброса:", err);
        }
    }

    const loadMembers = async () => {
        try {
            if (!showMembers) {
                const res = await collectionApi.getMembers(collection.id);
                setMembers(res.data);
                setShowMembers(true);
            } else {
                setShowMembers(false);
            }
        } catch (err) {
            console.error("Ошибка загрузки участников", err);
        }
    };

    const removeUser = async (userId) => {
        await collectionApi.removeMember(collection.id, userId);
        setMembers(members.filter(p => p.id !== userId));
    };

    const handleRemoveUsers = async () => {
        try {
            await collectionApi.clearMembers(collection.id);

        } catch (err) {
            console.error(err);
        }
        if (onUpdate) {
                await onUpdate();
        }
        onClose()
    };

    const handleTogglePublic = async (e) => {
        setIsUpdating(true);
        try {
            await collectionApi.updateSettings(collection.id, { is_public: e.target.checked, user_id: user.id });
            onUpdate();
        } catch (error) {
            console.error("Ошибка обновления:", error);
        } finally {
            setIsUpdating(false);
        }
    };

    const confirmDelete = async () => {
        await collectionApi.deleteCollection(collection.id);
        window.location.href = '/profile';
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
            if (privacyListRef.current && !privacyListRef.current.contains(event.target)) {
                setIsListOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="settings-card" onClick={e => e.stopPropagation()}>
                <aside className="settings-sidebar">
                    <h3>Настройки</h3>
                    <nav>
                        <button
                            className={activeTab === 'general' ? 'active' : ''}
                            onClick={() => setActiveTab('general')}
                        >
                            Основное
                        </button>
                        <button
                            className={activeTab === 'privacy' ? 'active' : ''}
                            onClick={() => setActiveTab('privacy')}
                        >
                            Доступ
                        </button>
                        <button
                            className={activeTab === 'danger' ? 'active' : ''}
                            onClick={() => setActiveTab('danger')}
                        >
                            Управление
                        </button>
                    </nav>
                    <button className="btn-close-aside" onClick={onClose}>Закрыть</button>
                </aside>
                <main className="settings-content">
                    {activeTab === 'general' && (
                        <div className="tab-pane">
                            <h2>Основные настройки</h2>
                            <div className="setting-row">
                                <div className="setting-info">
                                    <span className="setting-label">Публичный доступ</span>
                                    <span className="setting-desc">Позволяет другим пользователям видеть вашу коллекцию</span>
                                </div>
                                <label className="switch">
                                    <input
                                        type="checkbox"
                                        checked={collection.is_public}
                                        onChange={handleTogglePublic}
                                        disabled={isUpdating}
                                    />
                                    <span className="slider round"></span>
                                </label>
                            </div>
                        </div>
                    )}

                    {activeTab === 'privacy' && (
                        <div className="tab-pane privacy-container">
                            <h2 className="tab-title">Приватность и доступ</h2>

                            <div className="privacy-list-container" ref={privacyListRef}>
                                <label className="settings-label">Режим доступа</label>
                                <div
                                    className={`privacy-list-current ${isListOpen ? 'active' : ''}`}
                                    onClick={() => setIsListOpen(!isListOpen)}
                                >
                                    <span className="current-label">
                                        {privacyList.find(opt => opt.value === privacySettings.access_type)?.label}
                                    </span>
                                    <span className={`chevron-icon ${isListOpen ? 'rotated' : ''}`}>▾</span>
                                </div>

                                {isListOpen && (
                                    <div className="privacy-list-options-list">
                                        {privacyList.map((opt) => (
                                            <div
                                                key={opt.value}
                                                className={`privacy-list-option ${privacySettings.access_type === opt.value ? 'selected' : ''}`}
                                                onClick={() => {
                                                    setPrivacySettings({ ...privacySettings, access_type: opt.value });
                                                    setIsListOpen(false);
                                                }}
                                            >
                                                {opt.label}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {(privacySettings.access_type === 'password' || privacySettings.access_type === 'link_and_password') && (
                                <div className="settings-group">
                                    <label className="settings-label">Пароль коллекции</label>
                                    <input
                                        type="password"
                                        className="custom-input"
                                        placeholder={hasExistingPassword ? "••••••••" : "Введите новый пароль"}
                                        value={privacySettings.password}
                                        onChange={(e) => setPrivacySettings({...privacySettings, password: e.target.value})}
                                    />
                                </div>
                            )}

                            {(privacySettings.access_type === 'link' || privacySettings.access_type === 'link_and_password') && (
                                <div className="modal-buttons">
                                    <button className="btn-confirm" style={{ flex: '1' }} onClick={handleGetLink}>
                                        Получить ссылку
                                    </button>
                                    <button className="btn-cancel" style={{ flex: '1' }} onClick={handleResetLink}>
                                        Обновить ссылку
                                    </button>
                                </div>
                            )}
                            <div className="save-section">
                                <button className="btn-confirm" style={{ width: "100%", height: "35px" }} onClick={handleSavePrivacy}>Сохранить настройки</button>
                            </div>
                            <hr className="divider" />
                            <label className="settings-label">Участники коллекции</label>
                            <div>
                                <button className="btn-var" onClick={loadMembers}>
                                    Посмотреть участников
                                </button>
                                <button className="btn-danger" onClick={handleRemoveUsers}>
                                    Удалить всех
                                </button>
                            </div>

                            {showMembers && (
                                <div className="participants-list">
                                    {members.length > 0 ? members.map(member => (
                                        <div key={member.user.id}>
                                            <div className="u-info">
                                                <label>Имя пользователя</label>
                                                <label>Email</label>
                                                <label>Дата присоединения</label>
                                                <label>Удалить пользователя</label>
                                            </div>
                                            <hr className="divider" />
                                            <div className="participant-item">
                                                <div className="u-info">
                                                    <span>{member.user.username || "Аноним"}</span>
                                                    <span>{member.user.email?.substring(0, 3)}***@***</span>
                                                    <span>{new Date(member.joined_at).toLocaleDateString()}</span>
                                                    <button className="btn-icon-delete" onClick={() => removeUser(member.user.id)}>✕</button>
                                                </div>
                                            </div>
                                        </div>
                                    )) : <p style={{ textAlign: "center" }}>Список пуст</p>}
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'danger' && (
                        <div className="tab-pane">
                            <h2>Управление</h2>
                            <div className="placeholder-box">
                                <p className="warning-text">Внимание! Удаление коллекции необратимо.</p>
                                <button className="btn-danger" onClick={() => setShowDeleteConfirm(true)}>
                                    Удалить коллекцию навсегда
                                </button>
                            </div>
                        </div>
                    )}
                </main>

                {showDeleteConfirm && (
                    <div className="confirm-overlay">
                        <div className="confirm-dialog">
                            <h3>Вы уверены?</h3>
                            <p>Это действие нельзя будет отменить. Все данные коллекции будут стерты.</p>
                            <div className="confirm-buttons">
                                <button className="btn-cancel" style={{ flex: '1' }} onClick={() => setShowDeleteConfirm(false)}>Отмена</button>
                                <button className="btn-save" style={{ flex: '1' }} onClick={confirmDelete}>Да, удалить</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Collection;