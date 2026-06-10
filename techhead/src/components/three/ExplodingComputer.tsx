"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { RoundedBox, ContactShadows } from "@react-three/drei";
import { useReducedMotion } from "framer-motion";
import * as THREE from "three";

const CYCLE = 9; // seconds for a full explode → reassemble loop
const easeInOut = (x: number) =>
  x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;

// Map elapsed time → explosion amount [0..1] with dwell at each end.
function explosionAmount(t: number) {
  const p = (t % CYCLE) / CYCLE;
  if (p < 0.16) return 0;
  if (p < 0.42) return easeInOut((p - 0.16) / 0.26);
  if (p < 0.6) return 1;
  if (p < 0.86) return 1 - easeInOut((p - 0.6) / 0.26);
  return 0;
}

type PartDef = {
  pos: [number, number, number]; // assembled
  explode: [number, number, number]; // offset when exploded
  rot?: [number, number, number]; // extra rotation when exploded
  render: React.ReactNode;
};

function gold(emissive = 0.6) {
  return (
    <meshStandardMaterial
      color="#d4922a"
      metalness={0.9}
      roughness={0.25}
      emissive="#d4922a"
      emissiveIntensity={emissive}
    />
  );
}

function ComputerModel() {
  const group = useRef<THREE.Group>(null);
  const partRefs = useRef<(THREE.Group | null)[]>([]);
  const reduce = useReducedMotion();
  const { pointer } = useThree();

  const parts: PartDef[] = useMemo(
    () => [
      // Aluminium base / chassis bottom
      {
        pos: [0, -0.45, 0],
        explode: [0, -1.7, 0],
        render: (
          <RoundedBox args={[3.6, 0.22, 2.5]} radius={0.08} smoothness={4}>
            <meshStandardMaterial color="#46413c" metalness={0.85} roughness={0.35} />
          </RoundedBox>
        ),
      },
      // Battery
      {
        pos: [0, -0.32, 0.55],
        explode: [-2.6, -0.6, 1.2],
        rot: [0.3, 0.4, 0],
        render: (
          <RoundedBox args={[2.4, 0.12, 0.9]} radius={0.04} smoothness={3}>
            <meshStandardMaterial color="#2a2620" metalness={0.4} roughness={0.6} />
          </RoundedBox>
        ),
      },
      // Motherboard (green PCB)
      {
        pos: [0, -0.28, -0.55],
        explode: [2.7, -0.3, -0.6],
        rot: [0.2, -0.5, 0.1],
        render: (
          <group>
            <RoundedBox args={[2.6, 0.06, 0.95]} radius={0.02} smoothness={3}>
              <meshStandardMaterial color="#1f3b2e" metalness={0.3} roughness={0.7} />
            </RoundedBox>
            {/* chips + traces */}
            <mesh position={[-0.7, 0.08, 0.1]}>
              <boxGeometry args={[0.45, 0.1, 0.45]} />
              <meshStandardMaterial color="#0c0a09" metalness={0.6} roughness={0.4} />
            </mesh>
            <mesh position={[0.5, 0.07, -0.2]}>
              <boxGeometry args={[0.3, 0.06, 0.3]} />
              {gold(0.4)}
            </mesh>
            <mesh position={[0.9, 0.07, 0.25]}>
              <boxGeometry args={[0.5, 0.05, 0.2]} />
              <meshStandardMaterial color="#0c0a09" metalness={0.5} roughness={0.5} />
            </mesh>
          </group>
        ),
      },
      // RAM sticks
      {
        pos: [-0.9, -0.18, -0.2],
        explode: [-1.6, 1.9, -1.4],
        rot: [0.1, 0.6, 0.4],
        render: (
          <group>
            <RoundedBox args={[1.1, 0.18, 0.16]} radius={0.02} smoothness={3}>
              <meshStandardMaterial color="#2b6b52" metalness={0.4} roughness={0.5} />
            </RoundedBox>
            <mesh position={[0, -0.12, 0]}>
              <boxGeometry args={[1.0, 0.06, 0.14]} />
              {gold(0.35)}
            </mesh>
          </group>
        ),
      },
      // CPU + heatsink
      {
        pos: [0.7, -0.18, -0.4],
        explode: [1.4, 2.2, -0.6],
        rot: [0.5, 0.3, 0],
        render: (
          <group>
            <mesh>
              <boxGeometry args={[0.55, 0.08, 0.55]} />
              <meshStandardMaterial color="#cfcabf" metalness={0.95} roughness={0.18} />
            </mesh>
            {[...Array(6)].map((_, i) => (
              <mesh key={i} position={[-0.22 + i * 0.09, 0.16, 0]}>
                <boxGeometry args={[0.04, 0.28, 0.5]} />
                <meshStandardMaterial color="#b8b2a6" metalness={0.95} roughness={0.2} />
              </mesh>
            ))}
          </group>
        ),
      },
      // Cooling fan
      {
        pos: [-0.95, -0.2, -0.75],
        explode: [-2.9, 1.1, -1.2],
        rot: [0.6, 0, 0.5],
        render: <Fan />,
      },
      // Keyboard deck
      {
        pos: [0, -0.3, 0],
        explode: [0, 1.5, 0.2],
        render: <KeyboardDeck />,
      },
      // Screen (lid + display), hinged up at the back
      {
        pos: [0, 1.05, -1.15],
        explode: [0, 2.9, -2.4],
        rot: [-0.18, 0, 0],
        render: <Screen />,
      },
    ],
    [],
  );

  useFrame((state) => {
    const g = group.current;
    if (!g) return;
    const time = state.clock.elapsedTime;
    const amt = reduce ? 0 : explosionAmount(time);

    // Whole-model slow rotation, gentle bob, and pointer parallax
    const targetY = reduce ? 0.5 : 0.5 + Math.sin(time * 0.25) * 0.5 + pointer.x * 0.4;
    const targetX = reduce ? -0.18 : -0.12 + Math.sin(time * 0.3) * 0.06 - pointer.y * 0.2;
    g.rotation.y += (targetY - g.rotation.y) * 0.05;
    g.rotation.x += (targetX - g.rotation.x) * 0.05;
    g.position.y = reduce ? 0 : Math.sin(time * 0.6) * 0.12;

    parts.forEach((part, i) => {
      const ref = partRefs.current[i];
      if (!ref) return;
      ref.position.set(
        part.pos[0] + part.explode[0] * amt,
        part.pos[1] + part.explode[1] * amt,
        part.pos[2] + part.explode[2] * amt,
      );
      if (part.rot) {
        ref.rotation.set(part.rot[0] * amt, part.rot[1] * amt, part.rot[2] * amt);
      }
    });
  });

  return (
    <group ref={group} scale={1.05}>
      {parts.map((part, i) => (
        <group
          key={i}
          ref={(el) => {
            partRefs.current[i] = el;
          }}
        >
          {part.render}
        </group>
      ))}
    </group>
  );
}

