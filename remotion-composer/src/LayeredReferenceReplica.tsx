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

const A = "ae-style-head-overlays";
const W = 1920;
const H = 1080;
const fpsConst = 30;

function clamp(v: number, min = 0, max = 1) { return Math.max(min, Math.min(max, v)); }
function between(frame: number, start: number, end: number) { return clamp((frame - start) / (end - start)); }
function ease(t: number) { return t * t * (3 - 2 * t); }

const BG: React.FC<{ src: string; scale?: number; x?: number; y?: number; opacity?: number; brightness?: number }> = ({ src, scale=1, x=0, y=0, opacity=1, brightness=1 }) => (
  <AbsoluteFill style={{ overflow: "hidden", background: "#070B14", opacity }}>
    <Img src={staticFile(`${A}/${src}`)} style={{ width:"100%", height:"100%", objectFit:"cover", transform:`translate(${x}px, ${y}px) scale(${scale})`, filter:`brightness(${brightness})`, willChange:"transform, filter" }} />
  </AbsoluteFill>
);

const Character: React.FC<{ src: string; left: number; top: number; width: number; opacity?: number; scale?: number; rotate?: number; x?: number; y?: number; breathing?: boolean; nod?: number; anchor?: string }> = ({ src,left,top,width,opacity=1,scale=1,rotate=0,x=0,y=0,breathing=false,nod=0,anchor="50% 90%" }) => {
  const frame = useCurrentFrame();
  const breath = breathing ? 1 + Math.sin(frame/12)*0.012 : 1;
  const nodY = nod ? Math.sin(frame/10)*nod : 0;
  return <Img src={staticFile(`${A}/${src}`)} style={{ position:"absolute", left, top, width, opacity, transformOrigin:anchor, transform:`translate(${x}px, ${y+nodY}px) rotate(${rotate}deg) scale(${scale*breath})`, filter:"drop-shadow(0 18px 22px rgba(0,0,0,.35))", willChange:"transform, opacity" }} />;
};

const HeadOverlay: React.FC<{ src: string; left: number; top: number; width: number; rotateAmp?: number; yAmp?: number; xAmp?: number; baseRotate?: number; delay?: number }> = ({ src,left,top,width,rotateAmp=2,yAmp=5,xAmp=0,baseRotate=0,delay=0 }) => {
  const frame = useCurrentFrame();
  const t = frame + delay;
  const rot = baseRotate + Math.sin(t/11) * rotateAmp;
  const y = Math.sin(t/9) * yAmp;
  const x = Math.cos(t/13) * xAmp;
  return <Img src={staticFile(`${A}/${src}`)} style={{ position:"absolute", left, top, width, transformOrigin:"50% 80%", transform:`translate(${x}px, ${y}px) rotate(${rot}deg)`, filter:"drop-shadow(0 8px 8px rgba(0,0,0,.18))", willChange:"transform" }} />;
};

const Vignette: React.FC<{ opacity?: number }> = ({ opacity=.45 }) => <AbsoluteFill style={{ pointerEvents:"none", background:`radial-gradient(ellipse at center, transparent 42%, rgba(0,0,0,${opacity}) 100%)` }} />;

const Caption: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config:{damping:18, stiffness:120} });
  return <AbsoluteFill style={{ justifyContent:"flex-end", alignItems:"center", paddingBottom:70, pointerEvents:"none" }}>
    <div style={{ transform:`translateY(${interpolate(pop,[0,1],[15,0])}px)`, background:"rgba(0,0,0,.75)", borderRadius:10, padding:"13px 31px 15px", boxShadow:"0 10px 30px rgba(0,0,0,.38)" }}>
      <div style={{ color:"#fff", fontSize:42, lineHeight:1.26, fontWeight:900, letterSpacing:".02em", fontFamily:"PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif", textShadow:"0 2px 5px rgba(0,0,0,.75)" }}>{text}</div>
    </div>
  </AbsoluteFill>;
};

