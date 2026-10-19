import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { EditorialCanvas } from "./EditorialCanvas";
import type { EditorialBaseProps } from "./types";

export interface QuoteCardSceneProps extends EditorialBaseProps {
  text: string;
  attribution?: string;
  accentColor?: string;
}

export const QuoteCardScene: React.FC<QuoteCardSceneProps> = ({ text, attribution, accentColor, theme, durationInFrames }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const opacity = spring({ frame, fps, config: { damping: 20 } });
  return <EditorialCanvas theme={theme} durationInFrames={durationInFrames}>
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", padding: "0 220px", textAlign: "center", opacity }}>
      <div style={{ fontSize: 92, color: accentColor || theme.accentColor, lineHeight: 0.7, alignSelf: "flex-start" }}>“</div>
      <div style={{ fontSize: 54, fontWeight: 800, lineHeight: 1.35 }}>{text}</div>
      {attribution && <div style={{ marginTop: 30, fontSize: 26, opacity: 0.68 }}>— {attribution}</div>}
    </AbsoluteFill>
  </EditorialCanvas>;
};
