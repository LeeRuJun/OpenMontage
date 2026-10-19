# Book Explainer Self-Media Usage

Use this Layer 2 skill when OpenMontage produces a self-media book commentary video, especially for serious nonfiction / “hard books” in politics, history, business, society, international relations, philosophy, or strategy.

This is not a generic book-summary recipe. The goal is to turn a book into a sharp, watchable explanatory video that can survive Douyin/Bilibili/YouTube attention economics while still respecting the book’s argument.

## When to Use

Use when the user asks for:

- 讲书视频 / 读书视频 / 一本书解读
- 自媒体读书栏目
- 抖音 / B站 / 视频号书籍内容
- 封面、标题、简介、片头、结尾 for book commentary
- A book episode within an OpenMontage generated explainer pipeline

## Core Promise

A good book explainer should give the viewer:

> 一副看世界的眼镜，而不是一堆书摘。

Do not merely summarize chapters. Extract a central conflict, explain the book’s strongest framework, show where it helps, and show where it breaks.

## Content Architecture

Use this structure as the default script spine:

1. **Hook first** — Start with a conflict or question, not the book title.
2. **One-sentence promise** — What does this book help us understand?
3. **Context** — Author, historical moment, and why the book appeared when it did.
4. **Core framework** — The book’s main explanatory model.
5. **Three supporting ideas** — Each should be visually explainable.
6. **Strongest insight** — Why the book is worth reading.
7. **Danger / limitation** — What the book oversimplifies, hides, or risks becoming.
8. **Today’s relevance** — Why this book still helps interpret current reality.
9. **Closing sentence** — A memorable takeaway, not a generic “like and follow.”

## Hook Rules

Open with tension:

```text
为什么美国总觉得欧洲天真，欧洲总觉得美国粗暴？
为什么改革反而会引爆革命？
美国为什么总盯着欧亚大陆？
世界真的会按文明开战吗？
```

Avoid:

```text
今天我们来讲一本书……
这本书非常有名……
作者是谁谁谁……
```

For self-media, the first 5 seconds must make the viewer want the answer.

## Title Formula

Prefer conflict-heavy short titles. The title should work at phone-thumbnail size.

Patterns:

```text
强者相信权力，弱者相信规则
美国和欧洲为什么看不懂彼此？
欧洲的天堂，是美国撑起来的吗？
这本书最厉害的地方，也是最危险的地方
为什么改革反而引爆革命？
```

Use the book title as subtitle when needed:

```text
《天堂与权力》讲透美欧分歧
```

## Cover / Thumbnail Rules

A self-media cover is not a book poster. It is a click decision.

### Main title

Use 6–12 large Chinese characters. Avoid long academic subtitles as the main visual.

Good:

```text
强者相信权力
弱者相信规则
```

Less effective:

```text
美国与欧洲为什么看不懂彼此？
```

### Layout

- Douyin / video feed: 4:3 cover works well.
- Bilibili / YouTube: 16:9.
- Put the large hook text in the left or top-left safe zone.
- Use the book title as a smaller subtitle.
- Keep all text deterministic: if exact Chinese matters, generate a low-text base image and add Chinese text with PIL/Remotion/design tooling.

### Visual hierarchy

1. Big hook text
2. Strong symbolic visual
3. Book title / channel mark
4. Secondary detail only if still readable on phone

## Visual Strategy

Do not make the video a stack of text slides. The visual layer must explain.

Rotate visual logic every 15–20 seconds:

- Question card
- Split comparison
- Timeline
- Map / territory field
- Causal chain
- Metaphor diagram
- Quote evidence card
- Balance scale
- Final synthesis loop

For abstract political/history books, prefer diagrams and metaphors over generic stock footage.

Example for transatlantic strategy:

- Mars/Venus split field
- Hobbesian threat map
- Kantian institution network
- Protection umbrella metaphor
- Moral-label peel-away board
- Framework-vs-complexity balance scale
- Power/rules closed loop

## Voice Direction

For Chinese serious book explainers, use a mature narrator voice. Avoid young, cute, or exaggerated character voices.

Recommended MiniMax profile when available:

```yaml
provider: minimax
model: speech-2.8-hd
voice_id: Chinese (Mandarin)_Reliable_Executive
speed: 0.92
vol: 1
pitch: 0
emotion: do not send
```

Rules:

- Generate a 10–15 second sample first.
- Batch-generate only after the user approves the voice.
- Do not send an emotion parameter unless the provider and brief require it.
- Avoid `disgusted`, `angry`, cute-girl voices, or theatrical delivery for serious nonfiction.
- Let the voice rhythm be natural; do not force exact duration if it hurts credibility.

## Subtitle and On-Screen Text

Self-media viewers need readability, but not duplicated walls of text.

Rules:

- Bottom subtitles should be short and readable.
- Key ideas should appear as large conceptual callouts.
- Avoid showing the full narration sentence as both a big card and bottom caption.
- Favor short punch lines:

```text
不是性格差异
是权力位置差异
```

## Publishing Copy

Use the video’s central conflict, not a generic summary.

Template:

```text
[Sharp question]
《[Book]》给了一个很锋利的答案：
[Core distinction / framework]
读懂它，你会更容易看懂[real-world domain].

#[channel] #[book] #读书 #硬书 #topic
```

Example:

```text
为什么美国和欧洲总是看不懂彼此？
《天堂与权力》给了一个很锋利的答案：
不是性格差异，是权力位置差异。
读懂它，你会更容易看懂今天的国际新闻。
```

## Quality Checklist

Before presenting the episode as ready:

- Does the first 5 seconds start with a sharp question or conflict?
- Can the title be read on a phone thumbnail?
- Does the script explain the book’s framework, not just summarize chapters?
- Does it include the book’s limitation or danger?
- Does every major idea have a visual metaphor or diagram?
- Does the voice sound like a mature narrator / book commentator?
- Are subtitles readable without becoming full-screen paragraphs?
- Does the ending leave a repeatable idea?

## Common Failures

- Starting with author biography before the hook.
- Turning the video into a PPT of text cards.
- Using generic stock footage that does not explain the idea.
- Overusing flags, soldiers, explosions, or cinematic war imagery for political books.
- Using a cute or young TTS voice for serious nonfiction.
- Letting AI image generation render important Chinese text directly.
- Making the cover look like a book poster instead of a self-media thumbnail.
