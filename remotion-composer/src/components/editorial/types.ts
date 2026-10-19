import type { ReactNode } from "react";
import type { ThemeConfig } from "../../Root";

export interface EditorialBaseProps {
  durationInFrames: number;
  theme: ThemeConfig;
}

export interface EditorialNode {
  id: string;
  label: string;
  x: number;
  y: number;
  color?: string;
  detail?: string;
}

export interface EditorialEdge {
  from: string;
  to: string;
  color?: string;
}

export interface TimelineEvent {
  label: string;
  year?: string;
  detail?: string;
}

export interface MapPath {
  id: string;
  d: string;
  color?: string;
}

export interface EditorialCanvasProps extends EditorialBaseProps {
  children?: ReactNode;
  backgroundColor?: string;
  texture?: boolean;
}
