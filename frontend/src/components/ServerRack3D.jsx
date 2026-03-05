import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { Box, Typography, Paper } from '@mui/material';

const unitsData = [
    { id: 0, y: 2.4, name: "DECEPTION ENGINE", metrics: { status: 'Active', load: 0.3 } },
    { id: 1, y: 1.2, name: "BLOCKCHAIN NODE", metrics: { status: 'Synced', load: 0.1 } },
    { id: 2, y: 0.0, name: "TARPIT SYSTEM", metrics: { status: 'Engaged', load: 0.6 } },
    { id: 3, y: -1.2, name: "API GATEWAY", metrics: { status: 'Active', load: 0.4 } },
    { id: 4, y: -2.4, name: "LOG PROCESSOR", metrics: { status: 'Active', load: 0.2 } },
];

const ServerRack3D = () => {
    const mountRef = useRef(null);
    const sceneRefs = useRef({});
    const animState = useRef({
        mounted: false,
        time: 0,
        blinkLEDs: [], // Array of functions to tick
        hoveredUnit: null,
        errorUnit: null // ID of unit in error state
    });

    const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: null });

    useEffect(() => {
        if (!mountRef.current) return;

        const width = 350;
        const height = 380;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(35, width / height, 0.1, 100);
        camera.position.set(4, 3, 10);
        camera.lookAt(0, 0, 0);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        mountRef.current.appendChild(renderer.domElement);

        const group = new THREE.Group();
        group.position.y = -5; // For entry animation
        scene.add(group);

        // Rack Chassis
        const rackGroup = new THREE.Group();
        group.add(rackGroup);

        const chassisGeom = new THREE.BoxGeometry(3, 7, 2);
        const chassisMat = new THREE.MeshStandardMaterial({
            color: 0x3d5a80,
            metalness: 0.3, roughness: 0.7,
            emissive: 0x000000
        });
        const chassis = new THREE.Mesh(chassisGeom, chassisMat);
        rackGroup.add(chassis);

        const cutoutGeom = new THREE.BoxGeometry(2.7, 6.7, 0.05);
        const cutoutMat = new THREE.MeshStandardMaterial({ color: 0x293241, metalness: 0.4, roughness: 0.8 });
        const cutout = new THREE.Mesh(cutoutGeom, cutoutMat);
        cutout.position.z = 1.05;
        rackGroup.add(cutout);

        const railGeom = new THREE.BoxGeometry(0.08, 7, 0.3);
        const railMat = new THREE.MeshStandardMaterial({ color: 0x98c1d9, metalness: 0.5, roughness: 0.5 });
        const railL = new THREE.Mesh(railGeom, railMat);
        railL.position.set(-1.3, 0, 1.0);
        rackGroup.add(railL);
        const railR = new THREE.Mesh(railGeom, railMat);
        railR.position.set(1.3, 0, 1.0);
        rackGroup.add(railR);

        // Server Units
        const units = [];
        const fillBars = [];

        const unitGeom = new THREE.BoxGeometry(2.6, 0.9, 1.7);
        const unitFaceGeom = new THREE.BoxGeometry(2.6, 0.9, 0.05);
        const ledGeom = new THREE.SphereGeometry(0.06, 8, 8);
        const trackGeom = new THREE.BoxGeometry(0.8, 0.06, 0.02);
        const fillGeom = new THREE.BoxGeometry(1.0, 0.06, 0.025); // Normalize to 1.0 for scaleX

        unitsData.forEach((data, index) => {
            const unitGroup = new THREE.Group();
            unitGroup.position.set(-3, data.y, 0.15); // x=-3 for entry animation
            unitGroup.userData = { id: data.id, targetX: 0, index };
            group.add(unitGroup);

            const bodyMat = new THREE.MeshStandardMaterial({ color: 0x3d5a80, metalness: 0.3, roughness: 0.7, emissive: 0x000000 });
            const body = new THREE.Mesh(unitGeom, bodyMat);
            unitGroup.add(body);

            const faceMat = new THREE.MeshStandardMaterial({ color: 0x293241, metalness: 0.4, roughness: 0.8 });
            const face = new THREE.Mesh(unitFaceGeom, faceMat);
            face.position.z = 0.88;
            unitGroup.add(face);

            units.push({ id: data.id, group: unitGroup, body, face, data, index, leds: [] });

            // LEDs
            const ledTypes = ['power', 'activity', 'status'];
            ledTypes.forEach((type, ledIdx) => {
                const ledMat = new THREE.MeshStandardMaterial({
                    color: 0x111827, emissive: 0x000000, emissiveIntensity: 0
                });
                const led = new THREE.Mesh(ledGeom, ledMat);
                led.position.set(-1.0 + (ledIdx * 0.3), 0, 0.92);
                unitGroup.add(led);

                const light = new THREE.PointLight(0xffffff, 0, 0.8);
                light.position.copy(led.position);
                unitGroup.add(light);

                units[index].leds.push({ mesh: led, light, type });
            });

            // Activity Bars
            const track = new THREE.Mesh(trackGeom, new THREE.MeshBasicMaterial({ color: 0x050810 }));
            track.position.set(0.3, -0.2, 0.92);
            unitGroup.add(track);

            const loadColor = data.metrics.load >= 0.8 ? 0xff3d71 : (data.metrics.load >= 0.5 ? 0xffab00 : 0x00e676);
            const fillMat = new THREE.MeshBasicMaterial({ color: loadColor });
            const fill = new THREE.Mesh(fillGeom, fillMat);
            fill.scale.x = 0; // Starts at 0
            fill.position.set(0.3, -0.2, 0.925);
            unitGroup.add(fill);

            fillBars.push({ mesh: fill, targetScale: data.metrics.load, currentScale: 0, mat: fillMat });

            // Error alert light (starts hidden)
            const alertLight = new THREE.PointLight(0xff3d71, 0, 5);
            alertLight.position.set(0, 0, 1.5);
            unitGroup.add(alertLight);
            units[index].alertLight = alertLight;
        });

        sceneRefs.current = {
            scene, camera, renderer, group, units, fillBars
        };

        // Lighting
        scene.add(new THREE.AmbientLight(0xffffff, 1.2));

        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444455, 1.0);
        hemiLight.position.set(0, 10, 0);
        scene.add(hemiLight);

        const spotLight = new THREE.SpotLight(0xffffff, 2.5, 30, Math.PI / 4, 0.5, 1);
        spotLight.position.set(2, 12, 8);
        scene.add(spotLight);

        const pointLightL = new THREE.PointLight(0x00d4ff, 1.5, 20);
        pointLightL.position.set(-6, 4, 6);
        scene.add(pointLightL);

        const pointLightR = new THREE.PointLight(0x7c4dff, 1.2, 20);
        pointLightR.position.set(6, 2, 4);
        scene.add(pointLightR);

        // Blinking Logic setup
        const setLed = (unitIdx, ledType, colorHex, active = true) => {
            const ledObj = units[unitIdx].leds.find(l => l.type === ledType);
            if (!ledObj) return;
            const c = new THREE.Color(colorHex);
            ledObj.mesh.material.color.copy(c);
            ledObj.mesh.material.emissive.copy(c);
            ledObj.light.color.copy(c);
            ledObj.mesh.material.emissiveIntensity = active ? 3.0 : 0.1;
            ledObj.light.intensity = active ? 0.3 : 0;
            ledObj.baseColor = colorHex;
        };

        const createBlink = (unitIdx, ledType, colorHex, intervalMs) => {
            let lastTick = 0;
            let on = false;
            animState.current.blinkLEDs.push((time) => {
                if (time - lastTick > intervalMs) {
                    on = !on;
                    setLed(unitIdx, ledType, colorHex, on);
                    lastTick = time;
                }
            });
        };

        // Boot-up configuration
        units.forEach((u, i) => {
            // Delay boot
            setTimeout(() => {
                setLed(i, 'power', 0x00e676, true);

                setTimeout(() => {
                    // Activity
                    if (i === 0) createBlink(i, 'activity', 0x00d4ff, 200 + Math.random() * 500);
                    if (i === 1) createBlink(i, 'activity', 0x00d4ff, 2000);
                    if (i === 2) createBlink(i, 'activity', 0xffab00, 500 + Math.random() * 2500);
                    if (i === 3) createBlink(i, 'activity', 0x00d4ff, 50 + Math.random() * 200);
                    if (i === 4) createBlink(i, 'activity', 0x00e676, 500);

                    setTimeout(() => {
                        // Status
                        setLed(i, 'status', 0x00e676, true);
                    }, 400);
                }, 200);
            }, 800 + (i * 150)); // Base delay + stagger
        });

        // Raycasting
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const canvas = renderer.domElement;

        const onMouseMove = (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const bodies = units.map(u => u.body);
            const intersects = raycaster.intersectObjects(bodies);

            if (intersects.length > 0) {
                const u = units.find(unit => unit.body === intersects[0].object);
                if (u) {
                    animState.current.hoveredUnit = u.id;
                    setTooltip({
                        visible: true,
                        x: e.clientX - rect.left,
                        y: e.clientY - rect.top,
                        content: u.data
                    });
                    canvas.style.cursor = 'pointer';
                }
            } else {
                animState.current.hoveredUnit = null;
                setTooltip(prev => ({ ...prev, visible: false }));
                canvas.style.cursor = 'default';
            }
        };
        canvas.addEventListener('mousemove', onMouseMove);

        // Animation Loop
        let animFrameId;
        const clock = new THREE.Clock();

        const animate = () => {
            const time = clock.getElapsedTime() * 1000;
            const delta = clock.getDelta();

            // Entry Animation
            if (!animState.current.mounted) {
                group.position.y += (0 - group.position.y) * 0.08;

                units.forEach((u) => {
                    u.group.position.x += (u.group.userData.targetX - u.group.position.x) * 0.1;
                });

                if (Math.abs(group.position.y) < 0.01) animState.current.mounted = true;
            }

            // Rocking Animation
            let rotBase = Math.sin(time * 0.0004) * 0.15;
            if (animState.current.errorUnit !== null) {
                rotBase += Math.sin(time * 0.02) * 0.05; // Shake
            }
            group.rotation.y = rotBase;

            // Hover & Error Effects
            units.forEach((u) => {
                const isHovered = animState.current.hoveredUnit === u.id;
                const isError = animState.current.errorUnit === u.id;

                let targetEmissive = 0;
                let emhex = 0x000000;

                if (isError) {
                    targetEmissive = (Math.sin(time * 0.008) > 0) ? 0.5 : 0;
                    emhex = 0xff3d71;
                    u.alertLight.intensity = targetEmissive * 2;
                } else if (isHovered) {
                    targetEmissive = 0.3;
                    emhex = 0x0d2040;
                } else {
                    u.alertLight.intensity = 0;
                }

                u.body.material.emissive.setHex(emhex);
                u.body.material.emissiveIntensity += (targetEmissive - u.body.material.emissiveIntensity) * 0.1;

                u.leds.forEach(led => {
                    if (isHovered && !isError) {
                        if (led.mesh.material.emissiveIntensity > 0) led.mesh.material.emissiveIntensity = 4.0;
                    }
                    if (isError) {
                        setLed(u.index, led.type, 0xff3d71, true);
                    } else if (animState.current.errorUnit === null && u.wasError) {
                        setLed(u.index, led.type, led.baseColor, true);
                    }
                });

                u.wasError = isError;
            });

            // Activity Bars Interpolation
            if (animState.current.mounted) {
                fillBars.forEach(fb => {
                    fb.currentScale += (fb.targetScale - fb.currentScale) * 0.05;
                    const sc = Math.max(0.001, fb.currentScale);
                    fb.mesh.scale.x = sc * 0.8;
                    fb.mesh.position.x = 0.3 - (0.8 / 2) + (sc * 0.8 / 2); // left aligned
                });
            }

            // Process Blinks
            if (animState.current.errorUnit === null) {
                animState.current.blinkLEDs.forEach(f => f(time));
            }

            renderer.render(scene, camera);
            animFrameId = requestAnimationFrame(animate);
        };
        animate();

        return () => {
            cancelAnimationFrame(animFrameId);
            canvas.removeEventListener('mousemove', onMouseMove);
            if (renderer.domElement && renderer.domElement.parentNode) {
                renderer.domElement.parentNode.removeChild(renderer.domElement);
            }
            scene.traverse(obj => {
                if (obj.isMesh) {
                    if (obj.geometry) obj.geometry.dispose();
                    if (obj.material) {
                        if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
                        else obj.material.dispose();
                    }
                }
            });
            renderer.dispose();
        };
    }, []);

    // Random Load Simulation
    useEffect(() => {
        const interval = setInterval(() => {
            if (sceneRefs.current.fillBars) {
                sceneRefs.current.fillBars.forEach((fb, i) => {
                    fb.targetScale = Math.max(0.1, Math.min(1.0, fb.targetScale + (Math.random() - 0.5) * 0.2));
                    const loadColor = fb.targetScale >= 0.8 ? 0xff3d71 : (fb.targetScale >= 0.5 ? 0xffab00 : 0x00e676);
                    fb.mat.color.setHex(loadColor);

                    // Update React State backing it
                    unitsData[i].metrics.load = fb.targetScale;
                });
            }
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    const toScreenPos = (position3D, camera, w, h) => {
        const vec = position3D.clone().project(camera);
        return {
            x: (vec.x + 1) / 2 * w,
            y: (-vec.y + 1) / 2 * h
        };
    };

    const [screenLabels, setScreenLabels] = useState([]);

    // Update Label positions less frequently
    useEffect(() => {
        const interval = setInterval(() => {
            if (sceneRefs.current.units && sceneRefs.current.camera) {
                const labels = sceneRefs.current.units.map(u => {
                    // Position at front right corner of the unit body
                    const pos = u.group.position.clone();
                    pos.x += 1.8;
                    pos.y += 0;
                    pos.z += 0;

                    // Apply group rotation
                    pos.applyMatrix4(sceneRefs.current.group.matrixWorld);

                    return {
                        id: u.id,
                        data: u.data,
                        pos2D: toScreenPos(pos, sceneRefs.current.camera, 350, 380)
                    };
                });
                setScreenLabels(labels);
            }
        }, 100);
        return () => clearInterval(interval);
    }, []);


    return (
        <Box sx={{ position: 'relative', width: 350, height: 380 }}>
            <Box ref={mountRef} sx={{ width: '100%', height: '100%' }} />

            {/* HTML Overlays for Labels */}
            {screenLabels.map((lbl, i) => (
                <Box key={i} sx={{
                    position: 'absolute',
                    left: lbl.pos2D.x + 5,
                    top: lbl.pos2D.y - 12,
                    pointerEvents: 'none',
                    display: 'flex',
                    flexDirection: 'column',
                    opacity: 0.8,
                    transform: 'translateY(-50%)' // Center vertically to node
                }}>
                    <Typography sx={{ color: '#ffffff', fontSize: '10px', fontWeight: 'bold', fontFamily: '"IBM Plex Mono", monospace', whiteSpace: 'nowrap' }}>
                        {lbl.data.name}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Typography sx={{ color: lbl.data.metrics.status === 'Active' || lbl.data.metrics.status === 'Synced' || lbl.data.metrics.status === 'Engaged' ? '#00e676' : '#ffab00', fontSize: '9px', fontFamily: '"IBM Plex Mono", monospace', whiteSpace: 'nowrap' }}>
                            {lbl.data.metrics.status}
                        </Typography>
                        <Typography sx={{ color: '#7a9bbf', fontSize: '9px', fontFamily: '"IBM Plex Mono", monospace', whiteSpace: 'nowrap' }}>
                            {(lbl.data.metrics.load * 100).toFixed(0)}%
                        </Typography>
                    </Box>
                </Box>
            ))}

            {/* Hover Tooltip */}
            {tooltip.visible && tooltip.content && (
                <Paper sx={{
                    position: 'fixed',
                    left: tooltip.x + 16,
                    top: tooltip.y + 16,
                    p: 1.5,
                    bgcolor: 'rgba(8, 14, 28, 0.9)',
                    backdropFilter: 'blur(8px)',
                    border: '1px solid #00d4ff',
                    borderRadius: '6px',
                    pointerEvents: 'none',
                    zIndex: 20,
                    minWidth: 200
                }}>
                    <Typography sx={{ color: '#00d4ff', fontSize: '11px', fontWeight: 'bold', fontFamily: '"IBM Plex Mono", monospace', mb: 1 }}>
                        ⬛ {tooltip.content.name}
                    </Typography>
                    <Typography sx={{ color: '#e8f4fd', fontSize: '10px', fontFamily: '"IBM Plex Mono", monospace' }}>
                        Status: <span style={{ color: '#00e676' }}>{tooltip.content.metrics.status}</span>
                    </Typography>
                    <Typography sx={{ color: '#e8f4fd', fontSize: '10px', fontFamily: '"IBM Plex Mono", monospace' }}>
                        CPU Load: {(tooltip.content.metrics.load * 100).toFixed(1)}%
                    </Typography>
                </Paper>
            )}

            {/* Simulated Error Alert Banner */}
            {animState.current.errorUnit !== null && (
                <Box sx={{
                    position: 'absolute', top: 10, left: '50%', transform: 'translateX(-50%)',
                    bgcolor: 'rgba(255, 61, 113, 0.2)', border: '1px solid #ff3d71', borderRadius: '4px', px: 2, py: 0.5,
                    display: 'flex', alignItems: 'center', gap: 1
                }}>
                    <Typography sx={{ color: '#ff3d71', fontSize: '10px', fontWeight: 'bold', fontFamily: '"IBM Plex Mono", monospace' }}>
                        ⚠ UNIT FAILURE
                    </Typography>
                </Box>
            )}
        </Box>
    );
};

export default ServerRack3D;
