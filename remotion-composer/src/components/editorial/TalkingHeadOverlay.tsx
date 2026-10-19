import React from "react";
import { AbsoluteFill, staticFile } from "remotion";

export interface TalkingHeadOverlayProps {
  src: string;
  size?: number;
  right?: number;
  bottom?: number;
  opacity?: number;
  borderColor?: string;
}

export const TalkingHeadOverlay: React.FC<TalkingHeadOverlayProps> = ({ src, size = 150, right = 48, bottom = 42, opacity = 1, borderColor = "#B6503C" }) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <img src={src.startsWith("/") || src.startsWith("http") ? src : staticFile(src)} style={{ position: "absolute", right, bottom, width: size, height: size, borderRadius: "50%", objectFit: "cover", opacity, border: `5px solid ${borderColor}`, boxShadow: "0 8px 24px rgba(0,0,0,0.2)" }} />
  </AbsoluteFill>
);