const PresenterArmGhost: React.FC<{ start: number; end: number }> = ({ start, end }) => {
  // fake extra hand motion: a warm outlined gesture card that swings near the presenter hand.
  const f = useCurrentFrame(); const p = ease(between(f,start,end));
  const rot = interpolate(p,[0,1],[-18,6]);
  const op = interpolate(p,[0,0.2,1],[0,0.95,0.88]);
  return <div style={{ position:"absolute", left:1160, top:505, width:160, height:52, borderRadius:30, background:"#F4CBA2", border:"5px solid #1D1D1D", opacity:op, transformOrigin:"0% 50%", transform:`rotate(${rot}deg)`, boxShadow:"0 14px 20px rgba(0,0,0,.25)" }} />;
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

export const LayeredReferenceReplica: React.FC = () => {
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
    {/* Opening library: real separate BG + presenter sticker breathing, nodding, fake arm swing */}
    {frame < fOfficeFull && <AbsoluteFill style={{ opacity: frame < fOfficeReveal ? 1 : interpolate(frame,[fOfficeReveal,fOfficeFull],[1,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}) }}>
      <BG src="library_bg.png" scale={1.04+libP*.08} y={-libP*12} />
      <div style={{ position:"absolute", inset:0, background:"radial-gradient(circle at 50% 42%, rgba(255,215,120,.16), transparent 42%)" }} />
      <Character src="presenter_sticker.png" left={650} top={250} width={650} breathing nod={3} y={Math.sin(frame/18)*4} />
      <HeadOverlay src="presenter_head_overlay.png" left={802} top={278} width={350} rotateAmp={2.8} yAmp={7} xAmp={2} />
      <PresenterArmGhost start={12} end={42} />
      <Vignette opacity={0.29} />
    </AbsoluteFill>}

    {/* PiP shrink: separate library composite shrinks into office */}
    {frame >= 62 && frame < 130 && <AbsoluteFill style={{ background:"#D9E0E8" }}>
      <BG src="office_day_bg.png" opacity={interpolate(pipP,[0,.2,1],[0,1,1])} scale={1.07} x={interpolate(pipP,[0,1],[55,-15])} />
      <div style={{ position:"absolute", inset:0, transform:`translate(${interpolate(pipP,[0,1],[0,-420])}px, ${interpolate(pipP,[0,1],[0,-116])}px) scale(${interpolate(pipP,[0,1],[1.0,.42])})`, transformOrigin:"50% 50%", overflow:"hidden", borderRadius:pipP*20, border:`${pipP*8}px solid rgba(255,255,255,.92)`, boxShadow:`0 22px 60px rgba(0,0,0,${pipP*.36})` }}>
        <BG src="library_bg.png" scale={1.05} />
        <Character src="presenter_sticker.png" left={650} top={250} width={650} breathing />
        <HeadOverlay src="presenter_head_overlay.png" left={802} top={278} width={350} rotateAmp={2.2} yAmp={5} />
      </div>
      <Character src="worker_sticker.png" left={880} top={375} width={620} opacity={interpolate(pipP,[.25,1],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})} breathing nod={2} y={interpolate(pipP,[.25,1],[60,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})} />
      <HeadOverlay src="worker_head_overlay.png" left={1061} top={390} width={254} rotateAmp={1.6} yAmp={4} baseRotate={-1} delay={9} />
      <Vignette opacity={0.35} />
    </AbsoluteFill>}

    {/* Office work: background pans, worker breathes/nods downward, night overlay crossfades */}
    {frame >= fOfficeFull && frame < fBedroom+32 && <AbsoluteFill style={{ opacity: frame < fBedroom ? 1 : interpolate(frame,[fBedroom,fBedroom+32],[1,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}) }}>
      <BG src="office_day_bg.png" scale={1.11} x={interpolate(officeP,[0,1],[56,-60])} />
      <BG src="office_night_bg.png" opacity={nightP} scale={1.12} x={interpolate(officeP,[0,1],[46,-75])} brightness={.95} />
      <Character src="worker_sticker.png" left={760} top={340} width={710} breathing nod={frame>fNight?5:2} y={interpolate(nightP,[0,1],[0,24])} rotate={interpolate(nightP,[0,1],[0,-1.5])} />
      <HeadOverlay src="worker_head_overlay.png" left={968} top={357 + interpolate(nightP,[0,1],[0,20])} width={291} rotateAmp={frame>fNight?3.0:1.5} yAmp={frame>fNight?8:4} baseRotate={interpolate(nightP,[0,1],[0,-3])} delay={12} />
      <AbsoluteFill style={{ background:`linear-gradient(135deg, rgba(5,20,65,${.12+nightP*.44}), rgba(0,0,0,${.04+nightP*.25}))` }} />
      {frame >= 145 && frame < 204 && <FloatingOfficePaper />}
      <Vignette opacity={0.48} />
    </AbsoluteFill>}

    {/* Bedroom: slide in, character layer moves independently, phone/body tremor, bill slides */}
    {frame >= fBedroom && <AbsoluteFill style={{ transform:`translateX(${interpolate(bedSlide,[0,1],[W,0])}px)` }}>
      <BG src="bedroom_bg.png" scale={1.05+bedP*.12} x={interpolate(bedP,[0,1],[0,-65])} y={interpolate(bedP,[0,1],[0,-15])} />
      <AbsoluteFill style={{ background:"linear-gradient(90deg, rgba(4,12,30,.10), rgba(30,90,180,.16))" }} />
      <Character src="bed_phone_sticker.png" left={560} top={410} width={700} breathing nod={2.5} x={interpolate(bedP,[0,1],[20,-20])} y={interpolate(bedP,[0,1],[30,0]) + Math.sin(frame/7)*2} rotate={Math.sin(frame/20)*.8} />
      <HeadOverlay src="bed_phone_head_overlay.png" left={765 + interpolate(bedP,[0,1],[20,-20])} top={424 + interpolate(bedP,[0,1],[30,0])} width={294} rotateAmp={2.6} yAmp={5} baseRotate={-1.5} delay={18} />
      <PaperBill start={fBill} end={fBill+28} />
      <Vignette opacity={0.56} />
    </AbsoluteFill>}

    <Caption text={caption} />
    <Audio src={staticFile(`${A}/narration_10s.mp3`)} volume={0.94} />
    <Audio src={staticFile(`${A}/music_bed.mp3`)} volume={(f)=>Math.min(interpolate(f,[0,fpsConst*0.7],[0,0.08],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),interpolate(f,[fpsConst*9,fpsConst*10],[0.08,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}))} />
  </AbsoluteFill>;
};
