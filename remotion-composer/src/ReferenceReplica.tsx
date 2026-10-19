import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const fps30 = 30;
const A = "ae-style-no-ae-sample-ai";

function clamp(v: number, min = 0, max = 1) {
  return Math.max(min, Math.min(max, v));
}

function between(frame: number, start: number, end: number) {
  return clamp((frame - start) / (end - start));
}

function ease(t: number) {
  return t * t * (3 - 2 * t);
}

const ShadowVignette: React.FC<{ opacity?: number }> = ({ opacity = 0.48 }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: `radial-gradient(ellipse at center, transparent 43%, rgba(0,0,0,${opacity}) 100%)`,
    }}
  />
);

const SceneImage: React.FC<{
  src: string;
  opacity?: number;
  scale?: number;
  x?: number;
  y?: number;
  blur?: number;
}> = ({ src, opacity = 1, scale = 1, x = 0, y = 0, blur = 0 }) => (
  <AbsoluteFill style={{ overflow: "hidden", background: "#050812" }}>
    <Img
      src={staticFile(`${A}/${src}`)}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "cover",
        opacity,
        filter: blur ? `blur(${blur}px)` : undefined,
        transform: `translate(${x}px, ${y}px) scale(${scale})`,
        willChange: "transform, opacity, filter",
      }}
    />
  </AbsoluteFill>
);

const Caption: React.FC<{ text: string; active?: boolean }> = ({ text, active = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 18, stiffness: 120 } });
  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 70,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          opacity: active ? 1 : 0,
          transform: `translateY(${interpolate(pop, [0, 1], [16, 0])}px)`,
          background: "rgba(0,0,0,0.74)",
          borderRadius: 10,
          padding: "13px 30px 15px",
          boxShadow: "0 10px 28px rgba(0,0,0,0.35)",
          maxWidth: 1360,
        }}
      >
        <div
          style={{
            color: "white",
            fontSize: 42,
            lineHeight: 1.28,
            fontWeight: 800,
            letterSpacing: "0.02em",
            textShadow: "0 2px 5px rgba(0,0,0,0.7)",
            fontFamily: 'PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif',
          }}
        >
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const FloatingPaper: React.FC<{ start: number; end: number }> = ({ start, end }) => {
  const frame = useCurrentFrame();
  const p = ease(between(frame, start, end));
  const x = interpolate(p, [0, 1], [310, 0]);
  const y = interpolate(p, [0, 1], [-50, 0]);
  const rot = interpolate(p, [0, 1], [10, -5]);
  const op = interpolate(p, [0, 0.25, 1], [0, 1, 1]);
  return (
    <div
      style={{
        position: "absolute",
        right: 165 + x,
        top: 245 + y,
        width: 260,
        height: 330,
        opacity: op,
        transform: `rotate(${rot}deg)`,
        background: "#F8F2DF",
        border: "5px solid #182335",
        boxShadow: "0 20px 40px rgba(0,0,0,.45)",
        borderRadius: 8,
        padding: 26,
        fontFamily: 'Arial, sans-serif',
        color: "#203047",
      }}
    >
      <div style={{ fontSize: 34, fontWeight: 900 }}>BANK</div>
      <div style={{ marginTop: 22, fontSize: 42, color: "#C64242", fontWeight: 900 }}>351.00</div>
      <div style={{ marginTop: 34, height: 5, background: "#8B95A1", width: "86%" }} />
      <div style={{ marginTop: 24, height: 5, background: "#A5ADB7", width: "72%" }} />
      <div style={{ marginTop: 24, height: 5, background: "#A5ADB7", width: "58%" }} />
    </div>
  );
};

const WarmToColdOverlay: React.FC<{ start: number; end: number }> = ({ start, end }) => {
  const frame = useCurrentFrame();
  const p = ease(between(frame, start, end));
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, rgba(5,20,65,${0.15 + p * 0.46}), rgba(0,0,0,${0.05 + p * 0.28}))`,
        pointerEvents: "none",
      }}
    />
  );
};

const LibraryToOffice: React.FC = () => {
  const frame = useCurrentFrame();
  const t = ease(between(frame, 68, 112));
  const officeOpacity = interpolate(t, [0, 0.25, 1], [0, 1, 1]);
  const libScale = interpolate(t, [0, 1], [1.1, 0.42]);
  const libX = interpolate(t, [0, 1], [0, -420]);
  const libY = interpolate(t, [0, 1], [0, -115]);
  const border = interpolate(t, [0, 0.45, 1], [0, 0, 1]);
  const officeScale = 1.08 + t * 0.04;
  return (
    <AbsoluteFill style={{ background: "#D8DEE8", overflow: "hidden" }}>
      <SceneImage src="office_day.png" opacity={officeOpacity} scale={officeScale} x={interpolate(t, [0, 1], [60, -10])} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${libX}px, ${libY}px) scale(${libScale})`,
          transformOrigin: "50% 50%",
          boxShadow: border ? "0 20px 60px rgba(0,0,0,.35)" : "none",
          border: border ? "8px solid rgba(255,255,255,.9)" : "0px solid transparent",
          overflow: "hidden",
          borderRadius: border ? 20 : 0,
        }}
      >
        <SceneImage src="library_presenter.png" scale={1.04 + t * 0.03} />
      </div>
      <ShadowVignette opacity={0.38} />
    </AbsoluteFill>
  );
};

