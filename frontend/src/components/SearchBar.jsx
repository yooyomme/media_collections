import React, { useState, useEffect, useRef } from 'react';
import { collectionApi } from '../api';

const SearchBar = ({ collectionId, onAdded }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showDropdown, setShowDropdown] = useState(false);

    const [isCategoryOpen, setIsCategoryOpen] = useState(false);
    const [category, setCategory] = useState(1);

    const dropdownRef = useRef(null);
    const categoryRef = useRef(null);

    const controller = new AbortController();

    const categories = [
        { id: 1, slug: 'movie', label: 'Фильмы' },
        { id: 2, slug: 'tv', label: 'Сериалы' },
        { id: 3, slug: 'anime', label: 'Аниме' }
    ];

    useEffect(() => {
        if (query.trim().length < 2) {
            setResults([]);
            setShowDropdown(false);
            return;
        }
        const delayDebounceFn = setTimeout(async () => {
            setIsSearching(true);
            try {
                const data = await collectionApi.searchMediaItem(query, category, collectionId, controller.signal);
                setResults(data);
                setShowDropdown(true);
            } catch (error) {
                console.error("Search error:", error);
            } finally {
                setIsSearching(false);
            }
        }, 1500);
        return () => {
            clearTimeout(delayDebounceFn);
            controller.abort();
        };
    }, [query, category]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
            if (categoryRef.current && !categoryRef.current.contains(event.target)) {
                setIsCategoryOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleAdd = async (item) => {
        try {
            await collectionApi.addMediaItemToCollection(
                item.simkl_id,
                categories.find(c => c.id === category).slug,
                collectionId,
            );
            setResults(prev => prev.map(r =>
                r.simkl_id === item.simkl_id ? { ...r, already_in_collection: true } : r
            ));
            if (onAdded) onAdded();
        } catch (error) {
            console.error("Ошибка при добавлении:", error);
        }
    };

    return (
        <div className="search-container" ref={dropdownRef}>
            <div className="search-wrapper">
                <div className="category-container" ref={categoryRef}>
                    <div
                        className={`category-current ${isCategoryOpen ? 'active' : ''}`}
                        onClick={() => setIsCategoryOpen(!isCategoryOpen)}
                    >
                        {categories.find(c => c.id === category).label}
                        <span className="chevron-icon">▾</span>
                    </div>

                    {isCategoryOpen && (
                        <div className="category-options-list">
                            {categories.map((cat) => (
                                <div
                                    key={cat.id}
                                    className={`category-option ${category === cat.id ? 'selected' : ''}`}
                                    onClick={() => {
                                        setCategory(cat.id);
                                        setIsCategoryOpen(false);
                                    }}
                                >
                                    {cat.label}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                <div className="input-inner-wrapper">
                    <input
                        type="text"
                        className="search-input"
                        placeholder={`Ищем ${categories.find(c => c.id === category).label.toLowerCase()}...`}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onFocus={() => results.length > 0 && setShowDropdown(true)}
                    />
                    <div className="search-status-icon">
                        {isSearching && <div className="search-loader"></div>}
                    </div>
                </div>
            </div>

            {showDropdown && results.length > 0 && (
                <div className="search-results-panel">
                    {results.map((item) => (
                        <div key={item.simkl_id} className="search-result-item">
                            <div className="item-details">
                                <span className="item-name">{item.title}</span>
                                <span className="item-info-row">{item.year} • {categories.find(c => c.id === category).slug.toUpperCase()}</span>
                            </div>
                            <button
                                className={`add-action-btn ${item.already_in_collection ? 'disabled' : ''}`}
                                onClick={() => !item.already_in_collection && handleAdd(item)}
                                disabled={item.already_in_collection}
                            >
                                {item.already_in_collection ? 'Добавлено' : 'Добавить'}
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default SearchBar;