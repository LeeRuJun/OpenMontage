---
name: historical-color-direction
description: Use when authoring or reviewing visual boards and image prompts for fact-grounded historical stories that need richer color, environmental depth, and continuity without copying a reference video.
---

# Historical Color Direction

把公开分镜方法吸收为通用工作法，不使用固定外部视频，不把任何外部视频、构图、人物、字幕、水印或配色当作本项目模板。美术指导是每一集、每一板的参数，不是 Python 执行器里的固定朝代或固定滤镜。

## Board contract

每张正式视觉板先写清楚：

- **场景主体**：人物处于什么真实地点，或完整环境本身成为主体。
- **阅读路径**：前景、中景、远景各承担什么信息；至少有 3 个可随镜头逐步观察的区域。
- **光色关系**：按时段、天气、光源与材质组织色彩，记录反光面、材质本色，以及冷暖关系。
- **视觉用途**：这张板让观众理解哪个事件、因果或后果，而不是复述整段旁白。
- **连续性锚点**：只引用当前项目批准的角色、场景和道具资产 ID。

人物必须属于环境；人物属于环境，而不是漂浮在背景前的独立头像。纯人物头像、漂浮肖像和孤立物品不作为正式视觉板。物品不能成为正式图片主体，除非它只是完整场景中的证据层，并且场景仍然提供地点、空间关系和叙事信息。

## Parameterized color direction

提示词从项目参数合成，不套默认颜色：

```json
{
  "visual_style": {
    "name": "项目批准的风格名",
    "prompt_guidance": "材质、光线、色彩关系与影像质感"
  },
  "color_direction": "本板的时段、天气、光源与冷暖关系",
  "composition": "前景、中景、远景和镜头阅读路径"
}
```

- `visual_style` 来自已批准的项目制作设置或 proposal；`color_direction` 来自当前视觉板。
- 若已有批准的美术指导，必须原样传递其意图，不要默默重染成统一黄褐、低饱和或旧项目配色。
- 更丰富的色彩意味着区分建筑、衣料、植被、水面、石材和灯火的本色，并控制明度层级；不是无条件提高全局饱和度。
- 蓝青环境光、橙黄灯火、暗红织物、灰绿植被等只在事件地点、时段和光源支持时使用。

## Prompt shape

最终提示词按此顺序展开：

1. 历史时期与叙事事件；
2. 人物/环境主体及其处境；
3. 地点和前中远景空间关系；
4. 使事件可读的证据层；
5. 史实边界与不可虚构内容；
6. 构图、镜头、光色和字幕安全区；
7. 3–5 个可供后期读取的动态信息层；
8. 禁止拼贴、源图边框、AI 文字、现代物件和漂浮肖像。

最终图是一张单一连贯镜头，不是参考图拼贴、九宫格、物品陈列或 mood board。外部参考只提供可迁移的方法，不写入业务 JSON，也不绑定固定 URL。
