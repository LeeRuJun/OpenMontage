import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { EditorialCanvas } from "./EditorialCanvas";
import type { EditorialBaseProps, TimelineEvent } from "./types";

export interface TimelineSceneProps extends EditorialBaseProps {
  events: TimelineEvent[];
  activeIndex?: number;
  lineColor?: string;
  title?: string;
}

export const TimelineScene: React.FC<TimelineSceneProps> = ({ events, activeIndex = 0, lineColor, title, theme, durationInFrames }) => {
  const frame = useCurrentFrame();
  const accent = lineColor || theme.accentColor;
  return (
    <EditorialCanvas theme={theme} durationInFrames={durationInFrames}>
      {title && <div style={{ position: "absolute", top: 64, left: 90, fontSize: 54, fontWeight: 800 }}>{title}</div>}
      <div style={{ position: "absolute", left: 150, right: 150, top: 470, height: 8, background: accent }} />
      {events.map((event, index) => {
        const x = events.length === 1 ? 960 : 150 + (1770 / (events.length - 1)) * index;
        const opacity = interpolate(frame, [index * 8, index * 8 + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const active = index === activeIndex;
        return <div key={`${event.label}-${index}`} style={{ position: "absolute", left: x - 100, top: 405, width: 200, textAlign: "center", opacity }}>
          <div style={{ margin: "0 auto", width: active ? 34 : 24, height: active ? 34 : 24, borderRadius: "50%", background: active ? accent : theme.surfaceColor, border: `5px solid ${accent}` }} />
          {event.year && <div style={{ marginTop: 28, fontSize: 28, fontWeight: 800, color: accent }}>{event.year}</div>}
          <div style={{ marginTop: 8, fontSize: 26, fontWeight: 700 }}>{event.label}</div>
          {event.detail && <div style={{ marginTop: 8, fontSize: 20, opacity: 0.72 }}>{event.detail}</div>}
        </div>;
      })}
    </EditorialCanvas>
  );
};
