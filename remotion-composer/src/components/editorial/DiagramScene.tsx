import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { EditorialCanvas } from "./EditorialCanvas";
import type { EditorialBaseProps, EditorialEdge, EditorialNode } from "./types";

export interface DiagramSceneProps extends EditorialBaseProps {
  nodes: EditorialNode[];
  edges?: EditorialEdge[];
  revealOrder?: string[];
  accentColor?: string;
  title?: string;
}

export const DiagramScene: React.FC<DiagramSceneProps> = ({
  nodes,
  edges = [],
  revealOrder = nodes.map((node) => node.id),
  accentColor,
  title,
  theme,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const accent = accentColor || theme.accentColor;
  const position = new Map(nodes.map((node) => [node.id, node]));
  return (
    <EditorialCanvas theme={theme} durationInFrames={durationInFrames}>
      {title && <div style={{ position: "absolute", top: 64, left: 90, fontSize: 54, fontWeight: 800 }}>{title}</div>}
      <svg viewBox="0 0 1920 1080" style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
        {edges.map((edge, index) => {
          const from = position.get(edge.from); const to = position.get(edge.to);
          if (!from || !to) return null;
          const opacity = interpolate(frame, [index * 8, index * 8 + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return <line key={`${edge.from}-${edge.to}`} x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke={edge.color || accent} strokeWidth={5} opacity={opacity} />;
        })}
        {nodes.map((node, index) => {
          const order = revealOrder.indexOf(node.id); const opacity = interpolate(frame, [Math.max(0, order) * 10, Math.max(0, order) * 10 + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return <g key={node.id} opacity={opacity}>
            <rect x={node.x - 120} y={node.y - 48} width={240} height={96} rx={12} fill="rgba(255,255,255,0.46)" stroke={node.color || accent} strokeWidth={4} />
            <text x={node.x} y={node.y + 10} textAnchor="middle" fontSize={28} fill={theme.textColor}>{node.label}</text>
          </g>;
        })}
      </svg>
    </EditorialCanvas>
  );
};
