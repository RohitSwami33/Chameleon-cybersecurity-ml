import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { Box } from '@mui/material';

// EaseOutBack function
const easeOutBack = (x) => {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
};

const LoginShield3D = () => {
    const mountRef = useRef(null);
    const animState = useRef({ startTime: 0, assembled: false, flareOpacity: 0 });

    useEffect(() => {
        if (!mountRef.current) return;

        const width = 120;
        const height = 120;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
        camera.position.z = 8;

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        mountRef.current.appendChild(renderer.domElement);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambientLight);
        const pointLight = new THREE.PointLight(0x00d4ff, 2, 20);
        pointLight.position.set(2, 2, 5);
        scene.add(pointLight);

        // Group to hold the shield fragments
        const shieldGroup = new THREE.Group();
        // Scale down the entire shield to fit 120x120 container properly
        shieldGroup.scale.set(0.85, 0.85, 0.85);
        scene.add(shieldGroup);

        const fragments = [];
        const baseMat = new THREE.MeshStandardMaterial({
            color: 0x0a1628,
            roughness: 0.4,
            metalness: 0.6
        });
        const edgeMat = new THREE.LineBasicMaterial({
            color: 0x00d4ff,
            transparent: true,
            opacity: 0.8
        });

        // Define final shield construction 
        const finalTransforms = [
            { pos: [0, 1.8, 0], rot: [0, 0, 0], scale: [2.5, 1, 1] }, // Top edge
            { pos: [-1.4, 1.2, 0], rot: [0, 0, Math.PI / 6], scale: [1.5, 1, 1] }, // Top left corner
            { pos: [1.4, 1.2, 0], rot: [0, 0, -Math.PI / 6], scale: [1.5, 1, 1] }, // Top right corner
            { pos: [-1.8, -0.2, 0], rot: [0, 0, Math.PI / 2.2], scale: [2.5, 1, 1] }, // Left side
            { pos: [1.8, -0.2, 0], rot: [0, 0, -Math.PI / 2.2], scale: [2.5, 1, 1] }, // Right side
            { pos: [-1.0, -2.2, 0], rot: [0, 0, -Math.PI / 3], scale: [2.6, 1, 1] }, // Bottom left angle
            { pos: [1.0, -2.2, 0], rot: [0, 0, Math.PI / 3], scale: [2.6, 1, 1] }, // Bottom right angle
            { pos: [0, -3.2, 0], rot: [0, 0, Math.PI / 4], scale: [1.2, 1.2, 1] }  // Bottom tip
        ];

        // Generate the fragments
        finalTransforms.forEach(t => {
            const geom = new THREE.PlaneGeometry(1, 1);
            const mesh = new THREE.Mesh(geom, baseMat);

            const edges = new THREE.EdgesGeometry(geom);
            const line = new THREE.LineSegments(edges, edgeMat);
            mesh.add(line);

            // Random start positions
            const startPos = [
                (Math.random() - 0.5) * 10,
                (Math.random() - 0.5) * 10,
                (Math.random() - 0.5) * 10
            ];
            const startRot = [
                Math.random() * Math.PI * 2,
                Math.random() * Math.PI * 2,
                Math.random() * Math.PI * 2
            ];

            mesh.position.set(...startPos);
            mesh.rotation.set(...startRot);
            mesh.scale.set(...t.scale);

            mesh.userData = {
                startPos: new THREE.Vector3(...startPos),
                startRot: new THREE.Vector3(...startRot),
                targetPos: new THREE.Vector3(...t.pos),
                targetRot: new THREE.Vector3(...t.rot),
            };

            shieldGroup.add(mesh);
            fragments.push(mesh);
        });

        // Letter "C" Sprite on the face of the shield
        const canvas = document.createElement('canvas');
        canvas.width = 128;
        canvas.height = 128;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#00d4ff';
        ctx.font = 'bold 80px "IBM Plex Mono", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('C', 64, 64);

        const spriteMat = new THREE.SpriteMaterial({
            map: new THREE.CanvasTexture(canvas),
            transparent: true,
            opacity: 0
        });
        const letterSprite = new THREE.Sprite(spriteMat);
        letterSprite.position.set(0, -0.2, 0.5); // float slightly above
        letterSprite.scale.set(3, 3, 3);
        shieldGroup.add(letterSprite);

        // Flare Sprite
        const flareCanvas = document.createElement('canvas');
        flareCanvas.width = 128;
        flareCanvas.height = 128;
        const flareCtx = flareCanvas.getContext('2d');
        const grad = flareCtx.createRadialGradient(64, 64, 0, 64, 64, 64);
        grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
        grad.addColorStop(0.2, 'rgba(0, 212, 255, 0.8)');
        grad.addColorStop(1, 'rgba(0, 212, 255, 0)');
        flareCtx.fillStyle = grad;
        flareCtx.fillRect(0, 0, 128, 128);

        const flareMat = new THREE.SpriteMaterial({
            map: new THREE.CanvasTexture(flareCanvas),
            transparent: true,
            opacity: 0,
            blending: THREE.AdditiveBlending
        });
        const flareSprite = new THREE.Sprite(flareMat);
        flareSprite.position.set(0, -0.2, 0.6);
        flareSprite.scale.set(8, 8, 8);
        shieldGroup.add(flareSprite);

        let rafId;
        animState.current.startTime = Date.now();

        const animate = () => {
            const now = Date.now();
            const elapsed = (now - animState.current.startTime) / 1000;

            // Assembly animation (0.5s delay, 1.2s duration)
            if (elapsed > 0.5) {
                let progress = (elapsed - 0.5) / 1.2;
                if (progress >= 1.0 && !animState.current.assembled) {
                    progress = 1.0;
                    animState.current.assembled = true;
                    animState.current.flareTime = elapsed; // trigger flare
                } else if (progress > 1.0) {
                    progress = 1.0;
                }

                if (progress <= 1.0) {
                    const eased = progress >= 1.0 ? 1.0 : easeOutBack(progress);

                    fragments.forEach(f => {
                        f.position.lerpVectors(f.userData.startPos, f.userData.targetPos, eased);
                        // Hacky rot lerp
                        f.rotation.x = THREE.MathUtils.lerp(f.userData.startRot.x, f.userData.targetRot.x, eased);
                        f.rotation.y = THREE.MathUtils.lerp(f.userData.startRot.y, f.userData.targetRot.y, eased);
                        f.rotation.z = THREE.MathUtils.lerp(f.userData.startRot.z, f.userData.targetRot.z, eased);
                    });

                    letterSprite.material.opacity = Math.max(0, (progress - 0.5) * 2);
                }
            }

            // Post-assembly float
            if (animState.current.assembled) {
                shieldGroup.position.y = Math.sin(elapsed * 0.8) * 0.2;

                // Flare burst logic
                const flareElapsed = elapsed - animState.current.flareTime;
                if (flareElapsed < 0.5) {
                    // flash up quickly, fade out
                    const flareProg = flareElapsed / 0.5;
                    flareSprite.material.opacity = 1.0 - flareProg; // fades out
                    flareSprite.scale.set(8 + flareProg * 4, 8 + flareProg * 4, 8);
                } else {
                    flareSprite.material.opacity = 0;
                }
            }

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

    return <Box ref={mountRef} sx={{ width: 120, height: 120, margin: '0 auto', mb: 1 }} />;
};

export default LoginShield3D;
