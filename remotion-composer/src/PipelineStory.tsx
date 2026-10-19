import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Sequence,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/SpaceGrotesk";

const { fontFamily } = loadFont();

// ── Character: Pipeline Worker (SVG flat illustration) ─────────

const Character: React.FC<{ frame: number }> = ({ frame }) => {
  const bob = Math.sin(frame * 0.08) * 6;

  // Entry animation
  const entry = spring({ frame, fps: 30, config: { damping: 14, stiffness: 60, mass: 1 } });
  const charX = interpolate(entry, [0, 1], [-300, 0]);
  const charOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  return (
    <g transform={`translate(${charX}, 0)`} opacity={charOpacity}>
      {/* BODY GROUP — bobs up and down */}
      <g transform={`translate(0, ${bob})`}>
        {/* Shadow under feet */}
        <ellipse cx="0" cy="170" rx="70" ry="12" fill="rgba(0,0,0,0.15)" />

        {/* Left shoe */}
        <path d="M-35,155 Q-55,155 -55,165 Q-55,175 -35,175 L-15,175 L-15,155 Z" fill="#2d2d2d" />
        {/* Right shoe */}
        <path d="M15,155 Q55,155 55,165 Q55,175 15,175 L-15,175 L-15,155 Z" fill="#2d2d2d" />

        {/* Left leg */}
        <rect x="-38" y="100" width="28" height="60" rx="10" fill="#4a5568" />
        {/* Right leg */}
        <rect x="10" y="100" width="28" height="60" rx="10" fill="#4a5568" />

        {/* Body / torso */}
        <rect x="-50" y="25" width="100" height="85" rx="16" fill="#f08c00" />
        {/* Shirt collar detail */}
        <path d="M-20,25 L0,50 L20,25" fill="none" stroke="#e8590c" strokeWidth="3" strokeLinecap="round" />
        {/* Belt */}
        <rect x="-50" y="95" width="100" height="10" rx="3" fill="#d9480f" />

        {/* Left arm — holding wrench */}
        <g transform="translate(-50, 35) rotate(-25)">
          {/* Sleeve */}
          <rect x="-10" y="-8" width="24" height="50" rx="10" fill="#e8590c" />
          {/* Hand/skin */}
          <circle cx="6" cy="50" r="14" fill="#ffd8a8" />
          {/* Wrench */}
          <g transform="translate(6, 50) rotate(15)">
            <rect x="-4" y="-60" width="8" height="60" rx="3" fill="#95a5a6" />
            <path d="M-16,-60 L-16,-75 Q-16,-85 -8,-85 Q0,-85 0,-75 L0,-60 Z" fill="#7f8c8d" />
            <path d="M0,-60 L16,-60 L16,-75 Q16,-85 8,-85 Q0,-85 0,-75 Z" fill="#7f8c8d" />
          </g>
        </g>

        {/* Right arm */}
        <g transform="translate(50, 35) rotate(15)">
          <rect x="-14" y="-8" width="24" height="55" rx="10" fill="#e8590c" />
          {/* Hand — pointing */}
          <circle cx="-2" cy="55" r="14" fill="#ffd8a8" />
        </g>

        {/* Head */}
        <circle cx="0" cy="5" r="35" fill="#ffd8a8" />
        {/* Hair */}
        <path
          d="M-35,5 Q-35,-35 -15,-38 Q0,-42 15,-38 Q35,-35 35,5 Q35,-10 15,-15 Q0,-20 -15,-15 Q-35,-10 -35,5 Z"
          fill="#2d2d2d"
        />
        {/* Hair top volume */}
        <ellipse cx="-5" cy="-26" rx="22" ry="10" fill="#2d2d2d" />

        {/* Glasses */}
        <circle cx="-12" cy="0" r="11" fill="none" stroke="#2d2d2d" strokeWidth="2.5" />
        <circle cx="12" cy="0" r="11" fill="none" stroke="#2d2d2d" strokeWidth="2.5" />
        <line x1="-1" y1="0" x2="1" y2="0" stroke="#2d2d2d" strokeWidth="2.5" />

        {/* Eyes */}
        <circle cx="-10" cy="-2" r="3" fill="#2d2d2d" />
        <circle cx="14" cy="-2" r="3" fill="#2d2d2d" />

        {/* Smile */}
        <path d="M-6,10 Q0,18 6,10" fill="none" stroke="#c0392b" strokeWidth="2" strokeLinecap="round" />
      </g>
    </g>
  );
};

