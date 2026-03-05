import { useState, useRef, useCallback } from 'react';

export function useMagneticTilt(strength = 15) {
    const ref = useRef(null);
    const [transform, setTransform] = useState('perspective(800px) rotateX(0deg) rotateY(0deg) translateZ(0px)');
    const [glarePosition, setGlarePosition] = useState({ x: 50, y: 50, opacity: 0 });

    const handleMouseMove = useCallback((e) => {
        if (!ref.current) return;
        const rect = ref.current.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = (e.clientX - cx) / (rect.width / 2);
        const dy = (e.clientY - cy) / (rect.height / 2);
        const rotX = -dy * strength;
        const rotY = dx * strength;

        setTransform(
            `perspective(600px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateZ(20px)`
        );

        const xPct = ((e.clientX - rect.left) / rect.width) * 100;
        const yPct = ((e.clientY - rect.top) / rect.height) * 100;
        setGlarePosition({ x: xPct, y: yPct, opacity: 1 });
    }, [strength]);

    const handleMouseLeave = useCallback(() => {
        setTransform('perspective(600px) rotateX(0deg) rotateY(0deg) translateZ(0px)');
        setGlarePosition(prev => ({ ...prev, opacity: 0 }));
    }, []);

    return { ref, transform, handleMouseMove, handleMouseLeave, glarePosition };
}
