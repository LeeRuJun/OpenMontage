import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { EditorialCanvas } from "./EditorialCanvas";
import type { EditorialBaseProps } from "./types";

export interface DataRevealSceneProps extends EditorialBaseProps {
  label: string;
  value: number | string;
  unit?: string;
  from?: number;
  accentColor?: string;
  title?: string;
}

export const DataRevealScene: React.FC<DataRevealSceneProps> = ({ label, value, unit, from = 0, accentColor, title, theme, durationInFrames }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, Math.min(durationInFrames, 36)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const numeric = typeof value === "number" ? Math.round(from + (value - from) * progress).toLocaleString("zh-CN") : value;
  return (
    <EditorialCanvas theme={theme} durationInFrames={durationInFrames}>
      {title && <div style={{ position: "absolute", top: 64, left: 90, fontSize: 54, fontWeight: 800 }}>{title}</div>}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", textAlign: "center" }}>
        <div style={{ fontSize: 34, opacity: 0.72 }}>{label}</div>
        <div style={{ marginTop: 18, fontSize: 142, lineHeight: 1, fontWeight: 900, color: accentColor || theme.accentColor }}>{numeric}{unit || ""}</div>
      </AbsoluteFill>
    </EditorialCanvas>
  );
};