function Fan() {
  const blades = useRef<THREE.Group>(null);
  useFrame((_, delta) => {
    if (blades.current) blades.current.rotation.y += delta * 6;
  });
  return (
    <group>
      <mesh>
        <cylinderGeometry args={[0.55, 0.55, 0.16, 24]} />
        <meshStandardMaterial color="#1a1714" metalness={0.6} roughness={0.4} />
      </mesh>
      <group ref={blades} position={[0, 0.06, 0]}>
        {[...Array(7)].map((_, i) => (
          <mesh key={i} rotation={[0, (i / 7) * Math.PI * 2, 0]} position={[0.22, 0, 0]}>
            <boxGeometry args={[0.4, 0.02, 0.12]} />
            <meshStandardMaterial color="#3a3531" metalness={0.7} roughness={0.3} />
          </mesh>
        ))}
        <mesh>
          <cylinderGeometry args={[0.12, 0.12, 0.1, 16]} />
          {gold(0.5)}
        </mesh>
      </group>
    </group>
  );
}

function KeyboardDeck() {
  // 6 x 14 key grid as instanced-ish small boxes
  const keys = useMemo(() => {
    const arr: [number, number][] = [];
    const cols = 14;
    const rows = 5;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        arr.push([(-cols / 2 + c + 0.5) * 0.21, (-rows / 2 + r + 0.5) * 0.21]);
      }
    }
    return arr;
  }, []);
  return (
    <group>
      <RoundedBox args={[3.4, 0.1, 2.3]} radius={0.06} smoothness={3}>
        <meshStandardMaterial color="#211e1b" metalness={0.6} roughness={0.45} />
      </RoundedBox>
      <group position={[0, 0.07, -0.25]}>
        {keys.map(([x, z], i) => (
          <mesh key={i} position={[x, 0, z]}>
            <boxGeometry args={[0.16, 0.04, 0.16]} />
            <meshStandardMaterial color="#0f0d0b" metalness={0.3} roughness={0.7} />
          </mesh>
        ))}
      </group>
      {/* trackpad */}
      <mesh position={[0, 0.06, 0.78]}>
        <boxGeometry args={[1.1, 0.02, 0.7]} />
        <meshStandardMaterial color="#2c2825" metalness={0.5} roughness={0.4} />
      </mesh>
    </group>
  );
}

