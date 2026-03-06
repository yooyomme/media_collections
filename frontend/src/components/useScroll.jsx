import { useState, useRef } from 'react';

export const useScroll = () => {
    const scrollRef = useRef(null);
    const [isDown, setIsDown] = useState(false);
    const [startX, setStartX] = useState(0);
    const [scrollLeftState, setScrollLeftState] = useState(0);

    const onMouseDown = (e) => {
        setIsDown(true);
        setStartX(e.pageX - scrollRef.current.offsetLeft);
        setScrollLeftState(scrollRef.current.scrollLeft);
    };

    const onMouseLeave = () => setIsDown(false);
    const onMouseUp = () => setIsDown(false);

    const onMouseMove = (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - scrollRef.current.offsetLeft;
        const walk = (x - startX) * 2; // Скорость прокрутки
        scrollRef.current.scrollLeft = scrollLeftState - walk;
    };

    return {
        ref: scrollRef,
        events: {
            onMouseDown,
            onMouseLeave,
            onMouseUp,
            onMouseMove
        }
    };
};