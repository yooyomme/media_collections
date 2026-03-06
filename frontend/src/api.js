import axios from 'axios';

const api = axios.create({
     baseURL: 'http://localhost:8000/api',
     withCredentials: true,
});

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
        }
        return Promise.reject(error);
    }
);


//export const searchMedia = async (query, category_slug, collection_id, signal) => {
//    const response = await api.get(`/items/search/list`, {
//        params: { query, category_slug, collection_id },
//        signal: signal
//    });
//    return response.data;
//};
//
//export const addToCollection = async (itemData) => {
//    const response = await api.post(`/items/search/add`, itemData);
//    return response.data;
//};
//


export const collectionApi = {
    createCollection: (data) => api.post(`/collections`, data),
    getCollection: (id) => api.get(`/collections/${id}`),
    updateCollection: (id, data) => api.patch(`/collections/${id}`, data),
    deleteCollection: (id) => api.delete(`/collections/${id}`),
    updateSettings: (id, data) => api.patch(`/collections/${id}`, data),

    searchMediaItem: (query, categoryId, collectionId, signal) => api.get(`/items/search/list`, {
            params: {
                query,
                category_id: categoryId,
                collection_id: collectionId },
                signal
            }).then(res => res.data),
    addMediaItemToCollection: (simklId, mediaType, collectionId) => api.post(`/items/search/add`, {
            simkl_id: simklId,
            media_type: mediaType,
            collection_id: collectionId,
        }),
    rateMediaItem: (collectionId, itemId, rating) => api.post(`/collections/${ collectionId }/items/${ itemId }/rate`, {
            collection_id: collectionId,
            item_id: itemId,
            score: rating
    }).then(res => res.data),
    getUserVotesInCollection: (id) => api.get(`/collections/${ id }/rating_info`),
    deleteMediaItem: (itemId, collectionId) => api.delete(`/collections/${ collectionId }/items/${ itemId }`),

    updatePrivacy: (id, settings) => api.patch(`/collections/${id}/settings`, settings),
    uploadCover: (id, formData) => api.post(`/collections/${id}/cover`, formData),
    deleteCover: (id) => api.delete(`/collections/${id}/cover`),

    getInviteToken: (id) => api.get(`/collections/${id}/share`),
    resetInviteToken: (id) => api.patch(`/collections/${id}/settings/reset_invite_token`),

    getMembers: (id) => api.get(`/collections/${id}/members`),
    clearMembers: (id) => api.delete(`/collections/${id}/members`),
    removeMember: (id, memberId) => api.delete(`/collections/${id}/members/${memberId}`),
};

export const authApi = {
    register: (email, password, username) => api.post(`/users/register`, { email, password, username }),
    login: (email, password) => api.post(`/users/login`, { email, password }),
    logout: () => api.post(`users/logout`),
    refresh: () => api.post(`/users/token/refresh`),
    getMe: () => api.get(`/users/get_info/me`),

    getUserById: (id) => api.get(`/users/${id}`),

    updateUser: (id, data) => api.patch(`/users/${id}`, data),
    uploadAvatar: (id, formData) => api.post(`/users/${id}/avatar`, formData),
    deleteAvatar: (id) => api.delete(`/users/${id}/avatar`),

    deleteUser: (id) => api.delete(`/users/${id}`),

    getUserCollections: (id) => api.get(`/users/${id}/collections`),
    getUserMemberCollections: (id) => api.get(`/users/${id}/membership_collections`)
};

export const setAuthHeader = (token) => {
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete api.defaults.headers.common['Authorization'];
    }
};

export const pictureBaseUrl = "http://localhost:8000";

export default api;