// ── Decorative Scene Elements ──────────────────────────────────

const Coins: React.FC<{ frame: number }> = ({ frame }) => {
  const coins = [
    { cx: 100, cy: 600, delay: 20, color: "#fcc419", size: 18 },
    { cx: 300, cy: 500, delay: 35, color: "#ffd43b", size: 14 },
    { cx: 150, cy: 450, delay: 50, color: "#fcc419", size: 16 },
    { cx: 250, cy: 650, delay: 15, color: "#fab005", size: 12 },
    { cx: 180, cy: 400, delay: 45, color: "#ffd43b", size: 15 },
  ];

  return (
    <g>
      {coins.map((coin, i) => {
        const delay = coin.delay;
        const coinSpring = spring({
          frame: Math.max(0, frame - delay),
          fps: 30,
          config: { damping: 12, stiffness: 70, mass: 1 },
        });
        const y = interpolate(coinSpring, [0, 1], [200, 0]);
        const opacity = interpolate(coinSpring, [0, 1], [0, 1]);
        const rotate = interpolate(frame, [delay, delay + 60], [0, 360]);
        return (
          <g key={i} transform={`translate(${coin.cx}, ${coin.cy + y})`} opacity={opacity}>
            <circle
              cx={0} cy={0} r={coin.size}
              fill={coin.color}
              stroke="rgba(255,255,255,0.3)"
              strokeWidth="2"
              transform={`rotate(${rotate})`}
            />
            <text
              x={0} y={coin.size * 0.35}
              textAnchor="middle"
              fill="rgba(0,0,0,0.4)"
              fontSize={coin.size * 0.8}
              fontWeight="bold"
              transform={`rotate(${rotate})`}
            >
              ¥
            </text>
          </g>
        );
      })}
    </g>
  );
};

const Bubbles: React.FC<{ frame: number }> = ({ frame }) => {
  const bubbles = [
    { cx: 80, cy: 400, delay: 0, r: 8 },
    { cx: 60, cy: 350, delay: 10, r: 5 },
    { cx: 100, cy: 320, delay: 20, r: 10 },
    { cx: 50, cy: 280, delay: 30, r: 6 },
    { cx: 90, cy: 240, delay: 40, r: 7 },
  ];
  return (
    <g>
      {bubbles.map((b, i) => {
        const s = spring({ frame: Math.max(0, frame - b.delay), fps: 30, config: { damping: 15, stiffness: 40 } });
        const y = interpolate(s, [0, 1], [100, 0]);
        const opacity = interpolate(s, [0, 0.2, 1], [0, 0.6, 0]);
        return <circle key={i} cx={b.cx} cy={b.cy - y} r={b.r} fill="none" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" opacity={opacity} />;
      })}
    </g>
  );
};

// ── Title Scene ────────────────────────────────────────────────

const TitleReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const titleSpring = spring({ frame, fps: 30, config: { damping: 12, stiffness: 80, mass: 1 } });
  const scale = interpolate(titleSpring, [0, 1], [0.6, 1]);
  const bgOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  const glowAlpha = interpolate(frame, [15, 30, 45, 60], [0, 0.15, 0.05, 0]);

  return (
    <AbsoluteFill style={{ background: "linear-gradient(135deg, #e8590c 0%, #f08c00 30%, #e67700 60%, #d9480f 100%)", display: "flex", alignItems: "center", justifyContent: "center", opacity: bgOpacity }}>
      {/* Background pipes */}
      <svg style={{ position: "absolute", width: "100%", height: "100%", top: 0, left: 0 }} viewBox="0 0 1920 1080">
        <line x1={0} y1={540} x2={interpolate(frame, [10, 35], [0, 600], { extrapolateRight: "clamp" })} y2={540} stroke="rgba(255,255,255,0.12)" strokeWidth="4" strokeLinecap="round" />
        <line x1={interpolate(frame, [20, 45], [1320, 1920], { extrapolateRight: "clamp" })} y1={540} x2={1920} y2={540} stroke="rgba(255,255,255,0.12)" strokeWidth="4" strokeLinecap="round" />
        <circle cx={interpolate(frame, [15, 55], [600, 1320], { extrapolateRight: "clamp" })} cy={540} r={6} fill="rgba(255,255,255,0.3)" />
      </svg>
      {/* Glow */}
      <div style={{ position: "absolute", width: 600, height: 600, borderRadius: "50%", background: `radial-gradient(circle, rgba(255,255,255,${glowAlpha}) 0%, transparent 70%)`, top: "30%", left: "50%", transform: "translate(-50%, -50%)" }} />
      {/* Title */}
      <div style={{ transform: `scale(${scale})`, textAlign: "center", zIndex: 10 }}>
        <h1 style={{ fontFamily, fontSize: 88, fontWeight: 900, color: "#fff", textShadow: "0 4px 24px rgba(0,0,0,0.3)", margin: 0, lineHeight: 1.1, letterSpacing: 6 }}>管道的故事</h1>
      </div>
    </AbsoluteFill>
  );
};

const SubtitleReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const subSpring = spring({ frame, fps: 30, config: { damping: 15, stiffness: 60, mass: 1 } });
  const y = interpolate(subSpring, [0, 1], [80, 0]);
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", bottom: 180, width: "100%", display: "flex", justifyContent: "center", opacity, transform: `translateY(${y}px)` }}>
      <div style={{ fontFamily, fontSize: 36, fontWeight: 600, color: "rgba(255,255,255,0.92)", letterSpacing: 4, textShadow: "0 2px 12px rgba(0,0,0,0.2)" }}>从打工人到自由人的跃迁</div>
    </div>
  );
};

// ── Scene 2: Character showcase with pipeline —──────────────────

const CharacterShowcase: React.FC = () => {
  const frame = useCurrentFrame();
  const bgShift = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
  const titleOpacity = interpolate(frame, [15, 30], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: "linear-gradient(180deg, #0b3d5c 0%, #0d4f75 40%, #116c9c 80%, #1485b8 100%)", opacity: bgShift, display: "flex", alignItems: "center", justifyContent: "center" }}>
      {/* Big pipeline background */}
      <svg style={{ position: "absolute", width: "100%", height: "100%", top: 0, left: 0 }} viewBox="0 0 1920 1080">
        {/* Main pipeline */}
        <path d="M0,700 Q480,650 960,700 Q1440,750 1920,700" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="80" strokeLinecap="round" />
        <path d="M0,700 Q480,650 960,700 Q1440,750 1920,700" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="4" strokeLinecap="round" strokeDasharray={`${interpolate(frame, [30, 90], [0, 40], { extrapolateRight: "clamp" })} 12`} />
        {/* Flow dot */}
        <circle cx={interpolate(frame, [20, 150], [0, 1920], { extrapolateRight: "clamp" })} cy={700} r="8" fill="rgba(20, 184, 166, 0.4)" />
      </svg>

      {/* Coins floating around */}
      <svg style={{ position: "absolute", width: "100%", height: "100%", top: 0, left: 0 }} viewBox="0 0 1920 1080">
        <Coins frame={frame} />
        <Bubbles frame={frame} />
      </svg>

      {/* Title */}
      <div style={{ position: "absolute", top: 60, opacity: titleOpacity, fontFamily, fontSize: 48, fontWeight: 800, color: "#fff", letterSpacing: 4, zIndex: 10 }}>
        建造管道，而非提水
      </div>

      {/* Character in center */}
      <svg style={{ width: 400, height: 400, position: "absolute", left: "50%", top: "55%", transform: "translate(-50%, -50%)" }} viewBox="-200 -250 400 400">
        <Character frame={frame} />
      </svg>

      {/* Side labels */}
      <div style={{ position: "absolute", left: 80, top: "45%", opacity: interpolate(frame, [45, 60], [0, 1], { extrapolateRight: "clamp" }), fontFamily, fontSize: 24, color: "rgba(255,255,255,0.5)" }}>
        ☕ 提水 → 用时间换钱
      </div>
      <div style={{ position: "absolute", right: 80, top: "45%", opacity: interpolate(frame, [55, 70], [0, 1], { extrapolateRight: "clamp" }), fontFamily, fontSize: 24, color: "rgba(255,255,255,0.5)" }}>
        管道 → 让钱自动流 ☕
      </div>

      {/* Bottom cards */}
      <div style={{ position: "absolute", bottom: 60, display: "flex", gap: 40 }}>
        {[
          { label: "提水", desc: "时间换钱", delay: 60, color: "#e8590c" },
          { label: "管道", desc: "自动流入", delay: 75, color: "#0ca678" },
          { label: "自由", desc: "不再为钱工作", delay: 90, color: "#fcc419" },
        ].map((card, i) => {
          const s = spring({ frame: Math.max(0, frame - card.delay), fps: 30, config: { damping: 14, stiffness: 70 } });
          return (
            <div key={i} style={{
              opacity: interpolate(s, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(s, [0, 1], [40, 0])}px)`,
              background: "rgba(255,255,255,0.07)", backdropFilter: "blur(12px)",
              borderRadius: 16, border: "1px solid rgba(255,255,255,0.1)",
              padding: "20px 32px", textAlign: "center", width: 160,
            }}>
              <div style={{ fontFamily, fontSize: 22, fontWeight: 700, color: card.color, marginBottom: 4 }}>{card.label}</div>
              <div style={{ fontFamily, fontSize: 16, color: "rgba(255,255,255,0.55)" }}>{card.desc}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: Book callout —─────────────────────────────────────

const BookCallout: React.FC = () => {
  const frame = useCurrentFrame();

  // Transition background from blue to dark
  const bg = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });

  const bookSpring = spring({ frame: Math.max(0, frame - 5), fps: 30, config: { damping: 14, stiffness: 60, mass: 1 } });
  const textOpacity = interpolate(frame, [20, 35], [0, 1], { extrapolateRight: "clamp" });
  const tagOpacity = interpolate(frame, [30, 45], [0, 1], { extrapolateRight: "clamp" });
  const charFloat = Math.sin(frame * 0.05) * 5;

  return (
    <AbsoluteFill style={{ background: "rgb(11, 61, 92)", opacity: bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      {/* Book cover */}
      <div style={{
        transform: `scale(${interpolate(bookSpring, [0, 1], [0.7, 1])})`,
        opacity: interpolate(bookSpring, [0, 1], [0, 1]),
        background: "linear-gradient(135deg, #e8590c 0%, #f08c00 50%, #e67700 100%)",
        width: 300, height: 380, borderRadius: "8px 24px 24px 8px",
        boxShadow: "0 20px 60px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.15)",
        position: "absolute", left: 200, top: 350,
      }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 8, background: "rgba(0,0,0,0.1)", borderTopLeftRadius: 8, borderBottomLeftRadius: 24 }} />
        <div style={{ position: "absolute", left: 40, top: 60, right: 30, fontFamily, fontSize: 36, fontWeight: 900, color: "#fff", lineHeight: 1.3, letterSpacing: 3 }}>
          管道<br />的<br />故事
        </div>
      </div>

      {/* Quote text */}
      <div style={{ position: "absolute", left: 560, top: 350, opacity: textOpacity }}>
        <div style={{ fontFamily, fontSize: 32, fontWeight: 700, color: "rgba(255,255,255,0.9)", marginBottom: 12, letterSpacing: 2 }}>改变你的财富思维</div>
        <div style={{ fontFamily, fontSize: 20, color: "rgba(255,255,255,0.6)", lineHeight: 1.8, letterSpacing: 1 }}>
          你的管道就是你的生命线<br />今天就开始建造
        </div>
      </div>

      {/* Small character peek */}
      <svg style={{ position: "absolute", right: 100, bottom: 120, width: 200, height: 200, transform: `translateY(${charFloat}px)` }} viewBox="-150 -200 300 300">
        <g opacity={textOpacity}>
          <circle cx="0" cy="-120" r="28" fill="#ffd8a8" />
          <rect x="-35" y="-90" width="70" height="55" rx="12" fill="#f08c00" />
          {/* Tiny thumbs up */}
          <circle cx="20" cy="-30" r="12" fill="#ffd8a8" />
          <text x="12" y="-23" fontSize="16" fill="rgba(0,0,0,0.3)" transform="rotate(-30, 20, -30)">👍</text>
        </g>
      </svg>

      {/* Bottom tag */}
      <div style={{ position: "absolute", bottom: 100, opacity: tagOpacity, fontFamily, fontSize: 22, color: "rgba(255,255,255,0.5)", letterSpacing: 4 }}>
        帆书 · 樊登讲书
      </div>
    </AbsoluteFill>
  );
};

// ── Composition ───────────────────────────────────────────────

export const PipelineStory: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#0b3d5c" }}>
      <Sequence from={0} durationInFrames={75}>
        <TitleReveal />
        <SubtitleReveal />
      </Sequence>
      <Sequence from={60} durationInFrames={150}>
        <CharacterShowcase />
      </Sequence>
      <Sequence from={180} durationInFrames={120}>
        <BookCallout />
      </Sequence>
    </AbsoluteFill>
  );
};

export const PIPELINE_STORY_DURATION = 300;
