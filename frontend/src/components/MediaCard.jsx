import React from 'react';
import { collectionsApi } from '../api';

const MediaCard = ({ media, collectionId, onRated }) => {
    const handleRate = async (score) => {
        await collectionsApi.rateMedia(collectionId, media.id, score);
        onRated();
    };

    const ratingPercent = (media.avg_rating / 5) * 100;

    return (
        <div className="media-card">
            <img src={media.poster} alt={media.title} />
            <div className="media-info">
                <h3>{media.title} ({media.year})</h3>

                <div className="rating-area">
                    <p>Средняя оценка: {media.avg_rating.toFixed(1)} / 5</p>
                    <div className="progress-bar">
                        <div className="progress-fill" style={{ width: '${ratingPercent}%' }}>...</div>
                    </div>
                </div>

                <div className="vote-buttons">
                    <span>Твоя оценка:</span>
                    {[1, 2, 3, 4, 5].map(num => (
                        <button
                            key={num}
                            className={media.user_rating === num ? 'active' : ''}
                            onClick={() => handleRate(num)}
                        >
                            {num}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default MediaCard;