import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Box, Typography, Chip, Paper } from '@mui/material';

const BlockchainViz3D = ({ blocks = [], chainIntegrity = true }) => {
    const mountRef = useRef(null);
    const [hoveredBlock, setHoveredBlock] = useState(null);
    const hoveredRef = useRef(null);
    const prevIntegrity = useRef(chainIntegrity);
    const animationData = useRef({ verifyTime: 0 });

    useEffect(() => {
        if (!mountRef.current) return;

        // Handle initial width/height being 0
        let width = mountRef.current.clientWidth || mountRef.current.parentElement.clientWidth || 800;
        let height = 200; // Fixed height since parent might be dynamic

        const scene = new THREE.Scene();

        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        camera.position.set(0, 2, 8);

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        mountRef.current.appendChild(renderer.domElement);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableRotate = false;
        controls.enablePan = true;
        controls.enableZoom = false;
        controls.mouseButtons = {
            LEFT: THREE.MOUSE.PAN,
            MIDDLE: null,
            RIGHT: null
        };
        // Limit pan to horizontal/vertical slightly
        controls.screenSpacePanning = true;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x0a1628, 0.5);
        scene.add(ambientLight);

        // Floor Grid
        const gridHelper = new THREE.GridHelper(50, 25, 0x00d4ff, 0x00d4ff);
        gridHelper.position.y = -0.8;
        gridHelper.material.opacity = 0.1;
        gridHelper.material.transparent = true;
        scene.add(gridHelper);

        const centerLight = new THREE.PointLight(0x00d4ff, 2, 10);
        centerLight.position.set(0, 4, 0);
        scene.add(centerLight);

        const rightLight = new THREE.PointLight(0x7c4dff, 1, 8);
        rightLight.position.set(8, 0, 0);
        scene.add(rightLight);

        let blockObjects = [];
        let chainLinks = [];
        let time = 0;
        let rafId;

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2(-10, -10); // Start off-screen

        const onMouseMove = (event) => {
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        };
        const onMouseLeave = () => {
            mouse.x = -10;
            mouse.y = -10;
        };
        renderer.domElement.addEventListener('mousemove', onMouseMove);
        renderer.domElement.addEventListener('mouseleave', onMouseLeave);

        const handleResize = () => {
            if (!mountRef.current) return;
            width = mountRef.current.clientWidth || mountRef.current.parentElement.clientWidth || 800;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        };
        window.addEventListener('resize', handleResize);

        const renderBlocks = () => {
            // Clean up old
            [...blockObjects, ...chainLinks].forEach(obj => {
                scene.remove(obj);
                if (obj.geometry) obj.geometry.dispose();
                if (obj.material) {
                    if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
                    else obj.material.dispose();
                }
            });
            blockObjects = [];
            chainLinks = [];

            // Get up to 10 latest blocks, reversed so newest is on the right
            let visibleBlocks = [...blocks].slice(0, 10).reverse();

            // Render a Genesis Block if no records exist yet
            if (visibleBlocks.length === 0) {
                visibleBlocks = [{
                    timestamp: new Date().toISOString(),
                    ip_address: 'GENESIS NODE',
                    attack_type: 'SYSTEM INIT',
                    new_score: 50,
                    old_score: 50,
                    hash: '000000000000000000000000000',
                    is_malicious: false
                }];
            }

            visibleBlocks.forEach((blockData, index) => {
                const isNewest = index === visibleBlocks.length - 1;
                const xPos = index * 2.2;
                const yPos = isNewest ? 0.2 : 0;

                const geom = new THREE.BoxGeometry(1.2, 0.8, 0.6);
                const mat = new THREE.MeshStandardMaterial({
                    color: 0x0a1628,
                    emissive: 0x00d4ff,
                    emissiveIntensity: isNewest ? 0.4 : 0.15
                });
                const mesh = new THREE.Mesh(geom, mat);
                mesh.position.set(xPos, yPos, 0);
                mesh.userData = { blockData, isNewest, originalEmissive: isNewest ? 0.4 : 0.15 };

                const edges = new THREE.EdgesGeometry(geom);
                const line = new THREE.LineSegments(
                    edges,
                    new THREE.LineBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.6 })
                );
                line.raycast = () => { }; // Disable interaction on wireframe
                mesh.add(line);

                scene.add(mesh);
                blockObjects.push(mesh);

                if (index < visibleBlocks.length - 1) {
                    const linkGeom = new THREE.CylinderGeometry(0.04, 0.04, 1.0);
                    const linkMat = new THREE.MeshBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.5 });
                    const linkMesh = new THREE.Mesh(linkGeom, linkMat);

                    linkMesh.rotation.z = Math.PI / 2;
                    linkMesh.position.set(xPos + 1.1, 0, 0);
                    linkMesh.userData = { offset: index };

                    scene.add(linkMesh);
                    chainLinks.push(linkMesh);
                }
            });

            // Auto-pan to the newest block
            const targetX = visibleBlocks.length > 0 ? (visibleBlocks.length - 1) * 2.2 : 0;
            camera.position.x = Math.max(0, targetX - 4);
            controls.target.set(camera.position.x, 0, 0);
            controls.update();

            // Move center light to the middle of the blocks
            centerLight.position.x = targetX / 2;
        };

        renderBlocks();

        const animate = () => {
            time += 0.016;

            // Wobble
            blockObjects.forEach((b, i) => {
                b.rotation.y = Math.sin(time * 0.5 + i) * 0.05;
            });

            // Integrity verification animation (pulse green for 2 seconds when chainIntegrity becomes true)
            if (chainIntegrity !== prevIntegrity.current) {
                if (chainIntegrity) animationData.current.verifyTime = time;
                prevIntegrity.current = chainIntegrity;
            }

            const timeSinceVerify = time - animationData.current.verifyTime;
            const isVerifying = timeSinceVerify < 2.0;

            chainLinks.forEach(l => {
                if (isVerifying) {
                    l.material.color.setHex(0x00e676);
                    l.material.opacity = Math.sin(time * 8) * 0.4 + 0.6; // flash simultaneously
                } else if (!chainIntegrity) {
                    l.material.color.setHex(0xff3d71);
                    l.material.opacity = 0.8;
                } else {
                    l.material.color.setHex(0x00d4ff);
                    l.material.opacity = Math.sin(time * 2 + l.userData.offset) * 0.3 + 0.5;
                }
            });

            if (isVerifying && Math.sin(time * 8) > 0) {
                centerLight.color.setHex(0x00e676);
            } else if (!chainIntegrity) {
                centerLight.color.setHex(0xff3d71);
            } else {
                centerLight.color.setHex(0x00d4ff);
            }

            // Raycaster
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(blockObjects, false); // Ignore children

            blockObjects.forEach(b => {
                b.scale.setScalar(1.0); // Reset scale uniformly
                b.material.emissiveIntensity += (b.userData.originalEmissive - b.material.emissiveIntensity) * 0.1;
            });

            if (intersects.length > 0) {
                const hoveredObj = intersects[0].object;
                hoveredObj.scale.setScalar(1.05); // Scale uniformly using scalar constraint
                hoveredObj.material.emissiveIntensity += (0.8 - hoveredObj.material.emissiveIntensity) * 0.2;

                const data = hoveredObj.userData.blockData;
                if (hoveredRef.current !== data) {
                    hoveredRef.current = data;
                    setHoveredBlock(data);
                }
            } else {
                if (hoveredRef.current !== null) {
                    hoveredRef.current = null;
                    setHoveredBlock(null);
                }
            }

            controls.update();
            renderer.render(scene, camera);
            rafId = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            cancelAnimationFrame(rafId);
            window.removeEventListener('resize', handleResize);
            renderer.domElement.removeEventListener('mousemove', onMouseMove);
            renderer.domElement.removeEventListener('mouseleave', onMouseLeave);
            renderer.dispose();
            scene.traverse(obj => {
                if (obj.geometry) obj.geometry.dispose();
                if (obj.material) {
                    if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
                    else obj.material.dispose();
                }
            });
            if (mountRef.current) mountRef.current.innerHTML = '';
        };
    }, [blocks, chainIntegrity]); // Re-render scene when blocks update

    return (
        <Box sx={{ position: 'relative', width: '100%', mb: 3, zIndex: 50 }}>
            <Box
                ref={mountRef}
                sx={{
                    width: '100%',
                    height: 200,
                    backgroundColor: 'transparent',
                    cursor: hoveredBlock ? 'pointer' : 'grab',
                    '&:active': { cursor: 'grabbing' }
                }}
            />

            {/* Tooltip Overlay */}
            {hoveredBlock && (
                <Paper sx={{
                    position: 'absolute',
                    top: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    mt: -2,
                    p: 2,
                    backgroundColor: 'rgba(10, 22, 40, 0.95)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(0, 212, 255, 0.4)',
                    borderRadius: '12px',
                    zIndex: 10,
                    minWidth: 320,
                    pointerEvents: 'none',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)'
                }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1, borderBottom: '1px solid rgba(255, 255, 255, 0.1)', pb: 1 }}>
                        <Typography variant="caption" sx={{ color: '#00d4ff', fontFamily: '"IBM Plex Mono", monospace', fontWeight: 600 }}>
                            BLOCK ID: {hoveredBlock.hash?.substring(0, 8)}...
                        </Typography>
                        <Chip label={hoveredBlock.attack_type} size="small" sx={{
                            height: 20,
                            fontSize: '0.65rem',
                            fontWeight: 700,
                            backgroundColor: hoveredBlock.is_malicious ? 'rgba(255, 61, 113, 0.15)' : 'rgba(0, 230, 118, 0.15)',
                            color: hoveredBlock.is_malicious ? '#ff3d71' : '#00e676',
                            border: `1px solid ${hoveredBlock.is_malicious ? 'rgba(255, 61, 113, 0.3)' : 'rgba(0, 230, 118, 0.3)'}`
                        }} />
                    </Box>

                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="caption" sx={{ color: '#7a9bbf' }}>Timestamp:</Typography>
                            <Typography variant="caption" sx={{ color: '#a0b2c6', fontFamily: '"IBM Plex Mono", monospace' }}>
                                {new Date(hoveredBlock.timestamp).toLocaleString()}
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="caption" sx={{ color: '#7a9bbf' }}>Source IP:</Typography>
                            <Typography variant="caption" sx={{ color: '#e8f4fd', fontFamily: '"IBM Plex Mono", monospace', fontWeight: 600 }}>
                                {hoveredBlock.ip_address}
                            </Typography>
                        </Box>

                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5, backgroundColor: 'rgba(0,0,0,0.2)', p: 0.5, borderRadius: '4px' }}>
                            <Typography variant="caption" sx={{ color: '#7a9bbf' }}>Score Shift:</Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="caption" sx={{ color: '#a0b2c6', fontFamily: '"IBM Plex Mono", monospace' }}>
                                    {hoveredBlock.old_score}
                                </Typography>
                                <Typography variant="caption" sx={{ color: '#3d5a7a' }}>→</Typography>
                                <Typography variant="caption" sx={{
                                    color: (hoveredBlock.new_score - hoveredBlock.old_score) > 0 ? '#ff3d71' : '#00e676',
                                    fontFamily: '"Rajdhani", sans-serif',
                                    fontWeight: 700,
                                    fontSize: '0.8rem'
                                }}>
                                    {hoveredBlock.new_score}
                                    ({(hoveredBlock.new_score - hoveredBlock.old_score) > 0 ? '+' : ''}{hoveredBlock.new_score - hoveredBlock.old_score})
                                </Typography>
                            </Box>
                        </Box>

                        <Typography variant="caption" sx={{ color: '#3d5a7a', fontFamily: '"IBM Plex Mono", monospace', fontSize: '0.55rem', mt: 1, wordBreak: 'break-all' }}>
                            HASH: {hoveredBlock.hash}
                        </Typography>
                    </Box>
                </Paper>
            )}
        </Box>
    );
};

export default BlockchainViz3D;
