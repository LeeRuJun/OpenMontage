import React from "react";
import { AbsoluteFill, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { EditorialCanvas } from "./EditorialCanvas";
import type { EditorialBaseProps } from "./types";

export interface ImageCardSceneProps extends EditorialBaseProps {
  src: string;
  title?: string;
  subtitle?: string;
  animation?: "zoom-in" | "zoom-out" | "pan-left" | "pan-right" | "static";
  backgroundColor?: string;
}

export const ImageCardScene: React.FC<ImageCardSceneProps> = ({
  src,
  title,
  subtitle,
  animation = "zoom-in",
  backgroundColor,
  theme,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const intro = spring({ frame, fps, config: { damping: 18, stiffness: 90 } });
  const scale = animation === "zoom-out" ? 1.08 - progress * 0.08 : animation === "static" ? 1 : 1 + progress * 0.08;
  const x = animation === "pan-left" ? interpolate(progress, [0, 1], [18, -18]) : animation === "pan-right" ? interpolate(progress, [0, 1], [-18, 18]) : 0;

  return (
    <EditorialCanvas theme={theme} backgroundColor={backgroundColor} durationInFrames={durationInFrames}>
      <AbsoluteFill style={{ opacity: intro, overflow: "hidden" }}>
        <img src={src.startsWith("/") || src.startsWith("http") ? src : staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "contain", transform: `translateX(${x}px) scale(${scale})` }} />
        {(title || subtitle) && (
          <div style={{ position: "absolute", left: 100, right: 100, bottom: 80, padding: "26px 34px", background: "rgba(233,223,200,0.88)", borderLeft: `8px solid ${theme.accentColor}` }}>
            {title && <div style={{ fontSize: 54, fontWeight: 800 }}>{title}</div>}
            {subtitle && <div style={{ marginTop: 10, fontSize: 28, opacity: 0.78 }}>{subtitle}</div>}
          </div>
        )}
      </AbsoluteFill>
    </EditorialCanvas>
  );
};