export const ReferenceReplica: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Frame timing, matched to the 10s reference structure.
  const f0 = 0;
  const fLibraryEnd = 70;   // 2.33s
  const fOfficeRevealEnd = 116; // 3.87s
  const fNightStart = 150;  // 5.0s
  const fBedroomStart = 202; // 6.73s
  const fBillStart = 244;   // 8.13s

  const libraryP = ease(between(frame, f0, fLibraryEnd));
  const officeP = ease(between(frame, fOfficeRevealEnd, fBedroomStart));
  const nightMix = ease(between(frame, fNightStart, fBedroomStart));
  const bedroomSlide = ease(between(frame, fBedroomStart, fBedroomStart + 28));
  const bedroomP = ease(between(frame, fBedroomStart + 18, 300));

  let caption = "大家好 今天想跟你聊一本书";
  if (frame >= 72 && frame < 126) caption = "贝克哈吉斯的《管道的故事》";
  else if (frame >= 126 && frame < 204) caption = "你有没有过这种感觉 每天拼命工作";
  else if (frame >= 204 && frame < 250) caption = "加班加点不敢请假";
  else if (frame >= 250) caption = "不敢生病";

  return (
    <AbsoluteFill style={{ background: "#050812", overflow: "hidden", fontFamily: 'PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif' }}>
      {/* 0-2.3s: warm library presenter with subtle push-in */}
      {frame < fOfficeRevealEnd && (
        <AbsoluteFill style={{ opacity: frame < fLibraryEnd ? 1 : interpolate(frame, [fLibraryEnd, fOfficeRevealEnd], [1, 0.0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          <SceneImage src="library_presenter.png" scale={1.02 + libraryP * 0.08} x={libraryP * -18} y={libraryP * -8} />
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "radial-gradient(circle at 50% 40%, rgba(255,215,120,.16), transparent 42%)",
            }}
          />
          <ShadowVignette opacity={0.30} />
        </AbsoluteFill>
      )}

      {/* 2.3-3.9s: the exact reference-like PiP shrink into office */}
      {frame >= 62 && frame < 128 && <LibraryToOffice />}

      {/* 3.9-6.7s: office pan + day-to-night pressure */}
      {frame >= fOfficeRevealEnd && frame < fBedroomStart + 32 && (
        <AbsoluteFill style={{ opacity: frame < fBedroomStart ? 1 : interpolate(frame, [fBedroomStart, fBedroomStart + 32], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
          <SceneImage src="office_day.png" scale={1.1} x={interpolate(officeP, [0, 1], [50, -55])} />
          <SceneImage src="office_night.png" opacity={nightMix} scale={1.12} x={interpolate(officeP, [0, 1], [40, -70])} />
          <WarmToColdOverlay start={fNightStart - 18} end={fBedroomStart} />
          <ShadowVignette opacity={0.50} />
        </AbsoluteFill>
      )}

      {/* 6.7-10s: bedroom slides in from right, then pushes in to bill/phone */}
      {frame >= fBedroomStart && (
        <AbsoluteFill
          style={{
            transform: `translateX(${interpolate(bedroomSlide, [0, 1], [1920, 0])}px)`,
          }}
        >
          <SceneImage src="bedroom_bill.png" scale={1.05 + bedroomP * 0.13} x={interpolate(bedroomP, [0, 1], [0, -70])} y={interpolate(bedroomP, [0, 1], [0, -20])} />
          <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(4,12,30,.12), rgba(30,90,180,.16))" }} />
          <FloatingPaper start={fBillStart} end={fBillStart + 28} />
          <ShadowVignette opacity={0.56} />
        </AbsoluteFill>
      )}

      {/* Mild floating paper layer during office pressure, like simple AE foreground assets */}
      {frame >= 145 && frame < 204 && (
        <div
          style={{
            position: "absolute",
            right: 300 + Math.sin(frame / 12) * 20,
            top: 160 + Math.cos(frame / 15) * 20,
            width: 90,
            height: 130,
            background: "rgba(245,245,235,.82)",
            border: "3px solid rgba(20,25,35,.8)",
            transform: `rotate(${Math.sin(frame / 18) * 7}deg)`,
            boxShadow: "0 12px 24px rgba(0,0,0,.28)",
          }}
        />
      )}

      <Caption text={caption} />

      <Audio src={staticFile(`${A}/narration_10s.mp3`)} volume={0.94} />
      <Audio
        src={staticFile(`${A}/music_bed.mp3`)}
        volume={(f) => {
          const fadeIn = interpolate(f, [0, fps * 0.7], [0, 0.08], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const fadeOut = interpolate(f, [fps * 9, fps * 10], [0.08, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return Math.min(fadeIn, fadeOut);
        }}
      />
    </AbsoluteFill>
  );
};
