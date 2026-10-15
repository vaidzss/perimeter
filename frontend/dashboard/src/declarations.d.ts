declare module '@phosphor-icons/react' {
  import { ComponentType, SVGProps } from 'react';
  export interface IconProps extends SVGProps<SVGSVGElement> {
    color?: string;
    size?: string | number;
    weight?: 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';
    mirrored?: boolean;
    className?: string;
  }
  export type Icon = ComponentType<IconProps>;

  export const Shield: Icon;
  export const ShieldCheck: Icon;
  export const ShieldWarning: Icon;
  export const ShieldAlert: Icon;
  export const ShieldSlash: Icon;
  export const ArrowRight: Icon;
  export const ArrowUpRight: Icon;
  export const ArrowsLeftRight: Icon;
  export const Activity: Icon;
  export const Terminal: Icon;
  export const Crosshair: Icon;
  export const Broadcast: Icon;
  export const ArrowsClockwise: Icon;
  export const Warning: Icon;
  export const WarningCircle: Icon;
  export const GitBranch: Icon;
  export const GitFork: Icon;
  export const Radio: Icon;
  export const Check: Icon;
  export const FileCode: Icon;
  export const ChartLine: Icon;
  export const ChartBar: Icon;
  export const SlidersHorizontal: Icon;
  export const Siren: Icon;
  export const CheckCircle: Icon;
  export const Lightning: Icon;
  export const Play: Icon;
  export const Lock: Icon;
  export const LockKey: Icon;
  export const Skull: Icon;
  export const Cpu: Icon;
  export const XCircle: Icon;
  export const Swap: Icon;
  export const Flame: Icon;
  export const Copy: Icon;
  export const List: Icon;
  export const X: Icon;
  export const Database: Icon;
  export const Pulse: Icon;
  export const Users: Icon;
  export const Globe: Icon;
  export const CaretRight: Icon;
  export const CaretDown: Icon;
  export const MagnifyingGlass: Icon;
  export const Prohibit: Icon;
  export const EyeSlash: Icon;
  export const Circle: Icon;
  export const Sparkle: Icon;
}

declare module 'lenis' {
  export interface LenisOptions {
    lerp?: number;
    duration?: number;
    orientation?: 'vertical' | 'horizontal';
    gestureOrientation?: 'vertical' | 'horizontal' | 'both';
    smoothWheel?: boolean;
    wheelMultiplier?: number;
    touchMultiplier?: number;
    infinite?: boolean;
    autoResize?: boolean;
    wrapper?: Window | HTMLElement;
    content?: HTMLElement;
    [key: string]: any;
  }

  export default class Lenis {
    constructor(options?: LenisOptions);
    raf(time: number): void;
    destroy(): void;
    scrollTo(target: any, options?: any): void;
    start(): void;
    stop(): void;
  }
}
