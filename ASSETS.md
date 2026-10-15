# ASSETS & ATTRIBUTION: PERIMETER ASPM

This document logs all assets, 3D procedural geometries, photography, libraries, typography, and icon suites utilized across the Perimeter landing page and SOC dashboard.

---

## 1. High-Resolution Photographic & 3D Hardware Imagery

Downloaded directly to `frontend/dashboard/public/images/`:

| Asset File | Subject & Usage | Source | Resolution | License |
| :--- | :--- | :--- | :--- | :--- |
| **`datacenter_rack.jpg`** | Enterprise Datacenter Hardware & Fiber Ingress (Scene 2: Discover) | Unsplash ([photo-1558494949](https://unsplash.com/photos/1558494949-ef010cbdcc31)) | 1200w / 195 KB | Unsplash Free License |
| **`silicon_chip.jpg`** | Hardware Cryptographic Silicon Microchip (Scene 5: Attack Replay) | Unsplash ([photo-1518770660](https://unsplash.com/photos/1518770660439-4636190af475)) | 1200w / 176 KB | Unsplash Free License |
| **`glass_prism_core.jpg`** | Dark 3D Glass Prism Core with Metallic Bevels (Scene 3: Shadow API) | Unsplash ([photo-1618005182](https://unsplash.com/photos/1618005182384-a83a8bd57fbe)) | 1200w / 56 KB | Unsplash Free License |
| **`dark_monolith.jpg`** | Atmospheric 3D Dark Monolith & Ingress Core (Scene 7: Closing CTA) | Unsplash ([photo-1634017839](https://unsplash.com/photos/1634017839464-5c339ebe3cb4)) | 1200w / 204 KB | Unsplash Free License |
| **`titanium_core.jpg`** | Cyber Geometric Titanium Vault Core (Hardware Enclave Reference) | Unsplash ([photo-1607604276](https://unsplash.com/photos/1607604276583-eef5d076aa5f)) | 1200w / 163 KB | Unsplash Free License |
| **`optical_streams.jpg`** | Optical Light Streams & Low Latency Fiber Ingress | Unsplash ([photo-1509228468](https://unsplash.com/photos/1509228468518-180dd4864904)) | 1200w / 73 KB | Unsplash Free License |

---

## 2. 3D Geometries & WebGL Shaders

| Asset / Mesh | Source / Technique | Format | Size | License |
| :--- | :--- | :--- | :--- | :--- |
| **Titanium Cryptographic Enclave** | Three.js `BoxGeometry` & `MeshStandardMaterial(metalness: 0.92, roughness: 0.18)` | In-memory procedural | 0 KB (runtime generated) | MIT |
| **Frosted Glass Core** | Three.js `OctahedronGeometry` & `MeshPhysicalMaterial(transmission: 0.85, ior: 1.5)` | In-memory procedural | 0 KB (runtime generated) | MIT |
| **Concentric Titanium Rings** | Three.js `TorusGeometry` with ACESFilmic studio lighting | Vector torus buffer | 0 KB (runtime generated) | MIT |

---

## 3. Iconography

| Asset Family | Stroke Weight | Package | Author / Source | License |
| :--- | :--- | :--- | :--- | :--- |
| **Phosphor Icons** | 1.5px – 2.0px regular / bold | `@phosphor-icons/react` (v2.1.10) | Helena Zhang & Tobias Fried ([phosphoricons.com](https://phosphoricons.com)) | MIT |

---

## 4. Typography

| Font Family | Usage | Weights | Source | License |
| :--- | :--- | :--- | :--- | :--- |
| **SF Pro / Apple Sans Stack** | Apple-grade display headlines (`tracking-[-0.035em]`), section headers, nav | 500, 600, 700 | Apple System Font Stack (`-apple-system`, `BlinkMacSystemFont`, `Inter`) | System / OFL |
| **JetBrains Mono** | Data readouts, code snippets, metrics, latency telemetry | 400, 500, 700 | JetBrains ([jetbrains.com/mono](https://www.jetbrains.com/lp/mono/)) | SIL OFL 1.1 |

---

## 5. Motion & Animation Libraries

| Library | Version | Purpose | License |
| :--- | :--- | :--- | :--- |
| **GSAP (GreenSock)** | `^3.15.0` | Magnetic button physics (`quickTo`), fluid cursor interactions | GreenSock Standard License / Free for Web |
| **Lenis Smooth Scroll** | `^1.3.17` | 60fps inertial scrolling with `prefers-reduced-motion` compliance | MIT (Studio Freight) |
| **Three.js** | `^0.186.1` | WebGL 3D physical material rendering pipeline | MIT |
