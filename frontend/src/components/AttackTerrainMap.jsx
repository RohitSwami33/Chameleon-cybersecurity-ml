import React, { useRef, useEffect, useState, useMemo } from 'react';
import * as THREE from 'three';
import { Box, Typography, Button, ButtonGroup, Paper } from '@mui/material';

// Dummy data generator
const generateData = () => {
    const data = [];
    const now = new Date();
    for (let i = 0; i < 50; i++) {
        data.push({
            time: new Date(now.getTime() - (49 - i) * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            sqli: Math.pow(Math.random(), 3) * (Math.random() > 0.8 ? 1 : 0.3),
            xss: Math.pow(Math.random(), 2) * (Math.random() > 0.85 ? 0.8 : 0.2),
            ssi: Math.pow(Math.random(), 4) * (Math.random() > 0.9 ? 1 : 0.1),
            benign: Math.random() * 0.4 + 0.6 // Mostly high, so inverted is low
        });
    }
    return data;
};

const AttackTerrainMap = () => {
    const mountRef = useRef(null);
    const containerRef = useRef(null);
    const sceneRefs = useRef({});
    const animState = useRef({ progress: 0, mounted: false });

    const [viewMode, setViewMode] = useState('Solid'); // Solid, Grid, Wireframe
    const [filterCategory, setFilterCategory] = useState('All'); // All, SQLI, XSS, SSI
    const [timeRange, setTimeRange] = useState('1H');
    const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: '' });

    const dataBuffer = useRef(generateData());

    useEffect(() => {
        if (!mountRef.current) return;

        let width = containerRef.current.clientWidth;
        let height = 420;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 200);
        camera.position.set(0, 18, 22);
        camera.lookAt(0, 0, 0);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        mountRef.current.appendChild(renderer.domElement);

        const group = new THREE.Group();
        scene.add(group);

        // Terrain Geometry
        const geometry = new THREE.PlaneGeometry(20, 20, 49, 49);
        geometry.rotateX(-Math.PI / 2);

        const vertexCount = geometry.attributes.position.count;
        geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(vertexCount * 3), 3));

        const terrainMaterial = new THREE.MeshStandardMaterial({
            vertexColors: true,
            metalness: 0.1,
            roughness: 0.6,
            wireframe: false,
            side: THREE.DoubleSide
        });

        const wireframeMaterial = new THREE.MeshBasicMaterial({
            color: 0x00d4ff,
            opacity: 0.08,
            transparent: true,
            wireframe: true
        });

        const terrainMesh = new THREE.Mesh(geometry, terrainMaterial);
        terrainMesh.receiveShadow = true;
        terrainMesh.castShadow = true;
        group.add(terrainMesh);

        const wireframeMesh = new THREE.Mesh(geometry, wireframeMaterial);
        wireframeMesh.position.y += 0.02;
        group.add(wireframeMesh);

        // Highlight Sphere
        const sphereGeom = new THREE.SphereGeometry(0.2, 16, 16);
        const sphereMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const highlightSphere = new THREE.Mesh(sphereGeom, sphereMat);
        highlightSphere.visible = false;
        scene.add(highlightSphere);

        // Target Heights
        const targetHeights = new Float32Array(vertexCount);
        const baseHeights = new Float32Array(vertexCount);

        sceneRefs.current = {
            scene, camera, renderer, geometry, terrainMaterial, wireframeMaterial,
            terrainMesh, wireframeMesh, highlightSphere, targetHeights, baseHeights, group
        };

        // Lighting
        scene.add(new THREE.AmbientLight(0x050810, 0.6));

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 15, 5);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 1024;
        dirLight.shadow.mapSize.height = 1024;
        dirLight.shadow.camera.left = -15;
        dirLight.shadow.camera.right = 15;
        dirLight.shadow.camera.top = 15;
        dirLight.shadow.camera.bottom = -15;
        scene.add(dirLight);

        const redPoint = new THREE.PointLight(0xff3d71, 1.5, 12);
        redPoint.position.set(0, 5, 0); // dynamically moves
        scene.add(redPoint);

        const cyanRim = new THREE.PointLight(0x00d4ff, 0.8, 20);
        cyanRim.position.set(0, 8, -8);
        scene.add(cyanRim);

        const hemiLight = new THREE.HemisphereLight(0x0a1628, 0x050810, 0.3);
        scene.add(hemiLight);

        // Colors
        const colorLow = new THREE.Color('#00d4ff');
        const colorMid = new THREE.Color('#ffab00');
        const colorHigh = new THREE.Color('#ff3d71');
        const colorPeak = new THREE.Color('#ffffff');

        function heightToColor(normalizedHeight) {
            if (normalizedHeight < 0.33) return colorLow.clone().lerp(colorMid, normalizedHeight / 0.33);
            if (normalizedHeight < 0.66) return colorMid.clone().lerp(colorHigh, (normalizedHeight - 0.33) / 0.33);
            return colorHigh.clone().lerp(colorPeak, (normalizedHeight - 0.66) / 0.34);
        }

        sceneRefs.current.updateVertexColors = () => {
            const pos = geometry.attributes.position.array;
            const cols = geometry.attributes.color.array;
            let highestY = -999;
            let peakPos = new THREE.Vector3();

            for (let i = 0; i < vertexCount; i++) {
                const y = Math.max(0, pos[i * 3 + 1]);
                if (y > highestY) {
                    highestY = y;
                    peakPos.set(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]);
                }
                const normalizedHeight = Math.min(1, y / 6);
                const color = heightToColor(normalizedHeight);
                cols[i * 3] = color.r;
                cols[i * 3 + 1] = color.g;
                cols[i * 3 + 2] = color.b;
            }
            geometry.attributes.color.needsUpdate = true;

            // Move red point light to peak
            if (highestY > 1) {
                redPoint.position.lerp(new THREE.Vector3(peakPos.x, peakPos.y + 2, peakPos.z), 0.1);
            }
        };

        // Manual Orbit Controls
        let isDragging = false;
        let prevMouse = { x: 0, y: 0 };
        const spherical = { theta: 0, phi: 0.8, radius: 28 };

        const updateCameraFromSpherical = () => {
            camera.position.x = spherical.radius * Math.sin(spherical.phi) * Math.sin(spherical.theta);
            camera.position.y = spherical.radius * Math.cos(spherical.phi);
            camera.position.z = spherical.radius * Math.sin(spherical.phi) * Math.cos(spherical.theta);
            camera.lookAt(0, 0, 0);
        };
        updateCameraFromSpherical();

        const canvas = renderer.domElement;
        const handlers = {
            mousedown: (e) => { isDragging = true; prevMouse = { x: e.clientX, y: e.clientY }; },
            mouseup: () => { isDragging = false; },
            mousemove: (e) => {
                const rect = canvas.getBoundingClientRect();
                if (isDragging) {
                    spherical.theta -= (e.clientX - prevMouse.x) * 0.005;
                    spherical.phi = Math.max(0.3, Math.min(1.4, spherical.phi + (e.clientY - prevMouse.y) * 0.005));
                    prevMouse = { x: e.clientX, y: e.clientY };
                    updateCameraFromSpherical();
                } else {
                    // Tooltip Raycasting
                    const raycaster = new THREE.Raycaster();
                    const mouse = new THREE.Vector2();
                    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObject(terrainMesh);

                    if (intersects.length > 0) {
                        const { x, z } = intersects[0].point;
                        const timeIndex = Math.min(49, Math.max(0, Math.round((x + 10) / 20 * 49)));
                        const catIndex = Math.min(49, Math.max(0, Math.round((z + 10) / 20 * 49)));

                        const dataSlice = dataBuffer.current[timeIndex];
                        let categoryName = '';
                        let count = 0;
                        if (catIndex <= 12) { categoryName = 'SQLI'; count = dataSlice?.sqli || 0; }
                        else if (catIndex <= 24) { categoryName = 'XSS'; count = dataSlice?.xss || 0; }
                        else if (catIndex <= 36) { categoryName = 'SSI'; count = dataSlice?.ssi || 0; }
                        else { categoryName = 'BENIGN'; count = dataSlice?.benign || 0; }

                        setTooltip({
                            visible: true,
                            x: e.clientX - rect.left,
                            y: e.clientY - rect.top,
                            content: `${dataSlice?.time} — ${categoryName}: ${(count * 100).toFixed(0)} events`
                        });

                        highlightSphere.position.copy(intersects[0].point);
                        highlightSphere.position.y += 0.2;
                        highlightSphere.visible = true;
                        canvas.style.cursor = 'crosshair';
                    } else {
                        setTooltip(prev => ({ ...prev, visible: false }));
                        highlightSphere.visible = false;
                        canvas.style.cursor = 'default';
                    }
                }
            },
            wheel: (e) => {
                spherical.radius = Math.max(15, Math.min(45, spherical.radius + e.deltaY * 0.05));
                updateCameraFromSpherical();
                e.preventDefault();
            }
        };

        canvas.addEventListener('mousedown', handlers.mousedown);
        window.addEventListener('mouseup', handlers.mouseup);
        canvas.addEventListener('mousemove', handlers.mousemove);
        canvas.addEventListener('wheel', handlers.wheel, { passive: false });

        let animFrameId;
        const animate = () => {
            const { positions, targetHeights } = sceneRefs.current;
            const posArray = geometry.attributes.position.array;

            // Initial mount animation
            if (!animState.current.mounted) {
                animState.current.progress += 0.012;
                const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);
                const p = Math.min(1, animState.current.progress);
                const eased = easeOutCubic(p);

                for (let i = 0; i < vertexCount; i++) {
                    posArray[i * 3 + 1] = targetHeights[i] * eased;
                }
                if (animState.current.progress >= 1) {
                    animState.current.mounted = true;
                }
            } else {
                // Live update lerp
                for (let i = 0; i < vertexCount; i++) {
                    posArray[i * 3 + 1] += (targetHeights[i] - posArray[i * 3 + 1]) * 0.04;
                }
            }

            geometry.attributes.position.needsUpdate = true;
            geometry.computeVertexNormals();
            sceneRefs.current.updateVertexColors();

            renderer.render(scene, camera);
            animFrameId = requestAnimationFrame(animate);
        };
        animate();

        const ro = new ResizeObserver(([entry]) => {
            const { width } = entry.contentRect;
            renderer.setSize(width, 420);
            camera.aspect = width / 420;
            camera.updateProjectionMatrix();
        });
        ro.observe(containerRef.current);

        return () => {
            cancelAnimationFrame(animFrameId);
            window.removeEventListener('mouseup', handlers.mouseup);
            canvas.removeEventListener('mousedown', handlers.mousedown);
            canvas.removeEventListener('mousemove', handlers.mousemove);
            canvas.removeEventListener('wheel', handlers.wheel);
            ro.disconnect();
            if (renderer.domElement && renderer.domElement.parentNode) {
                renderer.domElement.parentNode.removeChild(renderer.domElement);
            }
            geometry.dispose();
            terrainMaterial.dispose();
            wireframeMaterial.dispose();
            sphereGeom.dispose();
            sphereMat.dispose();
            renderer.dispose();
        };
    }, []);

    // Live Data & Filter Updates
    useEffect(() => {
        if (!sceneRefs.current.geometry) return;

        const { targetHeights, terrainMaterial, wireframeMesh, terrainMesh } = sceneRefs.current;
        const data = dataBuffer.current;

        // Update view mode
        if (viewMode === 'Grid') {
            terrainMaterial.wireframe = true;
            terrainMaterial.opacity = 0.5;
            terrainMaterial.transparent = true;
            wireframeMesh.visible = false;
        } else if (viewMode === 'Wireframe') {
            terrainMesh.visible = false;
            wireframeMesh.visible = true;
            wireframeMesh.material.opacity = 0.5;
        } else {
            terrainMaterial.wireframe = false;
            terrainMaterial.opacity = 1;
            terrainMaterial.transparent = false;
            terrainMesh.visible = true;
            wireframeMesh.visible = true;
            wireframeMesh.material.opacity = 0.08;
        }

        const getIntensity = (timeSlice, zIndex) => {
            let base = 0;
            let cat = '';
            if (zIndex <= 12) { base = timeSlice.sqli; cat = 'SQLI'; }
            else if (zIndex <= 24) { base = timeSlice.xss; cat = 'XSS'; }
            else if (zIndex <= 36) { base = timeSlice.ssi; cat = 'SSI'; }
            else { base = 1.0 - timeSlice.benign; cat = 'BENIGN'; }

            if (filterCategory !== 'All' && filterCategory !== cat) {
                return 0; // Filtered out
            }

            const noise = Math.sin(zIndex * 0.5) * 0.05 + Math.cos(zIndex * timeSlice.sqli) * 0.05;
            return Math.max(0, Math.min(1, base + noise));
        };

        for (let i = 0; i < 50; i++) {
            for (let j = 0; j < 50; j++) {
                const vertexIndex = (i * 50 + j);
                const timeSlice = data[i] || {};
                const intensity = getIntensity(timeSlice, j);
                targetHeights[vertexIndex] = intensity * 6;
            }
        }

    }, [viewMode, filterCategory, timeRange]);

    // Live update simulator
    useEffect(() => {
        const interval = setInterval(() => {
            // Shift data
            const newData = {
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                sqli: Math.pow(Math.random(), 3) * (Math.random() > 0.8 ? 1 : 0.2),
                xss: Math.pow(Math.random(), 2) * (Math.random() > 0.85 ? 0.8 : 0.1),
                ssi: Math.pow(Math.random(), 4) * (Math.random() > 0.9 ? 1 : 0.1),
                benign: Math.random() * 0.4 + 0.6
            };
            dataBuffer.current.shift();
            dataBuffer.current.push(newData);

            // Re-trigger height update
            setFilterCategory(prev => prev); // dummy trigger
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <Paper elevation={0} sx={{
            position: 'relative', width: '100%', height: 420, overflow: 'hidden',
            bgcolor: 'rgba(8, 14, 28, 0.4)', borderRadius: '12px', border: '1px solid rgba(0, 212, 255, 0.1)', mb: 3
        }}>
            <Box ref={containerRef} sx={{ position: 'absolute', inset: 0 }}>
                <Box ref={mountRef} sx={{ width: '100%', height: '100%', outline: 'none' }} />
            </Box>

            {/* Overlays */}

            {/* Top Right Controls */}
            <Box sx={{ position: 'absolute', top: 16, right: 16, display: 'flex', flexDirection: 'column', gap: 1, zIndex: 10 }}>
                <ButtonGroup size="small" variant="outlined" sx={{ '& .MuiButton-root': { borderColor: 'rgba(0, 212, 255, 0.2)', color: '#7a9bbf', fontSize: '10px' } }}>
                    {['1H', '6H', '24H', '7D'].map(val => (
                        <Button key={val} onClick={() => setTimeRange(val)} sx={{ bgcolor: timeRange === val ? 'rgba(0, 212, 255, 0.1) !important' : 'transparent', color: timeRange === val ? '#00d4ff !important' : '#7a9bbf' }}>{val}</Button>
                    ))}
                </ButtonGroup>

                <ButtonGroup size="small" variant="outlined" sx={{ '& .MuiButton-root': { borderColor: 'rgba(124, 77, 255, 0.2)', color: '#7a9bbf', fontSize: '10px' } }}>
                    {['Solid', 'Grid', 'Wireframe'].map(val => (
                        <Button key={val} onClick={() => setViewMode(val)} sx={{ bgcolor: viewMode === val ? 'rgba(124, 77, 255, 0.1) !important' : 'transparent', color: viewMode === val ? '#7c4dff !important' : '#7a9bbf' }}>{val}</Button>
                    ))}
                </ButtonGroup>

                <ButtonGroup size="small" variant="outlined" sx={{ '& .MuiButton-root': { borderColor: 'rgba(255, 171, 0, 0.2)', color: '#7a9bbf', fontSize: '10px' } }}>
                    {['All', 'SQLI', 'XSS', 'SSI'].map(val => (
                        <Button key={val} onClick={() => setFilterCategory(val)} sx={{ bgcolor: filterCategory === val ? 'rgba(255, 171, 0, 0.1) !important' : 'transparent', color: filterCategory === val ? '#ffab00 !important' : '#7a9bbf' }}>{val}</Button>
                    ))}
                </ButtonGroup>
            </Box>

            {/* Legend */}
            <Paper elevation={0} sx={{
                position: 'absolute', top: 16, left: 16, p: 1.5,
                bgcolor: 'rgba(5, 8, 16, 0.7)', backdropFilter: 'blur(8px)',
                border: '1px solid rgba(0, 212, 255, 0.1)', borderRadius: '8px'
            }}>
                <Typography variant="caption" sx={{ color: '#e8f4fd', fontWeight: 600, display: 'block', mb: 1, fontSize: '10px', textTransform: 'uppercase', letterSpacing: 1 }}>
                    Threat Intensity
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 80, height: 6, background: 'linear-gradient(90deg, #00d4ff, #ffab00, #ff3d71, #ffffff)', borderRadius: '3px' }} />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                    <Typography variant="caption" sx={{ color: '#00d4ff', fontSize: '9px' }}>Low</Typography>
                    <Typography variant="caption" sx={{ color: '#ffffff', fontSize: '9px' }}>Peak</Typography>
                </Box>
            </Paper>

            {/* Category Labels (Left Edge) */}
            <Box sx={{ position: 'absolute', bottom: 40, left: 16, display: 'flex', flexDirection: 'column-reverse', height: '60%', justifyContent: 'space-between', pointerEvents: 'none' }}>
                <Typography variant="caption" sx={{ color: '#00d4ff', fontSize: '10px', fontWeight: 600 }}>SQLI</Typography>
                <Typography variant="caption" sx={{ color: '#7c4dff', fontSize: '10px', fontWeight: 600 }}>XSS</Typography>
                <Typography variant="caption" sx={{ color: '#ffab00', fontSize: '10px', fontWeight: 600 }}>SSI</Typography>
                <Typography variant="caption" sx={{ color: '#7a9bbf', fontSize: '10px', fontWeight: 600 }}>BENIGN</Typography>
            </Box>

            {/* Time Labels (Bottom Edge) */}
            <Box sx={{ position: 'absolute', bottom: 8, left: 60, right: 60, display: 'flex', justifyContent: 'space-between', pointerEvents: 'none' }}>
                <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '10px', fontFamily: '"IBM Plex Mono", monospace' }}>T-50</Typography>
                <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '10px', fontFamily: '"IBM Plex Mono", monospace' }}>T-25</Typography>
                <Typography variant="caption" sx={{ color: '#3d5a7a', fontSize: '10px', fontFamily: '"IBM Plex Mono", monospace' }}>NOW</Typography>
            </Box>

            {/* Tooltip */}
            {tooltip.visible && (
                <Paper sx={{
                    position: 'absolute', top: tooltip.y - 40, left: tooltip.x + 15,
                    p: 1, bgcolor: 'rgba(8, 14, 28, 0.9)', backdropFilter: 'blur(8px)',
                    border: '1px solid #ff3d71', borderRadius: '4px', pointerEvents: 'none', zIndex: 20
                }}>
                    <Typography sx={{ color: '#e8f4fd', fontSize: '11px', fontFamily: '"IBM Plex Mono", monospace' }}>
                        {tooltip.content}
                    </Typography>
                </Paper>
            )}
        </Paper>
    );
};

export default AttackTerrainMap;
