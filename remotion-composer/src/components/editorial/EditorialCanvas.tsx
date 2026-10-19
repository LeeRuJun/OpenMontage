import React from "react";
import { AbsoluteFill } from "remotion";
import type { EditorialCanvasProps } from "./types";

export const EditorialCanvas: React.FC<EditorialCanvasProps> = ({
  children,
  theme,
  backgroundColor = "#E9DFC8",
  texture = true,
}) => (
  <AbsoluteFill
    style={{
      overflow: "hidden",
      background: backgroundColor,
      color: theme.textColor,
      fontFamily: "Inter, system-ui, sans-serif",
    }}
  >
    {texture && (
      <AbsoluteFill
        style={{
          opacity: 0.12,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(rgba(67,52,32,0.22) 0.6px, transparent 0.6px)",
          backgroundSize: "7px 7px",
        }}
      />
    )}
    {children}
  </AbsoluteFill>
);
