/**
 * DepthLayers — CSS-only atmospheric depth fog
 *
 * Three radial-gradient blobs drifting at different speeds and depths.
 * All layers are position:fixed, z-index:1, pointer-events:none so they
 * sit behind all page content and never block interaction.
 *
 * Keyframes are defined in index.css (drift1 / drift2 / drift3).
 */
const DepthLayers = () => (
    <>
        {/* Layer 1 — Closest: fast drift, cyan, most visible */}
        <div style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1,
            pointerEvents: 'none',
            background: 'radial-gradient(ellipse 600px 300px at 20% 50%, rgba(0,212,255,0.04) 0%, transparent 70%)',
            animation: 'drift1 20s ease-in-out infinite alternate',
            willChange: 'transform',
        }} />

        {/* Layer 2 — Mid: medium drift, violet, subtle */}
        <div style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1,
            pointerEvents: 'none',
            background: 'radial-gradient(ellipse 800px 400px at 80% 30%, rgba(124,77,255,0.03) 0%, transparent 70%)',
            animation: 'drift2 28s ease-in-out infinite alternate',
            willChange: 'transform',
        }} />

        {/* Layer 3 — Far: slow drift, rose, least visible */}
        <div style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1,
            pointerEvents: 'none',
            background: 'radial-gradient(ellipse 1000px 500px at 50% 80%, rgba(255,61,113,0.02) 0%, transparent 70%)',
            animation: 'drift3 35s ease-in-out infinite alternate',
            willChange: 'transform',
        }} />
    </>
);

export default DepthLayers;
