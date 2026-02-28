import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { Box, Typography } from '@mui/material';

const AIOrb3D = ({ state = 'IDLE' }) => {
    const mountRef = useRef(null);
    const animationData = useRef({ time: 0, speakingIntensity: 0 });

    useEffect(() => {
        if (!mountRef.current) return;

        const width = 120;
        const height = 120;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
        camera.position.z = 5;

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        mountRef.current.appendChild(renderer.domElement);

        // Core Icosahedron
        const coreGeometry = new THREE.IcosahedronGeometry(1.0, 4);
        // Store original positions for deformation
        coreGeometry.userData.originalPositions = new Float32Array(coreGeometry.attributes.position.array);

        const coreMaterial = new THREE.MeshStandardMaterial({
            color: 0x050810,
            wireframe: false,
            emissive: 0x7c4dff,
            emissiveIntensity: 0.6,
            metalness: 0.8,
            roughness: 0.1
        });
        const coreMesh = new THREE.Mesh(coreGeometry, coreMaterial);
        scene.add(coreMesh);

        // Outer Wireframe Shell
        const shellGeometry = new THREE.IcosahedronGeometry(1.15, 1);
        const shellMaterial = new THREE.MeshBasicMaterial({
            color: 0x00d4ff,
            wireframe: true,
            transparent: true,
            opacity: 0.3
        });
        const shellMesh = new THREE.Mesh(shellGeometry, shellMaterial);
        scene.add(shellMesh);

        // Ambient light helps standard material
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const pointLight = new THREE.PointLight(0xffffff, 1);
        pointLight.position.set(5, 5, 5);
        scene.add(pointLight);

        // Halo Sprite
        const canvas = document.createElement('canvas');
        canvas.width = 128;
        canvas.height = 128;
        const context = canvas.getContext('2d');
        const gradient = context.createRadialGradient(64, 64, 0, 64, 64, 64);
        gradient.addColorStop(0, 'rgba(255,255,255,1)');
        gradient.addColorStop(1, 'rgba(255,255,255,0)');
        context.fillStyle = gradient;
        context.fillRect(0, 0, 128, 128);

        const spriteMaterial = new THREE.SpriteMaterial({
            map: new THREE.CanvasTexture(canvas),
            transparent: true,
            opacity: 0.5,
            color: 0x7c4dff,
            blending: THREE.AdditiveBlending
        });
        const haloSprite = new THREE.Sprite(spriteMaterial);
        haloSprite.scale.set(3, 3, 3);
        scene.add(haloSprite);

        let rafId;

        const animate = () => {
            const t = animationData.current.time;
            animationData.current.time += 0.016;

            const currentState = mountRef.current?.getAttribute('data-state') || 'IDLE';

            // Base configurations
            let rotSpeed = 0.003;
            let targetEmissive = 0x7c4dff;
            let targetHaloColor = 0x7c4dff;
            let targetHaloScale = 2.5; // (idle=0.8 relative to whatever scalar we want, let's use 2.5, 3.5, 4.5)
            let coreScale = 1 + Math.sin(t * 0.8) * 0.03;
            let shellOpacity = 0.3;
            let speakingTarget = 0;

            if (currentState === 'THINKING') {
                rotSpeed = 0.015;
                targetEmissive = 0x00d4ff; // Cyan
                targetHaloColor = 0x00d4ff;
                targetHaloScale = 3.5;
                shellOpacity = 0.1 + (Math.sin(t * 5) * 0.5 + 0.5) * 0.5; // oscillate 0.1 to 0.6
                coreScale = 1;
            } else if (currentState === 'SPEAKING') {
                rotSpeed = 0.005;
                targetEmissive = 0x00e676; // Green
                targetHaloColor = 0x00e676;
                targetHaloScale = 4.5;
                speakingTarget = 1.0;
                coreScale = 1;
            } else if (currentState === 'ERROR') {
                rotSpeed = 0.01;
                targetHaloColor = 0xff3d71;
                targetHaloScale = 3.0;
                coreScale = 1;
                // Flash emissive red
                if (Math.floor(t * 10) % 2 === 0) {
                    targetEmissive = 0xff3d71;
                } else {
                    targetEmissive = 0x440000;
                }
                // Quick jitter
                coreMesh.position.x = (Math.random() - 0.5) * 0.1;
                coreMesh.position.y = (Math.random() - 0.5) * 0.1;
            } else {
                // IDLE
                coreMesh.position.set(0, 0, 0);
            }

            // Smoothly interpolate speaking intensity
            animationData.current.speakingIntensity += (speakingTarget - animationData.current.speakingIntensity) * 0.1;

            // Apply speaking displacement
            const positions = coreGeometry.attributes.position.array;
            const originalPositions = coreGeometry.userData.originalPositions;
            const intensity = animationData.current.speakingIntensity;

            for (let i = 0; i < positions.length; i += 3) {
                if (intensity > 0.01) {
                    const noise = (Math.random() - 0.5) * 0.08 * intensity;
                    positions[i] = originalPositions[i] + noise;
                    positions[i + 1] = originalPositions[i + 1] + noise;
                    positions[i + 2] = originalPositions[i + 2] + noise;
                } else {
                    positions[i] = originalPositions[i];
                    positions[i + 1] = originalPositions[i + 1];
                    positions[i + 2] = originalPositions[i + 2];
                }
            }
            coreGeometry.attributes.position.needsUpdate = true;

            // Rotations
            coreMesh.rotation.y += rotSpeed;
            coreMesh.rotation.x += rotSpeed * 0.5;
            shellMesh.rotation.y += rotSpeed * 1.2;
            shellMesh.rotation.z -= rotSpeed * 0.8;

            coreMesh.scale.setScalar(coreScale);

            // Interpolate colors and scales
            const currentEmissive = new THREE.Color(coreMaterial.emissive.getHex());
            currentEmissive.lerp(new THREE.Color(targetEmissive), 0.1);
            coreMaterial.emissive.copy(currentEmissive);

            const currentHalo = new THREE.Color(haloSprite.material.color.getHex());
            currentHalo.lerp(new THREE.Color(targetHaloColor), 0.1);
            haloSprite.material.color.copy(currentHalo);

            haloSprite.scale.lerp(new THREE.Vector3(targetHaloScale, targetHaloScale, targetHaloScale), 0.1);
            shellMaterial.opacity += (shellOpacity - shellMaterial.opacity) * 0.1;

            renderer.render(scene, camera);
            rafId = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            cancelAnimationFrame(rafId);
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
    }, []);

    // Helper text mapping
    let label = 'Ready';
    if (state === 'THINKING') label = 'Analyzing...';
    if (state === 'SPEAKING') label = 'Responding...';
    if (state === 'ERROR') label = 'System Error';

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 2, mt: 2 }}>
            <Box
                ref={mountRef}
                data-state={state}
                sx={{ width: 120, height: 120 }}
            />
            <Typography sx={{
                fontFamily: '"IBM Plex Mono", monospace',
                fontSize: '0.65rem',
                color: state === 'ERROR' ? '#ff3d71' : '#7a9bbf',
                mt: 0.5,
                textTransform: 'uppercase',
                letterSpacing: 1
            }}>
                {label}
            </Typography>
        </Box>
    );
};

export default AIOrb3D;