function Screen() {
  return (
    <group rotation={[-0.12, 0, 0]}>
      {/* lid / back */}
      <RoundedBox args={[3.5, 2.3, 0.1]} radius={0.08} smoothness={4}>
        <meshStandardMaterial color="#46413c" metalness={0.85} roughness={0.35} />
      </RoundedBox>
      {/* display */}
      <mesh position={[0, 0, 0.06]}>
        <planeGeometry args={[3.2, 2.0]} />
        <meshStandardMaterial
          color="#0c0a09"
          emissive="#d4922a"
          emissiveIntensity={0.18}
          metalness={0.2}
          roughness={0.1}
        />
      </mesh>
      {/* glowing UI bars */}
      <mesh position={[-0.9, 0.55, 0.07]}>
        <planeGeometry args={[1.0, 0.12]} />
        <meshBasicMaterial color="#f0b357" toneMapped={false} />
      </mesh>
      <mesh position={[-0.55, 0.25, 0.07]}>
        <planeGeometry args={[1.7, 0.07]} />
        <meshBasicMaterial color="#8a6a32" toneMapped={false} />
      </mesh>
      <mesh position={[-0.7, 0.05, 0.07]}>
        <planeGeometry args={[1.4, 0.07]} />
        <meshBasicMaterial color="#5a4520" toneMapped={false} />
      </mesh>
      {/* logo dot */}
      <mesh position={[0, -0.2, 0.11]}>
        <circleGeometry args={[0.14, 32]} />
        <meshBasicMaterial color="#f0b357" toneMapped={false} />
      </mesh>
    </group>
  );
}

export default function ExplodingComputer() {
  return (
    <Canvas
      dpr={[1, 2]}
      camera={{ position: [0, 0.6, 9.5], fov: 38 }}
      gl={{ antialias: true, alpha: true }}
      style={{ background: "transparent" }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 6, 5]} intensity={1.6} color="#fff6e6" />
      <pointLight position={[-5, 2, 4]} intensity={40} distance={25} color="#d4922a" />
      <pointLight position={[4, -2, 3]} intensity={18} distance={20} color="#6ea0ff" />
      <ComputerModel />
      <ContactShadows
        position={[0, -2.6, 0]}
        opacity={0.45}
        scale={12}
        blur={3}
        far={5}
        color="#000000"
      />
    </Canvas>
  );
}
