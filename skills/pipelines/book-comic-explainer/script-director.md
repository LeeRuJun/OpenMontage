# Script Director — Book Comic Explainer Pipeline

## When to Use

You receive the approved angle and research. Your job: produce a complete video script.

**How to tell a compelling story:** Read `skills/creative/narrative-storytelling.md` BEFORE writing a single line. That skill teaches you how to make an audience need to know what happens next. This skill (script-director) is about the pipeline contract — what fields the script artifact needs, how to structure it, how to validate it, when to gate.

The story craft lives in narrative-storytelling. The process lives here. Read both.

**HOW TO MAKE PEOPLE NEED TO KNOW:**

**1. Start with pain, not information.**

不要告诉观众「这是谁、在哪里、发生了什么」。
给他们看一个他们不完全理解的痛苦画面。
他们需要知道为什么。他们会等。

  ✗ 开场: 「祥林嫂是鲁镇上一个普通的农村妇女。」
     → 观众: 关掉。

  ✓ 开场: 除夕夜。雪地。鞭炮声。一个女人倒在街角，不动了。
         然后画面切回几年前——她还活着，正在鲁家院子里扫地。
         观众: 她怎么死的？？？

**2. Every scene ends with a question the viewer NEEDS answered.**

不是「然后呢」，是「为什么」、「后来怎样」、「她怎么办」。

  她再嫁了 → 观众: 这次会好吗？ → 丈夫死了 → 观众: 她能撑住吗？
  → 儿子被狼吃了 → 观众: 她还有什么 → 她回到鲁家 → 观众: 他们对她好吗？
  → 她反复讲阿毛 → 观众: 为什么没人听 → 她捐了门槛 → 观众: 赎罪了吗
  → 四婶说「放着罢」 → 观众: 她还能站起来吗 → 她死了。

  每一段结束都有一个问题。这个问题是下一段的引擎。

**3. Make the audience care about ONE person.**

不是一群角色。是一个人的一个欲望。
祥林嫂想要的很简单：活下去，不被当成脏东西。
就这么简单。观众瞬间懂。他们开始站在她这边。

**4. Don't explain. Show.**

  ✗ 旁白: 「祥林嫂在鲁四老爷家过得很辛苦，每天从天不亮干到天黑。」
     → 观众什么都没看见。

  ✓ 画面: 凌晨。她一个人蹲在井边洗衣。手冻得通红。
         院子里还没人醒。她已经在干活。旁边是洗好的一堆被单。
     → 旁白只要一句: 「冬天了。水是冰的。」
     → 观众懂了。不用解释。

**5. End with an image, not a lesson.**

  ✗ 结尾旁白: 「祥林嫂的悲剧告诉我们，旧社会对女性的压迫是多么深重。」
     → 观众: 关掉。

  ✓ 结尾: 画面回到鲁家院子。她曾经扫地的地方。空了。雪盖住了她每天站的位置。
         鞭炮声还在响。供桌上的香火还在烧。
         没有旁白。

  观众什么都懂了。不用你说。

**6. In the last three minutes, slow down.**

最后一段戏放慢到极致。每一个画面停 8-12 秒。旁白极少。一两句。
让观众沉浸在情绪里。所有前面的重量都要在这最后几分钟里落下来。
如果这里说太多话，就毁了。

**7. Every line of narration earns its place.**

删掉每一句「没有它观众也会懂」的话。
删掉每一句「在解释而不是在推进」的话。
剩下的每一句都在拉动故事往前走，或者在制造画面无法独自传达的信息。

## Story Structure for Book-to-Video

