# 通用知识型讲书工作流设计

- 日期：2026-10-16
- 状态：待用户审核
- 适用 pipeline：`book-comic-explainer`
- 默认画布：1920×1080，16:9

## 1. 目标

将现有“漫画角色讲书”工作流升级为通用知识型讲书工作流，适用于历史、政治、商业、经济、心理、自助、科学、技术、传记、小说、哲学和社会科学等书籍。

视觉目标是参考已分析的《安史之乱》讲书视频：统一编辑画布、可复用图片/插画/地图/图解资产、轻量二维动效、旁白驱动的时间线、字幕和可选右下角真人头像。视频不采用纯 AI 视频镜头作为默认方案。

## 2. 核心原则

1. 先判断书籍类型，再决定视觉语法。
2. 先判断“如何讲”，再写最终脚本。
3. 旁白先行，旁白仍然是时间轴。
4. 先生成可复用的核心视觉资产包，再设计分镜。
5. storyboard 主要负责资产编排和时间关系，不为每一帧盲目生成新图。
6. 用 Remotion/SVG/代码化图层完成平移、缩放、路径绘制、数据出现、卡片切换和字幕同步。
7. 角色设计和场景设计只在小说、传记、案例场景等内容需要时启用。

## 3. 新的阶段流

```text
intake
  → book_profile
  → research
  → proposal + delivery_strategy
  → script
  → narration
  → visual_asset_plan
  → core_assets
  → asset_review
  → storyboard
  → gap_assets
  → edit
  → compose
```

### 3.1 `book_profile`

新增前置 artifact，至少包含：

```yaml
primary_type: history | politics | business_economics | psychology_self_help |
              science_technology | biography | literature | philosophy_social |
              mixed | unknown
secondary_types: []
narrative_mode: explanatory | story_driven | practical | debate | case_study
visual_grammar: historical_diagram | business_system | behavior_diagram |
                 technical_explainer | biographical_timeline |
                 narrative_illustration | concept_map | editorial_explainer
confidence: 0.0
 evidence: []
```

分类允许多标签，但必须有 `primary_type`。分类结果决定研究重点、资产类型、视觉组件和提示词约束。

### 3.2 `delivery_strategy`

在 proposal 阶段产出并由用户确认，至少包含：

- `core_promise`：观众看完得到什么
- `audience_problem`：观众原本不理解什么
- `narrative_mode`：重新解释、一个核心观点、问题解决、案例拆解、概念递进、人物命运、对立比较或实操方法
- `hook`
- `question_left_with_viewer`
- `progression`
- `summary_ratio`、`interpretation_ratio`、`example_ratio`
- `pacing`
- `ending` 和 `takeaway`

### 3.3 `visual_asset_plan`

由 `book_profile`、`delivery_strategy`、`script` 和 `narration_audio` 推导，建立可复用的资产清单：

```yaml
visual_grammar: historical_diagram
canvas: {width: 1920, height: 1080, aspect_ratio: "16:9"}
assets:
  - id: asset_id
    type: style_kit | illustration | map | diagram | timeline | object_visual |
          data_card | quote_card | portrait | background | talking_head
    role: explain_mechanism
    used_by: [section_id]
    generation_mode: image | svg | code | stock | user_asset
    status: planned | generated | approved | rejected | needs_refinement
    reusable: true
```

所有资产必须记录来源、路径、模型/工具、尺寸、适用段落和审核状态。

## 4. 视觉资产与合成

### 4.1 通用资产类型

- `style_kit`：背景、色板、字体、纸张/纹理
- `illustration`：插画、古画、案例场景
- `map`：地图、路线、区域高亮
- `diagram`：关系图、流程图、因果图
- `timeline`：事件/人物/发展时间线
- `object_visual`：物件、图标、象征物
- `data_card`：数字、对比、统计
- `quote_card`：关键观点、书中句子
- `portrait`：人物、作者、案例主体
- `talking_head`：可选真人头像 overlay

### 4.2 Remotion 场景能力

新增或扩展 16:9 场景 primitives：

- `EditorialCanvas`：统一米色/纸张/品牌背景
- `ImageCardScene`：图片 + 标题 + 轻微推拉摇移
- `MapScene`：SVG 路线、节点、区域高亮和箭头
- `DiagramScene`：节点、连线、流程和因果动画
- `TimelineScene`：时间轴和事件卡片
- `DataRevealScene`：数字递增、对比条和重点圈选
- `QuoteCardScene`：观点卡片和强调词
- `TalkingHeadOverlay`：可选右下角圆形真人头像

现有 `AnimeScene` 的图片交叉淡化、Ken Burns、平移、视差、渐变和暗角能力可复用，但不再作为默认视觉名称或默认风格。

## 5. 条件分支

- 历史/政治/经济：优先地图、时间线、档案插画、数据和因果图；不强制角色设计。
- 商业/案例：优先模型图、流程图、数据卡、人物/公司卡和案例场景。
- 心理/自助：优先行为循环、概念图、生活场景和步骤卡。
- 科学/技术：优先结构图、实验步骤、系统图和机制动画。
- 传记/小说：启用 `character_design` 和 `scene_design`，使用人物关系、场景插画和时间线。
- 混合型：按章节局部启用不同视觉语法。

## 6. 审核和成本控制

- `book_profile`：确认书籍类型和视觉语法。
- `proposal`：确认核心讲法和叙事角度。
- `narration`：确认声音样本和旁白时间线。
- `core_assets`：批量生成前先审一个资产样本；生成后按资产包审核。
- `storyboard`：审核资产如何服务旁白，不重复审核已通过的核心资产。
- 生成工具调用前仍需执行 registry preflight、provider/model 宣布和成本确认。

## 7. 《安史之乱》实施样例

本次视频采用：

```yaml
primary_type: history
secondary_types: [politics, economics]
visual_grammar: historical_diagram
narrative_mode: reframing_explainer
canvas: 1920x1080
```

核心资产包预计包括：统一纸张画布、唐代疆域/行军地图、财政流动图、钱币/粮仓/兵器物件、人物/势力卡、时间线、关键数字卡、引用卡和可选真人头像 overlay。素材先审核，再由 storyboard 编排成旁白驱动的长视频。

## 8. 验证

- manifest 和新 artifact schema 校验通过。
- 书籍类型、讲法策略、资产计划可单元测试。
- 资产 manifest 能区分计划、生成、审核、拒绝和补生成状态。
- Remotion 各新场景支持 deterministic seek/render。
- 16:9 输出通过 ffprobe，旁白总时长与 composition 时长一致。
- 至少用《安史之乱》做一条端到端 smoke render，验证地图、图解、数据卡、字幕、音频和真人头像 overlay。
