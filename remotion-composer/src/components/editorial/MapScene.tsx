import React from "react";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame } from "remotion";
import { EditorialCanvas } from "./EditorialCanvas";
import type { EditorialBaseProps, EditorialNode, MapPath } from "./types";

export interface MapSceneProps extends EditorialBaseProps {
  backgroundSrc?: string;
  nodes: EditorialNode[];
  paths?: MapPath[];
  highlightColor?: string;
  title?: string;
}

export const MapScene: React.FC<MapSceneProps> = ({
  backgroundSrc,
  nodes,
  paths = [],
  highlightColor,
  title,
  theme,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const accent = highlightColor || theme.accentColor;
  return (
    <EditorialCanvas theme={theme} durationInFrames={durationInFrames}>
      {backgroundSrc && <img src={backgroundSrc.startsWith("/") || backgroundSrc.startsWith("http") ? backgroundSrc : staticFile(backgroundSrc)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "contain", opacity: 0.72 }} />}
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
        {paths.map((path, index) => {
          const length = 1800;
          const draw = interpolate(progress, [index / Math.max(paths.length, 1), 0.35 + index / Math.max(paths.length, 1)], [length, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return <path key={path.id} d={path.d} fill="none" stroke={path.color || accent} strokeWidth={8} strokeLinecap="round" strokeDasharray={length} strokeDashoffset={draw} opacity={0.9} />;
        })}
        {nodes.map((node, index) => {
          const reveal = interpolate(progress, [index / Math.max(nodes.length, 1), 0.25 + index / Math.max(nodes.length, 1)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return <g key={node.id} opacity={reveal}>
            <circle cx={node.x} cy={node.y} r={18} fill={node.color || accent} />
            <text x={node.x + 28} y={node.y + 10} fontSize={30} fill={theme.textColor}>{node.label}</text>
          </g>;
        })}
      </svg>
      {title && <div style={{ position: "absolute", top: 68, left: 90, fontSize: 54, fontWeight: 800, color: theme.textColor }}>{title}</div>}
    </EditorialCanvas>
  );
};
