import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const A = "ae-style-layered-ai";
const W = 1920;
const fpsConst = 30;

function clamp(v: number, min = 0, max = 1) { return Math.max(min, Math.min(max, v)); }
function between(frame: number, start: number, end: number) { return clamp((frame - start) / (end - start)); }
function ease(t: number) { return t * t * (3 - 2 * t); }

const BG: React.FC<{ src: string; scale?: number; x?: number; y?: number; opacity?: number; brightness?: number }> = ({ src, scale=1, x=0, y=0, opacity=1, brightness=1 }) => (
  <AbsoluteFill style={{ overflow: "hidden", background: "#070B14", opacity }}>
    <Img src={staticFile(`${A}/${src}`)} style={{ width:"100%", height:"100%", objectFit:"cover", transform:`translate(${x}px, ${y}px) scale(${scale})`, filter:`brightness(${brightness})`, willChange:"transform, filter" }} />
  </AbsoluteFill>
);

const RigidCharacter: React.FC<{
  src: string; left: number; top: number; width: number; opacity?: number; baseScale?: number;
  x?: number; y?: number; rotate?: number; breathe?: number; bob?: number; sway?: number; anchor?: string;
}> = ({ src,left,top,width,opacity=1,baseScale=1,x=0,y=0,rotate=0,breathe=0.012,bob=3,sway=0.8,anchor="50% 90%" }) => {
  const frame = useCurrentFrame();
  const scale = baseScale * (1 + Math.sin(frame/13) * breathe);
  const yy = y + Math.sin(frame/10) * bob;
  const rr = rotate + Math.sin(frame/18) * sway;
  return <Img src={staticFile(`${A}/${src}`)} style={{ position:"absolute", left, top, width, opacity, transformOrigin:anchor, transform:`translate(${x}px, ${yy}px) rotate(${rr}deg) scale(${scale})`, filter:"drop-shadow(0 18px 22px rgba(0,0,0,.35))", willChange:"transform, opacity" }} />;
};

const Vignette: React.FC<{ opacity?: number }> = ({ opacity=0.45 }) => <AbsoluteFill style={{ pointerEvents:"none", background:`radial-gradient(ellipse at center, transparent 42%, rgba(0,0,0,${opacity}) 100%)` }} />;

const Caption: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config:{damping:18, stiffness:120} });
  return <AbsoluteFill style={{ justifyContent:"flex-end", alignItems:"center", paddingBottom:70, pointerEvents:"none" }}>
    <div style={{ transform:`translateY(${interpolate(pop,[0,1],[15,0])}px)`, background:"rgba(0,0,0,.75)", borderRadius:10, padding:"13px 31px 15px", boxShadow:"0 10px 30px rgba(0,0,0,.38)" }}>
      <div style={{ color:"#fff", fontSize:42, lineHeight:1.26, fontWeight:900, letterSpacing:".02em", fontFamily:"PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif", textShadow:"0 2px 5px rgba(0,0,0,.75)" }}>{text}</div>
    </div>
  </AbsoluteFill>;
};

const PresenterGesture: React.FC<{ start: number; end: number }> = ({ start, end }) => {
  const f = useCurrentFrame(); const p = ease(between(f,start,end));
  const rot = interpolate(p,[0,1],[-16,5]);
  const op = interpolate(p,[0,0.2,1],[0,0.9,0.75]);
  return <div style={{ position:"absolute", left:1165, top:505, width:150, height:48, borderRadius:28, background:"#F4CBA2", border:"5px solid #1D1D1D", opacity:op, transformOrigin:"0% 50%", transform:`rotate(${rot}deg)`, boxShadow:"0 14px 20px rgba(0,0,0,.25)" }} />;
};

const PaperBill: React.FC<{ start: number; end: number }> = ({ start, end }) => {
  const f=useCurrentFrame(); const p=ease(between(f,start,end));
  return <div style={{ position:"absolute", right:interpolate(p,[0,1],[-310,135]), top:interpolate(p,[0,1],[285,250]), width:285, height:350, background:"#F8F2DF", border:"5px solid #182335", borderRadius:8, opacity:interpolate(p,[0,.18,1],[0,1,1]), transform:`rotate(${interpolate(p,[0,1],[11,-5])}deg)`, boxShadow:"0 20px 42px rgba(0,0,0,.45)", padding:26, fontFamily:"Arial, sans-serif", color:"#203047" }}>
    <div style={{fontSize:34,fontWeight:900}}>BANK</div>
    <div style={{marginTop:22,fontSize:42,color:"#C64242",fontWeight:900}}>351.00</div>
    <div style={{marginTop:34,height:5,background:"#8B95A1",width:"86%"}}/><div style={{marginTop:24,height:5,background:"#A5ADB7",width:"72%"}}/><div style={{marginTop:24,height:5,background:"#A5ADB7",width:"58%"}}/>
  </div>;
};

const FloatingOfficePaper: React.FC = () => {
  const f=useCurrentFrame();
  return <div style={{ position:"absolute", right:295+Math.sin(f/12)*24, top:155+Math.cos(f/15)*22, width:92, height:130, background:"rgba(245,245,235,.84)", border:"3px solid rgba(20,25,35,.85)", transform:`rotate(${Math.sin(f/18)*8}deg)`, boxShadow:"0 12px 24px rgba(0,0,0,.3)" }} />;
};

