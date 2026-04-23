/**
 * Neural Network Particle Field
 * =============================
 * Three.js visualization of interconnected nodes with data packet travel.
 * Uses React Three Fiber for declarative 3D rendering.
 */
import { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Instances, Instance, Line } from '@react-three/drei';
import * as THREE from 'three';

// ── CONFIG ──
const NODE_COUNT = 120;
const CONNECTION_DISTANCE = 2.8;
const CAMERA_SPEED = 0.05;
const PACKET_SPEED = 0.8;

const PALETTE = [
  new THREE.Color('#8b5cf6'), // purple
  new THREE.Color('#eab308'), // gold
  new THREE.Color('#06b6d4'), // cyan
  new THREE.Color('#a855f7'), // violet
];

// ── TYPES ──
interface NodeData {
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  color: THREE.Color;
  size: number;
  pulsePhase: number;
}

interface Connection {
  from: number;
  to: number;
  packetProgress: number;
  hasPacket: boolean;
}

// ── DATA PACKET ──
function DataPacket({ start, end, progress }: { start: THREE.Vector3; end: THREE.Vector3; progress: number }) {
  const ref = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (ref.current) {
      ref.current.position.lerpVectors(start, end, progress);
      const scale = 1 + Math.sin(progress * Math.PI) * 0.5;
      ref.current.scale.setScalar(scale);
    }
  });

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.06, 8, 8]} />
      <meshBasicMaterial color="#ffffff" transparent opacity={0.9} />
    </mesh>
  );
}

// ── CONNECTIONS ──
function Connections({ nodes, connections }: { nodes: NodeData[]; connections: Connection[] }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (!groupRef.current) return;

    // Animate packet progress
    connections.forEach((conn) => {
      if (conn.hasPacket) {
        conn.packetProgress += delta * PACKET_SPEED;
        if (conn.packetProgress >= 1) {
          conn.packetProgress = 0;
          conn.hasPacket = Math.random() > 0.7; // 30% chance to respawn immediately
        }
      } else if (Math.random() < 0.005) {
        conn.hasPacket = true;
        conn.packetProgress = 0;
      }
    });
  });

  return (
    <group ref={groupRef}>
      {connections.map((conn, i) => {
        const from = nodes[conn.from].position;
        const to = nodes[conn.to].position;
        const color = nodes[conn.from].color;

        return (
          <group key={i}>
            <Line
              points={[from.clone(), to.clone()]}
              color={color}
              lineWidth={0.5}
              transparent
              opacity={0.25}
            />
            {conn.hasPacket && (
              <DataPacket
                start={from}
                end={to}
                progress={conn.packetProgress}
              />
            )}
          </group>
        );
      })}
    </group>
  );
}

// ── NODES ──
function NodeField({ nodes }: { nodes: NodeData[] }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const colorArray = useMemo(() => new Float32Array(NODE_COUNT * 3), []);

  useEffect(() => {
    if (!meshRef.current) return;

    nodes.forEach((node, i) => {
      dummy.position.copy(node.position);
      dummy.scale.setScalar(node.size);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
      colorArray[i * 3] = node.color.r;
      colorArray[i * 3 + 1] = node.color.g;
      colorArray[i * 3 + 2] = node.color.b;
    });

    meshRef.current.instanceMatrix.needsUpdate = true;
    meshRef.current.instanceColor!.needsUpdate = true;
  }, [nodes, dummy, colorArray]);

  useFrame((_, delta) => {
    if (!meshRef.current) return;

    nodes.forEach((node, i) => {
      // Gentle floating motion
      node.position.add(node.velocity.clone().multiplyScalar(delta * 0.3));

      // Boundary wrap
      const bound = 6;
      ['x', 'y', 'z'].forEach((axis) => {
        if (Math.abs(node.position[axis as 'x' | 'y' | 'z']) > bound) {
          node.velocity[axis as 'x' | 'y' | 'z'] *= -1;
        }
      });

      // Pulse size
      const pulse = 1 + Math.sin(Date.now() * 0.002 + node.pulsePhase) * 0.2;
      dummy.position.copy(node.position);
      dummy.scale.setScalar(node.size * pulse);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });

    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, NODE_COUNT]}>
      <sphereGeometry args={[0.12, 16, 16]} />
      <meshBasicMaterial
        transparent
        opacity={0.85}
        toneMapped={false}
      />
      <instancedBufferAttribute
        attach="instanceColor"
        args={[colorArray, 3]}
      />
    </instancedMesh>
  );
}

// ── CAMERA CONTROLLER ──
function CameraController() {
  const { camera, pointer } = useThree();
  const targetRotation = useRef({ x: 0, y: 0 });

  useFrame((state, delta) => {
    // Subtle mouse follow
    targetRotation.current.x = pointer.y * 0.15;
    targetRotation.current.y = pointer.x * 0.15;

    // Smooth interpolation
    camera.rotation.x += (targetRotation.current.x - camera.rotation.x) * delta * 2;
    camera.rotation.y += (targetRotation.current.y - camera.rotation.y) * delta * 2;

    // Slow orbit drift
    const time = state.clock.elapsedTime;
    camera.position.x = Math.sin(time * 0.05) * 0.5;
    camera.position.y = Math.cos(time * 0.03) * 0.3;
  });

  return null;
}

// ── SCENE ──
function Scene() {
  const [nodes, connections] = useMemo(() => {
    // Generate nodes
    const n: NodeData[] = Array.from({ length: NODE_COUNT }, () => ({
      position: new THREE.Vector3(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 8,
        (Math.random() - 0.5) * 6
      ),
      velocity: new THREE.Vector3(
        (Math.random() - 0.5) * 0.5,
        (Math.random() - 0.5) * 0.5,
        (Math.random() - 0.5) * 0.3
      ),
      color: PALETTE[Math.floor(Math.random() * PALETTE.length)],
      size: 0.8 + Math.random() * 0.6,
      pulsePhase: Math.random() * Math.PI * 2,
    }));

    // Generate connections (proximity based)
    const c: Connection[] = [];
    for (let i = 0; i < NODE_COUNT; i++) {
      for (let j = i + 1; j < NODE_COUNT; j++) {
        const dist = n[i].position.distanceTo(n[j].position);
        if (dist < CONNECTION_DISTANCE && Math.random() < 0.4) {
          c.push({
            from: i,
            to: j,
            packetProgress: Math.random(),
            hasPacket: Math.random() < 0.3,
          });
        }
      }
    }

    return [n, c];
  }, []);

  return (
    <>
      <CameraController />
      <NodeField nodes={nodes} />
      <Connections nodes={nodes} connections={connections} />
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#8b5cf6" />
      <pointLight position={[-10, -10, -5]} intensity={0.3} color="#06b6d4" />
    </>
  );
}

// ── MAIN EXPORT ──
export default function NeuralNetwork() {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mq.matches);
    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  if (reducedMotion) {
    return (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-cyan-500/10" />
      </div>
    );
  }

  return (
    <div className="absolute inset-0 overflow-hidden">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        dpr={[1, 1.5]}
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance',
        }}
        style={{ background: 'transparent' }}
      >
        <Scene />
      </Canvas>
      {/* Gradient overlay for text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/60 via-transparent to-[#0a0a0f]/90 pointer-events-none" />
    </div>
  );
}
