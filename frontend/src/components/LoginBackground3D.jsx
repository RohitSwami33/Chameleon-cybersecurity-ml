import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

const LoginBackground3D = () => {
    const mountRef = useRef(null);

    useEffect(() => {
        if (!mountRef.current) return;

        let width = window.innerWidth;
        let height = window.innerHeight;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
        camera.position.z = 50;

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setClearColor(0x050810, 1);
        mountRef.current.appendChild(renderer.domElement);

        // 400 random drifting particles
        const particleGeo = new THREE.BufferGeometry();
        const particleCount = 400;
        const positions = new Float32Array(particleCount * 3);
        const velocities = [];

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 200;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 200;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 100;
            velocities.push(Math.random() * 0.05 + 0.02);
        }

        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particleMat = new THREE.PointsMaterial({
            color: 0x00d4ff,
            size: 0.5,
            transparent: true,
            opacity: 0.6,
        });
        const particles = new THREE.Points(particleGeo, particleMat);
        scene.add(particles);

        // Large icosahedron wireframes
        const icosGroup = new THREE.Group();
        const icosGeo = new THREE.IcosahedronGeometry(15, 1);
        const icosMat = new THREE.MeshBasicMaterial({
            color: 0x7c4dff,
            wireframe: true,
            transparent: true,
            opacity: 0.1
        });

        for (let i = 0; i < 3; i++) {
            const mesh = new THREE.Mesh(icosGeo, icosMat);
            mesh.position.set(
                (Math.random() - 0.5) * 80,
                (Math.random() - 0.5) * 80,
                -30 - Math.random() * 20
            );
            mesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);

            // store random rotation speeds
            mesh.userData = {
                rx: (Math.random() - 0.5) * 0.002,
                ry: (Math.random() - 0.5) * 0.002,
                rz: (Math.random() - 0.5) * 0.002
            };
            icosGroup.add(mesh);
        }
        scene.add(icosGroup);

        let rafId;

        const animate = () => {
            // Particle drift
            const posAttr = particleGeo.attributes.position;
            for (let i = 0; i < particleCount; i++) {
                posAttr.array[i * 3 + 1] += velocities[i];
                // wrap
                if (posAttr.array[i * 3 + 1] > 100) {
                    posAttr.array[i * 3 + 1] = -100;
                }
            }
            posAttr.needsUpdate = true;

            // Icos rotation
            icosGroup.children.forEach(child => {
                child.rotation.x += child.userData.rx;
                child.rotation.y += child.userData.ry;
                child.rotation.z += child.userData.rz;
            });

            renderer.render(scene, camera);
            rafId = requestAnimationFrame(animate);
        };

        animate();

        const handleResize = () => {
            width = window.innerWidth;
            height = window.innerHeight;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        };
        window.addEventListener('resize', handleResize);

        return () => {
            cancelAnimationFrame(rafId);
            window.removeEventListener('resize', handleResize);
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

    return <div ref={mountRef} style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0 }} />;
};

export default LoginBackground3D;