export const RigidCharacterReplica: React.FC = () => {
  const frame = useCurrentFrame();
  const fOfficeReveal = 70, fOfficeFull = 118, fNight = 150, fBedroom = 202, fBill = 244;
  const libP = ease(between(frame,0,fOfficeReveal));
  const pipP = ease(between(frame,62,fOfficeFull));
  const officeP = ease(between(frame,fOfficeFull,fBedroom));
  const nightP = ease(between(frame,fNight,fBedroom));
  const bedSlide = ease(between(frame,fBedroom,fBedroom+28));
  const bedP = ease(between(frame,fBedroom+18,300));

  let caption = "大家好 今天想跟你聊一本书";
  if (frame >= 72 && frame < 126) caption = "贝克哈吉斯的《管道的故事》";
  else if (frame >= 126 && frame < 204) caption = "你有没有过这种感觉 每天拼命工作";
  else if (frame >= 204 && frame < 250) caption = "加班加点不敢请假";
  else if (frame >= 250) caption = "不敢生病";

  return <AbsoluteFill style={{ background:"#07101E", overflow:"hidden", fontFamily:"PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif" }}>
    {frame < fOfficeFull && <AbsoluteFill style={{ opacity: frame < fOfficeReveal ? 1 : interpolate(frame,[fOfficeReveal,fOfficeFull],[1,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}) }}>
      <BG src="library_bg.png" scale={1.04+libP*0.08} y={-libP*12} />
      <div style={{ position:"absolute", inset:0, background:"radial-gradient(circle at 50% 42%, rgba(255,215,120,.16), transparent 42%)" }} />
      <RigidCharacter src="presenter_sticker.png" left={650} top={250} width={650} breathe={0.01} bob={4} sway={1.0} />
      <PresenterGesture start={12} end={42} />
      <Vignette opacity={0.29} />
    </AbsoluteFill>}

    {frame >= 62 && frame < 130 && <AbsoluteFill style={{ background:"#D9E0E8" }}>
      <BG src="office_day_bg.png" opacity={interpolate(pipP,[0,0.2,1],[0,1,1])} scale={1.07} x={interpolate(pipP,[0,1],[55,-15])} />
      <div style={{ position:"absolute", inset:0, transform:`translate(${interpolate(pipP,[0,1],[0,-420])}px, ${interpolate(pipP,[0,1],[0,-116])}px) scale(${interpolate(pipP,[0,1],[1.0,0.42])})`, transformOrigin:"50% 50%", overflow:"hidden", borderRadius:pipP*20, border:`${pipP*8}px solid rgba(255,255,255,.92)`, boxShadow:`0 22px 60px rgba(0,0,0,${pipP*0.36})` }}>
        <BG src="library_bg.png" scale={1.05} />
        <RigidCharacter src="presenter_sticker.png" left={650} top={250} width={650} breathe={0.006} bob={2} sway={0.4} />
      </div>
      <RigidCharacter src="worker_sticker.png" left={880} top={375} width={620} opacity={interpolate(pipP,[0.25,1],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})} y={interpolate(pipP,[0.25,1],[60,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})} breathe={0.008} bob={2} sway={0.4} />
      <Vignette opacity={0.35} />
    </AbsoluteFill>}

    {frame >= fOfficeFull && frame < fBedroom+32 && <AbsoluteFill style={{ opacity: frame < fBedroom ? 1 : interpolate(frame,[fBedroom,fBedroom+32],[1,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}) }}>
      <BG src="office_day_bg.png" scale={1.11} x={interpolate(officeP,[0,1],[56,-60])} />
      <BG src="office_night_bg.png" opacity={nightP} scale={1.12} x={interpolate(officeP,[0,1],[46,-75])} brightness={0.95} />
      <RigidCharacter src="worker_sticker.png" left={760} top={340} width={710} y={interpolate(nightP,[0,1],[0,26])} rotate={interpolate(nightP,[0,1],[0,-2])} breathe={0.01} bob={frame>fNight?7:3} sway={frame>fNight?1.2:0.5} />
      <AbsoluteFill style={{ background:`linear-gradient(135deg, rgba(5,20,65,${0.12+nightP*0.44}), rgba(0,0,0,${0.04+nightP*0.25}))` }} />
      {frame >= 145 && frame < 204 && <FloatingOfficePaper />}
      <Vignette opacity={0.48} />
    </AbsoluteFill>}

    {frame >= fBedroom && <AbsoluteFill style={{ transform:`translateX(${interpolate(bedSlide,[0,1],[W,0])}px)` }}>
      <BG src="bedroom_bg.png" scale={1.05+bedP*0.12} x={interpolate(bedP,[0,1],[0,-65])} y={interpolate(bedP,[0,1],[0,-15])} />
      <AbsoluteFill style={{ background:"linear-gradient(90deg, rgba(4,12,30,.10), rgba(30,90,180,.16))" }} />
      <RigidCharacter src="bed_phone_sticker.png" left={560} top={410} width={700} x={interpolate(bedP,[0,1],[20,-20])} y={interpolate(bedP,[0,1],[30,0])} rotate={-1.0} breathe={0.008} bob={4} sway={0.8} />
      <PaperBill start={fBill} end={fBill+28} />
      <Vignette opacity={0.56} />
    </AbsoluteFill>}

    <Caption text={caption} />
    <Audio src={staticFile(`${A}/narration_10s.mp3`)} volume={0.94} />
    <Audio src={staticFile(`${A}/music_bed.mp3`)} volume={(f)=>Math.min(interpolate(f,[0,fpsConst*0.7],[0,0.08],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),interpolate(f,[fpsConst*9,fpsConst*10],[0.08,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}))} />
  </AbsoluteFill>;
};