```
HOOK (0-3 min)
  一个画面让他们疼或让他们好奇。不是让他们认识角色。
  观众还不知道这个人是谁。但他们想知道。

WORLD BEFORE (3-8 min)
  在一切破碎之前，她是什么样的。
  不是讲生平。是给她被在乎的理由。
  让她做一个选择——观众从选择里认识她。

THE SPIRAL (8-16 min)
  上升 → 代价 → 更大的上升 → 更大的代价。
  选 3-4 个关键节点。不是书里所有的事。是服务角度的事。
  每一段的结尾都让人喘不过气。
  每一段的开头都让人必须继续。

THE FALL (16-19 min)
  最低的那一点。不是发生了更多坏事。
  是她终于意识到一切都失去了。
  观众不需要被告诉「这很惨」——让他们自己感觉到。

THE MEANING (19 min - END)
  一个画面。一句词。或者什么都没有。
  没有总结。没有道理。让故事停在最强的那一帧。
```

## Process

### Step 1: Absorb the Angle and Research

Read the approved angle from `proposal_packet.selected_concept`.
This angle is your north star. Every scene either serves it or is cut.

Read `research_brief` for: characters, key events, cultural context, visual leads.

### Step 2: Choose the 8-12 Scenes That Matter

From all the events in the book, pick the ones that serve the angle. Kill everything else.
For each scene, answer: What question does it leave the viewer with?
If it doesn't leave a question, kill it.

### Step 3: Write the Script — Voice + Image Together

Each section has three parts designed simultaneously:

```json
{
  "id": "s03",
  "dramatic_function": "raise_stakes",
  "question_left_with_viewer": "她能撑住吗？",

  "text": "冬天了。水是冰的。",
  "duration_seconds": 45,
  "delivery": {
    "pace": "slow",
    "tone": "restrained",
    "note": "不是同情。是陈述。轻。"
  },

  "frames": [
    {
      "id": "s03_f01",
      "character": "祥林嫂",
      "action": "蹲在井边洗衣，手冻得通红",
      "scene": "鲁家院子",
      "shot": "mid_shot",
      "composition": "她在画面偏左。右边是还没亮的天。井口冒着寒气。"
    }
  ]
}
```

`dramatic_function`: hook | build_world | raise_stakes | reveal_character | escalate | peak | land.
`question_left_with_viewer`: required. If you can't name it, the scene doesn't belong.
`text`: sparse. 30-80 Chinese characters typical for a 45-second section. Let frames carry weight.

### Step 4: Verify the Story Engine

Before submitting, trace the question chain:

```
s01 → 她怎么死的？
s02 → 她是谁？她怕什么？
s03 → 她真的属于这里吗？
...
sN → (landing — no question. just silence.)
```

Every section must have a question. If the chain breaks anywhere, the viewer leaves.

### Step 5: Voice Performance Design

Read `skills/meta/voice-performance-director.md` and the channel voice profile.
Every section's `delivery` must include: pace, tone, and a concrete note.
Not "read naturally" — be specific about where to pause, what to stress, when to go quiet.

### Step 6: Self-Evaluate

Score (1-5):

| Criterion | Question |
|-----------|----------|
| Hook power | Would someone who knows nothing about this book keep watching after the first 30 seconds? |
| Question chain | Does every section end with a question the viewer needs answered? |
| Character investment | Do I care what happens to this person? |
| Show, not tell | Are frames carrying 60%+ of the emotional weight? |
| Sparsity | Can I cut 20% of the narration without losing anything? |
| Ending | Does it land on an image, not a verbal lesson? |

If any score below 3, revise.

## Common Failures

| Failure | Why | Fix |
|---------|-----|-----|
| Explaining instead of story | You're a teacher, not a storyteller | Kill every sentence that explains. Let images explain. |
| No question at scene end | You listed events, didn't build tension | Write the question before you write the scene. |
| Too many words | You don't trust the images | Cut narration by half. Does the story still make sense? |
| Safe ending | You're afraid to let silence speak | Delete the last paragraph. End on the strongest image. |

## Gate Reminder (Binding)

This stage gates on human approval. After self-review: checkpoint `status="awaiting_human"`, present the full script with question chain, and **END YOUR TURN**.
