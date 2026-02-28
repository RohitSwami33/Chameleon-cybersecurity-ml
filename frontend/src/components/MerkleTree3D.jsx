import React, { useRef, useEffect, useState, useCallback } from 'react';
import * as THREE from 'three';
import { Box, Typography, Paper } from '@mui/material';

const createHaloTexture = (colorHex) => {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createRadialGradient(64, 64, 0, 64, 64, 64);
    grad.addColorStop(0, colorHex);
    grad.addColorStop(1, 'transparent');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 128, 128);
    return new THREE.CanvasTexture(canvas);
};

const MerkleTree3D = ({ lastUpdated, recordsCount = 0 }) => {
    const mountRef = useRef(null);
    const containerRef = useRef(null);
    const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, nodeId: null });
    const animState = useRef({ time: 0, verifying: false });
    const sceneRefs = useRef({});

    useEffect(() => {
        if (!mountRef.current) return;

        // WebGL Fallback check
        try {
            const canvas = document.createElement('canvas');
            if (!window.WebGLRenderingContext || (!canvas.getContext('webgl') && !canvas.getContext('experimental-webgl'))) {
                // Return simple fallback inside mountRef later if we handled it in render, but for now we expect webgl
            }
        } catch (e) {
            console.warn("WebGL not supported");
        }

        let width = containerRef.current.clientWidth;
        let height = 340;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
        camera.position.set(0, 2, 10);
        camera.lookAt(0, 0, 0);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);
        mountRef.current.appendChild(renderer.domElement);

        const group = new THREE.Group();
        scene.add(group);

        const nodes = [];
        const edges = [];
        const edgeTo = {}; // map nodeId to edge object arriving at it

        const nodeDefs = [
            { id: 0, pos: [0, 3, 0], type: 'root', parent: null },
            { id: 1, pos: [-2.5, 1, 0], type: 'branch', parent: 0 },
            { id: 2, pos: [2.5, 1, 0], type: 'branch', parent: 0 },
            { id: 3, pos: [-3.8, -1.2, 0], type: 'leaf', parent: 1 },
            { id: 4, pos: [-1.2, -1.2, 0], type: 'leaf', parent: 1 },
            { id: 5, pos: [1.2, -1.2, 0], type: 'leaf', parent: 2 },
            { id: 6, pos: [3.8, -1.2, 0], type: 'leaf', parent: 2 }
        ];

        // Textures
        const haloRootTex = createHaloTexture('rgba(0, 212, 255, 1)');
        const haloBranchTex = createHaloTexture('rgba(124, 77, 255, 1)');
        const haloLeafTex = createHaloTexture('rgba(0, 212, 255, 1)');

        nodeDefs.forEach(def => {
            const isRoot = def.type === 'root';
            const isBranch = def.type === 'branch';

            const geom = new THREE.SphereGeometry(isRoot ? 0.5 : 0.35, 32, 32);
            let mat;

            if (isRoot) {
                mat = new THREE.MeshStandardMaterial({
                    color: 0x00d4ff, emissive: 0x00d4ff, emissiveIntensity: 0.8,
                    metalness: 0.3, roughness: 0.1
                });
            } else if (isBranch) {
                mat = new THREE.MeshStandardMaterial({
                    color: 0x7c4dff, emissive: 0x7c4dff, emissiveIntensity: 0.5,
                    metalness: 0.5, roughness: 0.4
                });
            } else {
                mat = new THREE.MeshStandardMaterial({
                    color: 0x0a1628, emissive: 0x00d4ff, emissiveIntensity: 0.2,
                    metalness: 0.8, roughness: 0.1
                });
            }

            const mesh = new THREE.Mesh(geom, mat);
            mesh.position.set(...def.pos);
            mesh.userData = {
                id: def.id, type: def.type, parent: def.parent,
                baseScale: 1, baseEmissive: mat.emissiveIntensity,
                isHovered: false, isVerified: false,
                baseColor: mat.color.clone(),
                targetEmissive: mat.emissiveIntensity,
                targetScale: 1
            };
            group.add(mesh);
            nodes.push(mesh);

            // Halo Sprite
            let haloTex, haloSize, haloOp;
            if (isRoot) { haloTex = haloRootTex; haloSize = 2.0; haloOp = 0.3; }
            else if (isBranch) { haloTex = haloBranchTex; haloSize = 1.4; haloOp = 0.2; }
            else { haloTex = haloLeafTex; haloSize = 1.0; haloOp = 0.15; }

            const spriteMat = new THREE.SpriteMaterial({
                map: haloTex, color: 0xffffff, transparent: true,
                opacity: haloOp, blending: THREE.AdditiveBlending
            });
            const sprite = new THREE.Sprite(spriteMat);
            sprite.scale.set(haloSize, haloSize, haloSize);
            mesh.add(sprite);

            // Add Edge
            if (def.parent !== null) {
                const parentNode = nodeDefs.find(n => n.id === def.parent);
                const curve = new THREE.CatmullRomCurve3([
                    new THREE.Vector3(...parentNode.pos),
                    new THREE.Vector3(...def.pos)
                ]);
                const tubeGeom = new THREE.TubeGeometry(curve, 20, 0.025, 8, false);
                const tubeMat = new THREE.MeshBasicMaterial({
                    color: 0x00d4ff, transparent: true, opacity: 0.25
                });
                const edgeMesh = new THREE.Mesh(tubeGeom, tubeMat);
                edgeMesh.userData = {
                    baseColor: new THREE.Color(0x00d4ff),
                    targetColor: new THREE.Color(0x00d4ff),
                    baseOpacity: 0.25,
                    radius: 0.025,
                    targetRadius: 0.025,
                    curve: curve
                };
                group.add(edgeMesh);
                edges.push(edgeMesh);
                edgeTo[def.id] = edgeMesh;
            }
        });

        sceneRefs.current = { nodes, edges, edgeTo, group };

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x0a1628, 0.4);
        scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x00d4ff, 1.5, 15);
        pointLight1.position.set(0, 6, 4);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x7c4dff, 0.8, 10);
        pointLight2.position.set(-5, 0, 3);
        scene.add(pointLight2);

        const verifyLight = new THREE.PointLight(0x00e676, 0, 8);
        verifyLight.position.set(0, -2, 2);
        scene.add(verifyLight);
        sceneRefs.current.verifyLight = verifyLight;

        // Raycasting setup
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const canvas = renderer.domElement;

        const onMouseMove = (e) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            if (!animState.current.verifying) {
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(nodes, false);

                let hoveringNode = null;
                if (intersects.length > 0) {
                    hoveringNode = intersects[0].object;
                    canvas.style.cursor = 'pointer';
                } else {
                    canvas.style.cursor = 'default';
                }

                setTooltip({
                    visible: !!hoveringNode,
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top,
                    nodeId: hoveringNode ? hoveringNode.userData.id : null
                });

                nodes.forEach(node => {
                    node.userData.isHovered = (node === hoveringNode);
                    if (!node.userData.isVerified) {
                        node.userData.targetScale = node.userData.isHovered ? 1.4 : 1.0;
                        node.userData.targetEmissive = node.userData.isHovered ? 1.0 : node.userData.baseEmissive;
                    }
                });
            } else {
                setTooltip(prev => ({ ...prev, visible: false }));
            }
        };

        const onClick = () => {
            if (animState.current.verifying) return;
            const hovered = nodes.find(n => n.userData.isHovered);
            if (hovered && hovered.userData.type === 'leaf') {
                animState.current.verifying = true;

                // Construct proof path
                const path = [];
                let curr = hovered.userData.id;
                while (curr !== null) {
                    const nd = nodes.find(n => n.userData.id === curr);
                    path.push(nd);
                    curr = nd.userData.parent;
                }

                // Animate path sequentially
                path.forEach((nd, i) => {
                    setTimeout(() => {
                        nd.userData.isVerified = true;
                        nd.material.color.setHex(0xffffff); // flash white
                        setTimeout(() => nd.material.color.setHex(0x00e676), 50);
                        nd.userData.targetEmissive = 1.2;
                        nd.userData.targetScale = 1.6;

                        setTimeout(() => { if (nd.userData.isVerified) nd.userData.targetScale = 1.2; }, 200);

                        const edge = edgeTo[nd.userData.id];
                        if (edge) {
                            edge.userData.targetColor = new THREE.Color(0x00e676);
                            edge.userData.targetRadius = 0.06;
                            setTimeout(() => {
                                edge.userData.targetRadius = 0.025;
                            }, 300);
                        }

                        // Root reached
                        if (nd.userData.type === 'root') {
                            verifyLight.position.set(0, 3, 2);
                            verifyLight.intensity = 5;
                            edges.forEach(e => e.userData.targetColor = new THREE.Color(0x00e676));

                            // Pulse down light
                            const dimLight = setInterval(() => {
                                verifyLight.intensity -= 0.5;
                                if (verifyLight.intensity <= 0) {
                                    verifyLight.intensity = 0;
                                    clearInterval(dimLight);
                                }
                            }, 30);
                        }
                    }, i * 400);
                });

                // Reset after 3s
                setTimeout(() => {
                    nodes.forEach(n => {
                        n.userData.isVerified = false;
                        n.material.color.copy(n.userData.baseColor);
                    });
                    edges.forEach(e => {
                        e.userData.targetColor = e.userData.baseColor;
                        e.userData.targetRadius = e.userData.radius;
                    });
                    animState.current.verifying = false;
                }, 3000);
            }
        };

        canvas.addEventListener('mousemove', onMouseMove);
        canvas.addEventListener('click', onClick);

        let animFrameId;
        const clock = new THREE.Clock();

        const animate = () => {
            const time = clock.getElapsedTime();

            if (!animState.current.verifying) {
                const isHoveringAny = nodes.some(n => n.userData.isHovered);
                if (!isHoveringAny) {
                    group.rotation.y += 0.002;
                }
            }

            nodes.forEach((node, i) => {
                // Base idle breathing
                let s = node.userData.targetScale;
                if (!node.userData.isHovered && !node.userData.isVerified) {
                    s = 1 + Math.sin(time * 1.5 + i * 0.8) * 0.04;
                }
                node.scale.lerp(new THREE.Vector3(s, s, s), 0.1);

                // Emissive interpolation
                let eTarget = node.userData.targetEmissive;
                if (node.userData.type === 'root' && !node.userData.isVerified && !node.userData.isHovered) {
                    eTarget = 0.6 + Math.sin(time * 2) * 0.2;
                }
                node.material.emissiveIntensity += (eTarget - node.material.emissiveIntensity) * 0.1;
            });

            edges.forEach(edge => {
                // Edge opacity oscillation
                edge.material.opacity = 0.15 + Math.sin(time * 0.8) * 0.1;
                if (animState.current.verifying) edge.material.opacity = 0.8;

                // Color lerp
                edge.material.color.lerp(edge.userData.targetColor, 0.08);

                // Radius lerp via recreating geometry if changed
                if (Math.abs(edge.userData.radius - edge.userData.targetRadius) > 0.001) {
                    edge.userData.radius += (edge.userData.targetRadius - edge.userData.radius) * 0.2;
                    edge.geometry.dispose();
                    edge.geometry = new THREE.TubeGeometry(edge.userData.curve, 20, edge.userData.radius, 8, false);
                }
            });

            renderer.render(scene, camera);
            animFrameId = requestAnimationFrame(animate);
        };

        animate();

        // Responsive Observer
        const ro = new ResizeObserver(([entry]) => {
            const { width } = entry.contentRect;
            renderer.setSize(width, 340);
            camera.aspect = width / 340;
            camera.updateProjectionMatrix();
        });
        ro.observe(containerRef.current);

        return () => {
            cancelAnimationFrame(animFrameId);
            renderer.dispose();
            scene.traverse((obj) => {
                if (obj.isMesh || obj.isLine || obj.isSprite) {
                    if (obj.geometry) obj.geometry.dispose();
                    if (obj.material) {
                        if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
                        else obj.material.dispose();
                    }
                }
            });
            canvas.removeEventListener('mousemove', onMouseMove);
            canvas.removeEventListener('click', onClick);
            ro.disconnect();
            if (renderer.domElement && renderer.domElement.parentNode) {
                renderer.domElement.parentNode.removeChild(renderer.domElement);
            }
        };
    }, []);

    // Global Verification Event (Scheduled every 30s)
    useEffect(() => {
        const interval = setInterval(() => {
            const { nodes, edges, verifyLight } = sceneRefs.current;
            if (!nodes) return;
            console.log('Merkle verification animation triggered');

            animState.current.verifying = true;

            // Trigger stagger
            [...nodes].reverse().forEach((nd, i) => {
                setTimeout(() => {
                    nd.userData.isVerified = true;
                    nd.material.color.setHex(0x00e676);
                    nd.userData.targetScale = 1.3;
                    setTimeout(() => { nd.userData.targetScale = 1.0; }, 150);
                }, i * 100);
            });

            edges.forEach(e => {
                e.userData.targetColor = new THREE.Color(0x00e676);
                e.material.opacity = 1.0;
            });

            // Sweep light
            if (verifyLight) {
                let y = -2;
                verifyLight.intensity = 5;
                const sweep = setInterval(() => {
                    y += 0.2;
                    verifyLight.position.set(0, y, 2);
                    if (y >= 4) {
                        clearInterval(sweep);
                        // Reset light
                        const dim = setInterval(() => {
                            verifyLight.intensity -= 0.2;
                            if (verifyLight.intensity <= 0) {
                                verifyLight.intensity = 0;
                                clearInterval(dim);
                            }
                        }, 50);
                    }
                }, 30);
            }

            // Cleanup
            setTimeout(() => {
                nodes.forEach(n => {
                    n.userData.isVerified = false;
                    n.material.color.copy(n.userData.baseColor);
                });
                edges.forEach(e => {
                    e.userData.targetColor = e.userData.baseColor;
                    e.material.opacity = 0.25;
                });
                animState.current.verifying = false;
            }, 2500);

        }, 30000);
        return () => clearInterval(interval);
    }, []);

    let tooltipLabel = '';
    let hashAbbr = '';
    if (tooltip.nodeId !== null) {
        if (tooltip.nodeId === 0) tooltipLabel = "ROOT NODE (LEVEL 0)";
        else if (tooltip.nodeId <= 2) tooltipLabel = `BRANCH NODE #${tooltip.nodeId} (LEVEL 1)`;
        else tooltipLabel = `LEAF NODE #${tooltip.nodeId - 2} (LEVEL 2)`;

        // fake deterministic hash
        hashAbbr = '0e' + ((tooltip.nodeId * 7777) % 99999).toString(16) + 'd1f9...';
    }

    return (
        <Box ref={containerRef} sx={{ position: 'relative', width: '100%', mb: 2 }}>
            <Box ref={mountRef} sx={{ width: '100%', height: 340, cursor: 'default' }} />

            {/* Tooltip Overlay */}
            {tooltip.visible && (
                <Paper
                    sx={{
                        position: 'absolute',
                        top: tooltip.y + 12,
                        left: tooltip.x + 12,
                        pointerEvents: 'none',
                        zIndex: 10,
                        backgroundColor: 'rgba(8, 14, 28, 0.85)',
                        backdropFilter: 'blur(8px)',
                        border: '1px solid #00d4ff',
                        borderRadius: '6px',
                        p: 1.5,
                        minWidth: 180,
                        transform: 'translate(0, 0)',
                    }}
                >
                    <Typography sx={{ color: '#00d4ff', fontSize: '11px', fontFamily: '"IBM Plex Mono", monospace', fontWeight: 700, mb: 1 }}>
                        🔵 {tooltipLabel}
                    </Typography>
                    <Typography sx={{ color: '#e8f4fd', fontSize: '11px', fontFamily: '"IBM Plex Mono", monospace' }}>
                        Hash: {hashAbbr}
                    </Typography>
                    <Typography sx={{ color: '#e8f4fd', fontSize: '11px', fontFamily: '"IBM Plex Mono", monospace' }}>
                        Records: {tooltip.nodeId >= 3 ? Math.max(1, Math.floor(recordsCount / 4)) : '-'}
                    </Typography>
                    <Typography sx={{ color: '#00e676', fontSize: '11px', fontFamily: '"IBM Plex Mono", monospace', mt: 0.5 }}>
                        Verified ✓
                    </Typography>
                </Paper>
            )}
        </Box>
    );
};

export default MerkleTree3D;
