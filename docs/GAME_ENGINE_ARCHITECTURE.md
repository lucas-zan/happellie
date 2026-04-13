# HappyEllie 游戏引擎架构设计

> 核心原则：**模型只填内容，引擎负责好玩**
> 文档版本：v2（2026-04-13，含完整迁移方案和技术选型）

---

## 一、架构核心思想

### 当前做法的问题

当前 `PageRenderer` 按 `ComponentType` switch 渲染组件，本质上是**卡片式表单**：

```
当前：每一页 = Card 容器 → 一组 LessonComponent → switch 渲染文字+按钮
```

小朋友看到的是文字段落和普通按钮，没有角色形象、没有动画反馈、没有游戏节奏。

### 新架构：游戏模板引擎

```
新的：每一步 = 一个完整的游戏模板 → 自带布局/动画/交互/音效 → AI 只填内容
```

类比：电视综艺节目——舞台（模板）提前搭好，导演（AI）每期只决定题目和嘉宾。

```
┌─────────────────────────────────────────┐
│  AI 生成层                               │
│                                         │
│  输出: [ { template_id, slots }, ... ]  │
│  只决定：用哪个模板 + 填什么文字/词汇    │
└──────────────────┬──────────────────────┘
                   │ JSON
                   ▼
┌─────────────────────────────────────────┐
│  校验层                                  │
│                                         │
│  template_id 白名单 → slots schema 校验  │
│  → 缺失字段补默认值 → 内容安全检查       │
└──────────────────┬──────────────────────┘
                   │ 合格的 GameStep[]
                   ▼
┌─────────────────────────────────────────┐
│  游戏引擎（前端）                        │
│                                         │
│  GameEngine 读取 steps → 按顺序推进      │
│  → 每步渲染对应的 Template 组件          │
│  → 模板自带全部动画/交互/音效            │
└─────────────────────────────────────────┘
```

---

## 二、需要重写什么、保留什么

### 保留不动的部分

| 模块 | 文件 | 理由 |
|------|------|------|
| 接口层全部 | `domain/interfaces/*.py` | Protocol 定义与模板无关，继续使用 |
| DI 容器 | `core/container.py` | lru_cache 工厂模式可复用，只新增注册项 |
| 配置系统 | `core/config.py` | 不受影响 |
| 数据库连接 | `infra/db/connection.py` | 不受影响 |
| SQLite 仓库 | `infra/repositories/*.py` | Session / Pet / Content 仓库照用 |
| 词库仓库 | `infra/vocab/json_vocab_repository.py` | 照用 |
| LLM 客户端 | `infra/ai/openai_compatible_structured_llm.py` | 照用 |
| 成本追踪 | `infra/analytics/basic_cost_tracker.py` | 照用 |
| 画像分析 | `infra/analytics/*.py` | 照用 |
| TTS 接口 | `infra/tts/*.py` | 照用（后续替换实现） |
| API 路由层 | `api/routes/*.py` | 薄层，改返回类型即可 |
| 前端 API 客户端 | `api/client.ts` | 小改返回类型 |
| 前端基础组件 | `components/Button.tsx` 等 | 基础 UI 原语继续用 |
| 前端宠物页 | `pages/PetPage.tsx` | 独立页面，后续增强 |
| 前端管理页 | `pages/AdminPage.tsx` | 不受影响 |
| 前端布局 | `layout/AppLayout.tsx` | 保留，后续改为游戏模式时可隐藏侧边栏 |
| CSS 设计系统 | `styles.css` 变量和基础样式 | 颜色/间距/圆角/字体变量保留 |

### 需要重写的部分

| 模块 | 当前文件 | 改动性质 |
|------|----------|----------|
| **LessonPackage schema** | `schemas/lesson.py` | **扩展**：新增 `GameStep` + `TemplateId`，保留 `LessonPackage` 外壳，内部从 `pages` 迁移到 `steps` |
| **PetSummary schema** | `schemas/pet.py` | **扩展**：增加 `growth_exp` / `emotion_state` |
| **DB schema** | `infra/db/schema.py` | **扩展**：新增 `learning_events` 表 |
| **AILessonPlanner** | `infra/planning/ai_lesson_planner.py` | **重写 prompt**：输出从 `pages + components` 改为 `steps + template_id + slots` |
| **RulesLessonPlanner** | `infra/planning/rules_lesson_planner.py` | **重写**：输出 step 编排而非 page 编排 |
| **AILessonGenerator** | `infra/ai/ai_lesson_generator.py` | **重写 prompt**：输出 `GameStep[]` 而非 `LessonPage[]` |
| **RulesLessonGenerator** | `infra/ai/rules_lesson_generator.py` | **重写**：硬编码 step 序列而非 page 序列 |
| **LessonService** | `services/lesson_service.py` | **小改**：增加 step 校验环节 |
| **SessionService** | `services/session_service.py` | **小改**：接收 `StepResult[]` 替代 `BlockResult[]` |
| **前端 types.ts** | `api/types.ts` | **扩展**：新增 `GameStep` / `TemplateId` / slots 类型 |
| **前端 LessonPage** | `pages/LessonPage.tsx` | **重写**：用 `GameEngine` 替代手动分页逻辑 |
| **前端 PageRenderer** | `renderers/PageRenderer.tsx` | **废弃**：被 `GameEngine` + 模板组件取代 |
| **前端游戏样式** | `styles.css` 游戏部分 | **重写**：用模板专属样式替代 `.game-*` 类 |

### 新增的部分

| 模块 | 位置 | 说明 |
|------|------|------|
| 模板 slots schema 校验器 | `backend/app/infra/validation/` | 校验 AI 输出的 step 合法性 |
| 前端游戏引擎 | `frontend/src/engine/` | 步骤状态机 + 事件采集 + 音频管理 |
| 前端游戏模板 | `frontend/src/templates/` | 每种 template_id 一个完整组件 |
| 前端角色系统 | `frontend/src/characters/` | 角色注册 + 表情渲染 |
| 前端动画系统 | `frontend/src/engine/animations/` | CSS 动画库 + 转场控制 |

### 改动量评估

```
保留不动：约 60% 的代码（接口、仓库、配置、DI、基础 UI）
重写/扩展：约 25% 的代码（planner prompt、generator prompt、schema、LessonPage）
新增：     约 15% 的代码（GameEngine、Templates、校验器、动画）
```

**不是推倒重来，是在稳固地基上换上层建筑。**

---

## 三、技术选型

### 后端（保持不变）

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| Python | 3.11+ | 运行时 | 当前已用 |
| FastAPI | 0.115 | HTTP API | 当前已用，async 友好 |
| Pydantic v2 | 2.10 | Schema 校验 | 当前已用，天然适合 slots 校验 |
| SQLite | - | 持久化 | 当前已用，本地优先 |
| OpenAI-compatible API | - | LLM 调用 | 当前已用，已有抽象层 |

**后端不引入任何新依赖。** Pydantic v2 本身就可以做 slots schema 校验。

### 前端

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| React | 18.3 | UI 框架 | 当前已用 |
| Vite | 6.0 | 构建工具 | 当前已用 |
| TypeScript | 5.7 | 类型安全 | 当前已用 |
| react-router-dom | 6.30 | 路由 | 当前已用 |
| **CSS 动画** | 原生 | 全部动画效果 | **零依赖，性能好** |
| **@dnd-kit/core** | 最新 | 拖拽交互 | 仅用于 `drag_match` / `sentence_puzzle` 模板 |
| Tauri | 2.x | 桌面壳 | 当前已用 |

#### 关于动画：为什么选纯 CSS 而不是动画库

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| **纯 CSS 动画** | 零依赖、性能最好、浏览器原生 | 复杂序列需要手动编排 | **首选** |
| Framer Motion | API 友好 | 包体积大（~30KB）、React 绑定 | 不选 |
| Lottie | 可做复杂角色动画 | 需要 AE 制作、运行时较重 | 未来可选（角色动画） |
| GSAP | 强大的时间线编排 | 商业授权复杂 | 不选 |
| CSS + Web Animations API | 零依赖 + JS 控制时间线 | 需稍多代码 | **备选增强** |

结论：**Phase 1 全部用纯 CSS 动画 + CSS transition**。如果后续角色需要复杂骨骼动画，再单独引入 Lottie 或 Spine。

#### 关于拖拽：为什么选 @dnd-kit

| 方案 | 优点 | 缺点 |
|------|------|------|
| **@dnd-kit/core** | React 友好、触屏优先、轻量（~12KB）、高度可定制 | 需要学习 |
| react-beautiful-dnd | 列表拖拽强 | 已停止维护、不适合自由拖拽 |
| 原生 drag API | 零依赖 | 触屏体验差、自定义困难 |

@dnd-kit 是唯一需要新增的前端依赖。只在 `drag_match` 和 `sentence_puzzle` 两个模板中使用。

#### 关于音频

| 方案 | 选型 |
|------|------|
| 单词发音 | 后端 TTS 预生成 → 缓存为音频文件 → 前端 `<audio>` 播放 |
| 音效（正确/错误/金币） | 前端内置小体积 mp3（每个 <5KB） |
| 播放控制 | 自定义 `useAudioPlayer` hook，封装 `HTMLAudioElement` |

不需要 Howler.js 等音频库。原生 `<audio>` + 几个小 mp3 足够。

---

## 四、数据合同（后端 Schema 详细设计）

### 4.1 GameStep —— 新的课程最小单元

```python
# backend/app/schemas/lesson.py 新增

TemplateId = Literal[
    # 叙事类
    "story_dialogue",    # 角色对话（视觉小说风格）
    "story_choice",      # 剧情选择（影响后续）
    "mission_briefing",  # 任务介绍
    # 学习类
    "word_reveal",       # 单词揭示（图片+发音+例句）
    "word_in_scene",     # 场景找词
    # 练习类
    "listen_pick",       # 听音选图
    "drag_match",        # 拖拽匹配
    "choice_battle",     # 答题打怪
    "sentence_puzzle",   # 句子拼装
    "speak_repeat",      # 跟读模仿
    # 奖励类
    "reward_chest",      # 宝箱开启
    "feed_pet",          # 喂宠物
    "episode_end",       # 本集结束
]


class GameStep(BaseModel):
    step_id: str
    template_id: TemplateId
    slots: dict
    is_interactive: bool = False
    reward_on_complete: dict = Field(default_factory=dict)
```

### 4.2 LessonPackage v3

```python
class LessonPackage(BaseModel):
    package_version: str = "lesson_package_v3"
    lesson_id: str
    student_id: str
    pet_id: str = "pet-default"
    title: str
    theme: str = "forest_adventure"
    estimated_minutes: int = 6
    vocab: list[str]
    target_vocab_items: list[VocabItem] = Field(default_factory=list)
    story: StoryThread = Field(default_factory=StoryThread)
    steps: list[GameStep] = Field(default_factory=list)
    reward_preview: dict = Field(default_factory=dict)
    focus_tags: list[str] = Field(default_factory=list)
    teacher_note: str = ""
    source_model: str = ""
    debug_metadata: dict = Field(default_factory=dict)
    
    # 兼容字段，过渡期保留
    pages: list[LessonPage] = Field(default_factory=list)
```

### 4.3 每个模板的 slots 规范

每个 `template_id` 对应一个精确的 slots schema。AI 只填这些字段：

```python
# 叙事类

STORY_DIALOGUE_SLOTS = {
    "background": str,           # 背景场景 key
    "dialogues": [               # 对话序列
        {
            "character": str,    # 角色 id（从 CharacterRegistry 取形象）
            "mood": str,         # 表情 key（happy/worried/excited...）
            "line": str,         # 台词（短，一句话）
        }
    ],
}

STORY_CHOICE_SLOTS = {
    "character": str,            # 提问角色
    "scenario": str,             # 场景描述
    "choices": [
        {
            "key": str,          # 选项 key
            "text": str,         # 选项文字
            "consequence_tag": str,  # 后果标签（kind/brave/funny）
        }
    ],
}

MISSION_BRIEFING_SLOTS = {
    "companion": { "id": str, "line": str },
    "objectives": [str],         # 任务目标列表（2-3 条）
}

# 学习类

WORD_REVEAL_SLOTS = {
    "word": str,
    "meaning": str,
    "image_hint": str,           # 图片 key
    "audio_text": str,           # TTS 要合成的文本
    "sentence": str,             # 例句
    "character": { "id": str, "mood": str, "line": str },
}

WORD_IN_SCENE_SLOTS = {
    "scene_hint": str,           # 场景图 key
    "hidden_words": [
        { "word": str, "meaning": str, "position_hint": str }
    ],
}

# 练习类

LISTEN_PICK_SLOTS = {
    "character": { "id": str, "line": str },
    "audio_text": str,           # 要播放的单词/短语
    "options": [
        { "key": str, "image_hint": str }
    ],
    "correct_key": str,
    "success_line": str,
    "fail_line": str,
}

DRAG_MATCH_SLOTS = {
    "character": { "id": str, "line": str },
    "pairs": [
        { "left": str, "right": str }    # 英文→中文 或 英文→图片
    ],
    "match_type": str,           # "text_to_text" | "text_to_image"
}

CHOICE_BATTLE_SLOTS = {
    "monster": { "id": str, "name": str, "hp": int },
    "companion": { "id": str, "line": str },
    "rounds": [
        {
            "question": str,
            "options": [str],
            "answer": str,
            "round_type": str,   # "text" | "image" | "audio"
        }
    ],
    "victory_line": str,
    "defeat_line": str,
}

SENTENCE_PUZZLE_SLOTS = {
    "character": { "id": str, "line": str },
    "target_sentence": str,
    "scrambled_words": [str],
    "hint": str,                 # 中文提示
}

SPEAK_REPEAT_SLOTS = {
    "character": { "id": str, "mood": str, "line": str },
    "audio_text": str,           # 要跟读的文本
    "display_text": str,         # 显示的文本（可能含高亮标记）
}

# 奖励类

REWARD_CHEST_SLOTS = {
    "total_coins": int,
    "total_food": { str: int },       # food_type → 数量
    "bonus_item": { "key": str, "name": str } | None,
}

FEED_PET_SLOTS = {
    "available_food": { str: int },
    "pet_current_mood": str,
}

EPISODE_END_SLOTS = {
    "episode_summary": str,
    "next_hook": str,            # 悬念/预告
    "next_episode_hint": str,
    "companion_farewell": { "id": str, "mood": str, "line": str },
}
```

### 4.4 StepResult —— 前端事件回传

```python
# backend/app/schemas/session.py 新增

class StepResult(BaseModel):
    step_id: str
    template_id: str
    correct: bool | None = None      # 非交互步骤为 None
    score: int = 0
    duration_ms: int = 0
    details: dict = Field(default_factory=dict)
    #   details 按模板类型不同：
    #   listen_pick: { "selected_key": "apple" }
    #   drag_match:  { "attempts": 2 }
    #   choice_battle: { "rounds_correct": 2, "rounds_total": 3 }
    #   story_choice: { "chosen_key": "help" }
```

---

## 五、前端游戏引擎详细设计

### 5.1 目录结构

```
frontend/src/
│
├── api/                          # 保留，小改类型
│   ├── client.ts
│   └── types.ts
│
├── components/                   # 保留，基础 UI 原语
│   ├── Button.tsx
│   ├── Card.tsx
│   └── ...
│
├── layout/                       # 保留
│   └── AppLayout.tsx
│
├── pages/                        # 保留 + 改 LessonPage
│   ├── HomePage.tsx
│   ├── LessonPage.tsx            # 改为挂载 GameEngine
│   ├── PetPage.tsx
│   └── AdminPage.tsx
│
├── engine/                       # 【新增】游戏引擎核心
│   ├── GameEngine.tsx            # 步骤推进 + 全屏游戏容器
│   ├── GameHUD.tsx               # 顶部状态栏（金币/进度/角色头像）
│   ├── TemplateRegistry.ts       # template_id → 组件映射表
│   ├── types.ts                  # GameStep, StepResult, TemplateProps
│   ├── hooks/
│   │   ├── useGameState.ts       # coins/food/score 累计状态
│   │   ├── useStepTransition.ts  # 步骤切换 + 动画控制
│   │   ├── useAudio.ts           # 音频播放（TTS + 音效）
│   │   └── useEventLog.ts        # 事件采集缓冲
│   └── animations/
│       └── game-animations.css   # 全部游戏动画（纯 CSS）
│
├── templates/                    # 【新增】游戏模板组件
│   ├── narrative/
│   │   ├── StoryDialogue.tsx
│   │   ├── StoryChoice.tsx
│   │   └── MissionBriefing.tsx
│   ├── learn/
│   │   ├── WordReveal.tsx
│   │   └── WordInScene.tsx
│   ├── practice/
│   │   ├── ListenPick.tsx
│   │   ├── DragMatch.tsx
│   │   ├── ChoiceBattle.tsx
│   │   ├── SentencePuzzle.tsx
│   │   └── SpeakRepeat.tsx
│   └── reward/
│       ├── RewardChest.tsx
│       ├── FeedPet.tsx
│       └── EpisodeEnd.tsx
│
├── characters/                   # 【新增】角色渲染
│   ├── CharacterRenderer.tsx     # 根据 id + mood 渲染角色
│   ├── CharacterRegistry.ts      # id → 素材路径映射
│   ├── DialogueBubble.tsx        # 对话气泡组件
│   └── assets/                   # 角色素材（初期 SVG）
│       ├── ellie/
│       ├── foxy/
│       └── ...
│
├── renderers/
│   └── PageRenderer.tsx          # 【废弃】过渡期保留，不再新增功能
│
└── styles.css                    # 保留基础变量，游戏样式迁移到模板
```

### 5.2 GameEngine 核心逻辑

```typescript
// engine/types.ts

export interface TemplateProps<TSlots = Record<string, unknown>> {
  slots: TSlots;
  onComplete: (result: StepResult) => void;
  audio: AudioController;
  gameState: GameState;
}

export type TemplateComponent = React.FC<TemplateProps>;
```

```typescript
// engine/TemplateRegistry.ts

import { StoryDialogue } from '../templates/narrative/StoryDialogue';
import { ListenPick } from '../templates/practice/ListenPick';
import { ChoiceBattle } from '../templates/practice/ChoiceBattle';
// ... 其他模板

const registry: Record<string, TemplateComponent> = {
  story_dialogue: StoryDialogue,
  story_choice: StoryChoice,
  mission_briefing: MissionBriefing,
  word_reveal: WordReveal,
  word_in_scene: WordInScene,
  listen_pick: ListenPick,
  drag_match: DragMatch,
  choice_battle: ChoiceBattle,
  sentence_puzzle: SentencePuzzle,
  speak_repeat: SpeakRepeat,
  reward_chest: RewardChest,
  feed_pet: FeedPet,
  episode_end: EpisodeEnd,
};

export function getTemplate(templateId: string): TemplateComponent | null {
  return registry[templateId] ?? null;
}
```

```typescript
// engine/GameEngine.tsx 核心流程

function GameEngine({ lesson, onFinish }: GameEngineProps) {
  const [stepIndex, setStepIndex] = useState(0);
  const [transitioning, setTransitioning] = useState(false);
  const gameState = useGameState();
  const audio = useAudio();
  const events = useEventLog(lesson.lesson_id);

  const step = lesson.steps[stepIndex];
  const Template = getTemplate(step.template_id);

  function handleStepComplete(result: StepResult) {
    events.record(step, result);

    // 即时奖励
    if (result.correct && step.reward_on_complete.coins) {
      gameState.addCoins(step.reward_on_complete.coins);
      audio.play('coin');
    }

    // 转场到下一步
    if (stepIndex < lesson.steps.length - 1) {
      setTransitioning(true);
      // CSS 动画 300ms 后切换
      setTimeout(() => {
        setStepIndex(i => i + 1);
        setTransitioning(false);
      }, 300);
    } else {
      onFinish(gameState.snapshot(), events.flush());
    }
  }

  if (!Template) return <FallbackStep step={step} onSkip={handleStepComplete} />;

  return (
    <div className="game-engine">
      <GameHUD
        coins={gameState.coins}
        progress={(stepIndex + 1) / lesson.steps.length}
        petMood={gameState.petMood}
      />
      <div className={`game-stage ${transitioning ? 'game-stage--exit' : 'game-stage--enter'}`}>
        <Template
          key={step.step_id}
          slots={step.slots}
          onComplete={handleStepComplete}
          audio={audio}
          gameState={gameState}
        />
      </div>
    </div>
  );
}
```

### 5.3 模板示例：ListenPick（听音选图）

```
 ┌────────────────────────────────┐
 │  🦊 "Which one is the apple?"  │  ← 角色 + 对话气泡
 │                                 │
 │         🔊 (播放按钮，脉冲动画)  │  ← 点击重听
 │                                 │
 │   ┌─────┐ ┌─────┐ ┌─────┐     │
 │   │ 🍎  │ │ 🍌  │ │ 🥕  │     │  ← 三张图片，弹跳入场
 │   └─────┘ └─────┘ └─────┘     │
 │                                 │
 │   ✅ "Great job!" + ⭐⭐⭐     │  ← 正确反馈 + 星星爆炸
 └────────────────────────────────┘
```

内置行为（全部硬编码在模板里，AI 不控制）：

1. 进入时自动播放 `audio_text` 发音
2. 角色对话气泡逐字出现（CSS `@keyframes typing`）
3. 三张图片依次弹跳入场（CSS `@keyframes bounce-in`，错开 150ms）
4. 点击选项后：
   - 正确：绿色闪光 + 星星爆炸 + 角色欢呼 + 金币飞入 HUD
   - 错误：温柔摇晃 + 正确答案高亮 + 角色鼓励
5. 1.5 秒后自动调用 `onComplete`

AI 只提供：哪个角色说什么话、播放哪个词的发音、三张图片是什么、正确答案是哪个。

### 5.4 模板示例：ChoiceBattle（答题打怪）

```
 ┌────────────────────────────────┐
 │  ❤️❤️❤️ (怪物HP)    💰 18     │  ← HUD
 │                                 │
 │         👾 Snack Thief          │  ← 怪物角色（摇晃待机动画）
 │     "Hehe! Try to beat me!"    │
 │                                 │
 │  ┌──────────────────────────┐  │
 │  │ What does 'bread' mean?  │  │  ← 题目
 │  │                          │  │
 │  │  [ 面包 ] [ 牛奶 ] [ 果汁 ] │  ← 选项
 │  └──────────────────────────┘  │
 │                                 │
 │  🦊 "You can do it!"           │  ← 伙伴鼓励
 └────────────────────────────────┘
```

内置行为：

1. 怪物入场动画（从上方落下 + 摇晃待机）
2. 每答对一题：怪物被击中闪烁 + HP 条下降 + 攻击特效
3. 答错时：怪物嘲笑动画 + 柔和提示正确答案
4. 全部答完：
   - 胜利：怪物爆散 + 伙伴欢呼 + 战利品掉落动画
   - 失败（可选）：怪物逃跑 + "下次再来"
5. 多回合自动推进，不需要手动翻页

### 5.5 动画系统

全部使用**纯 CSS @keyframes + CSS transition + CSS custom properties**。

```css
/* engine/animations/game-animations.css */

/* === 入场动画 === */

.anim-bounce-in {
  animation: bounce-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes bounce-in {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.12); }
  100% { transform: scale(1); opacity: 1; }
}

.anim-slide-up {
  animation: slide-up 0.35s ease-out both;
}

@keyframes slide-up {
  from { transform: translateY(30px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.anim-fade-in {
  animation: fade-in 0.3s ease both;
}

/* 延迟入场：通过 CSS custom property 控制 */
.anim-stagger { animation-delay: calc(var(--i, 0) * 120ms); }

/* === 反馈动画 === */

.anim-correct {
  animation: correct-pulse 0.5s ease;
}

@keyframes correct-pulse {
  0% { box-shadow: 0 0 0 0 rgba(72, 190, 116, 0.5); transform: scale(1); }
  50% { box-shadow: 0 0 0 12px rgba(72, 190, 116, 0); transform: scale(1.05); }
  100% { box-shadow: 0 0 0 0 transparent; transform: scale(1); }
}

.anim-wrong {
  animation: wrong-shake 0.4s ease;
}

@keyframes wrong-shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}

.anim-star-burst {
  animation: star-burst 0.6s ease-out forwards;
}

@keyframes star-burst {
  0% { transform: scale(0) rotate(0); opacity: 1; }
  100% { transform: scale(1.8) rotate(120deg); opacity: 0; }
}

/* === 奖励动画 === */

.anim-coin-fly {
  animation: coin-fly 0.7s ease-out forwards;
}

@keyframes coin-fly {
  0% { transform: translateY(0) scale(1); opacity: 1; }
  100% { transform: translateY(-60px) scale(0.4); opacity: 0; }
}

.anim-chest-glow {
  animation: chest-glow 1.2s ease-in-out;
}

@keyframes chest-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 200, 50, 0); }
  50% { box-shadow: 0 0 40px rgba(255, 200, 50, 0.6); }
}

/* === 角色动画 === */

.anim-character-idle {
  animation: idle-bob 2s ease-in-out infinite;
}

@keyframes idle-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.anim-character-talk {
  animation: talk-bounce 0.15s ease-in-out infinite alternate;
}

@keyframes talk-bounce {
  from { transform: scaleY(1); }
  to { transform: scaleY(1.03); }
}

.anim-character-celebrate {
  animation: celebrate 0.6s ease;
}

@keyframes celebrate {
  0% { transform: translateY(0) rotate(0); }
  30% { transform: translateY(-12px) rotate(-5deg); }
  60% { transform: translateY(-12px) rotate(5deg); }
  100% { transform: translateY(0) rotate(0); }
}

.anim-character-hit {
  animation: hit-flash 0.3s ease 2;
}

@keyframes hit-flash {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* === 页面转场 === */

.game-stage--enter {
  animation: stage-enter 0.3s ease-out;
}

@keyframes stage-enter {
  from { transform: translateX(40px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.game-stage--exit {
  animation: stage-exit 0.25s ease-in forwards;
}

@keyframes stage-exit {
  to { transform: translateX(-40px); opacity: 0; }
}

/* === 对话气泡打字效果 === */

.dialogue-typing {
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid var(--text);
  animation:
    typing 1.5s steps(40, end),
    blink-caret 0.5s step-end infinite;
}

@keyframes typing {
  from { width: 0; }
  to { width: 100%; }
}

@keyframes blink-caret {
  50% { border-color: transparent; }
}
```

每个模板直接 `className="anim-bounce-in anim-stagger"` 使用，**零 JS 动画代码**。

### 5.6 角色素材策略

初期方案：**SVG 矢量插画**，每个角色 6 个表情状态。

```
characters/assets/
├── ellie/
│   ├── happy.svg
│   ├── curious.svg
│   ├── worried.svg
│   ├── excited.svg
│   ├── eating.svg
│   └── sleeping.svg
├── foxy/
│   ├── happy.svg
│   ├── determined.svg
│   ├── celebrating.svg
│   └── ...
└── monsters/
    ├── snack_thief/
    │   ├── sneaky.svg
    │   ├── angry.svg
    │   └── defeated.svg
    └── ...
```

SVG 可以用 AI 图像生成工具批量生成统一风格，后续随时替换为专业原画。

---

## 六、后端改动详细设计

### 6.1 planner prompt 重写

核心变化：不再让模型输出 `pages + component_types`，改为输出 `steps: [{ template_id, slots }]`。

```
你是 HappyEllie 的课程编排师。你需要编排一节 8-12 步的英语游戏课。

可用模板（每步只能选一个）：
- story_dialogue: 角色对话，推进剧情
- story_choice: 剧情选择，2-3 个选项
- mission_briefing: 任务介绍
- word_reveal: 教新单词（图+音+例句）
- listen_pick: 听音选图（3-4 选项）
- drag_match: 拖拽匹配（3-4 对）
- choice_battle: 答题打怪（2-3 回合）
- sentence_puzzle: 句子拼装
- speak_repeat: 跟读模仿
- reward_chest: 宝箱奖励
- feed_pet: 喂宠物
- episode_end: 本集结束

编排规则：
1. 第 1 步必须是 story_dialogue 或 mission_briefing
2. 每个新词必须先 word_reveal，再出现在练习中
3. 练习类模板至少用 2 种不同的
4. 中间穿插 story_dialogue 推进剧情（不能连续 3 步都是练习）
5. 倒数第 3 步是 reward_chest
6. 倒数第 2 步是 feed_pet
7. 最后一步是 episode_end
8. 总步骤 8-12 步

你只输出 steps 数组，每个 step 包含 template_id 和 slots。
slots 必须严格遵循每个模板的字段要求。
不要输出任何 HTML、CSS 或动画代码。
```

### 6.2 校验器

使用 Pydantic 对每个 template_id 做 slots 校验：

```python
# backend/app/infra/validation/step_validator.py

from pydantic import BaseModel, ValidationError

class StoryDialogueSlots(BaseModel):
    background: str = "default"
    dialogues: list[DialogueLine]

class ListenPickSlots(BaseModel):
    character: CharacterRef
    audio_text: str
    options: list[PickOption]
    correct_key: str
    success_line: str = "Great job!"
    fail_line: str = "Not quite, try again!"

# ... 每个模板一个 Slots Model

SLOT_VALIDATORS: dict[str, type[BaseModel]] = {
    "story_dialogue": StoryDialogueSlots,
    "listen_pick": ListenPickSlots,
    # ...
}

def validate_step(step: GameStep) -> GameStep:
    validator = SLOT_VALIDATORS.get(step.template_id)
    if validator is None:
        # 未知模板 → 替换为安全的 story_dialogue
        return make_fallback_step(step)
    try:
        validated = validator.model_validate(step.slots)
        step.slots = validated.model_dump()
        return step
    except ValidationError:
        return make_fallback_step(step)
```

### 6.3 LessonService 改动

```python
# lesson_service.py 新增校验环节

def plan_next_lesson(self, payload: LessonRequest) -> LessonResponse:
    # ... 现有 planner + generator 逻辑不变 ...
    
    # 新增：校验每个 step
    validated_steps = [validate_step(step) for step in lesson.steps]
    lesson.steps = validated_steps
    
    return LessonResponse(lesson=lesson, source="generated", blueprint=blueprint)
```

---

## 七、迁移路径（不是推倒重来）

### Phase A：并行开发（1 周）

```
现有 PageRenderer 继续工作
新建 engine/ 和 templates/ 目录
实现 GameEngine 骨架 + 3 个核心模板
新路由 /play 挂载 GameEngine（不影响现有 /lesson）
```

### Phase B：后端 schema 升级（3 天）

```
lesson.py 新增 GameStep + TemplateId
LessonPackage 同时支持 pages 和 steps
RulesLessonPlanner 先输出 steps（硬编码）
RulesLessonGenerator 先输出 steps（硬编码）
API 返回值同时含 pages 和 steps
```

### Phase C：前端切换（1 周）

```
/lesson 页面支持 toggle：旧模式 / 新模式
验证新模式下完整流程跑通
补齐动画和音效
```

### Phase D：AI prompt 切换（3 天）

```
AILessonPlanner prompt 改为输出 steps
AILessonGenerator prompt 改为输出 steps
增加 step 校验器
```

### Phase E：清理（2 天）

```
下线 PageRenderer
下线 pages 字段
下线 /lesson 页面的旧模式 toggle
清理旧的 .game-* CSS
```

---

## 八、一节完整课程的真实数据示例

```json
{
  "package_version": "lesson_package_v3",
  "lesson_id": "lesson-7f3a1b2c",
  "student_id": "student-demo",
  "title": "Forest Snack Hunt - Episode 3",
  "theme": "forest_adventure",
  "estimated_minutes": 7,
  "vocab": ["bread", "juice", "yummy"],
  "story": {
    "arc_key": "forest_adventure",
    "episode_index": 3,
    "episode_title": "The Snack Thief Strikes",
    "recap": "Last time, Ellie and Foxy found a hungry bear cub in the forest.",
    "current_mission": "Find bread and juice for the bear, but watch out for the Snack Thief!",
    "next_hook": "The Snack Thief promised to return with reinforcements..."
  },
  "steps": [
    {
      "step_id": "s1",
      "template_id": "story_dialogue",
      "slots": {
        "background": "forest_path",
        "dialogues": [
          { "character": "foxy", "mood": "excited", "line": "Remember the bear cub from yesterday?" },
          { "character": "ellie", "mood": "happy", "line": "Yes! It was so hungry!" },
          { "character": "foxy", "mood": "determined", "line": "Let's find it some food today!" }
        ]
      },
      "is_interactive": false
    },
    {
      "step_id": "s2",
      "template_id": "mission_briefing",
      "slots": {
        "companion": { "id": "foxy", "line": "Here's our plan:" },
        "objectives": [
          "Learn 3 new food words",
          "Find snacks for the bear cub",
          "Watch out for the Snack Thief!"
        ]
      },
      "is_interactive": false
    },
    {
      "step_id": "s3",
      "template_id": "word_reveal",
      "slots": {
        "word": "bread",
        "meaning": "面包",
        "image_hint": "bread",
        "audio_text": "bread",
        "sentence": "The bear loves bread.",
        "character": { "id": "bear_cub", "mood": "happy", "line": "I love bread!" }
      },
      "is_interactive": false
    },
    {
      "step_id": "s4",
      "template_id": "word_reveal",
      "slots": {
        "word": "juice",
        "meaning": "果汁",
        "image_hint": "juice",
        "audio_text": "juice",
        "sentence": "This juice is yummy.",
        "character": { "id": "foxy", "mood": "excited", "line": "Juice is so refreshing!" }
      },
      "is_interactive": false
    },
    {
      "step_id": "s5",
      "template_id": "listen_pick",
      "slots": {
        "character": { "id": "foxy", "line": "Listen carefully. Which one is it?" },
        "audio_text": "bread",
        "options": [
          { "key": "bread", "image_hint": "bread" },
          { "key": "juice", "image_hint": "juice" },
          { "key": "apple", "image_hint": "apple" }
        ],
        "correct_key": "bread",
        "success_line": "You found the bread!",
        "fail_line": "Listen again — that's bread!"
      },
      "is_interactive": true,
      "reward_on_complete": { "coins": 3 }
    },
    {
      "step_id": "s6",
      "template_id": "drag_match",
      "slots": {
        "character": { "id": "bear_cub", "line": "Help me match the words!" },
        "pairs": [
          { "left": "bread", "right": "面包" },
          { "left": "juice", "right": "果汁" },
          { "left": "yummy", "right": "好吃的" }
        ],
        "match_type": "text_to_text"
      },
      "is_interactive": true,
      "reward_on_complete": { "coins": 5 }
    },
    {
      "step_id": "s7",
      "template_id": "story_dialogue",
      "slots": {
        "background": "forest_clearing",
        "dialogues": [
          { "character": "narrator", "mood": "neutral", "line": "Suddenly, something jumped out of the bushes!" },
          { "character": "snack_thief", "mood": "sneaky", "line": "Those snacks are MINE!" },
          { "character": "foxy", "mood": "determined", "line": "Not today, thief! Let's fight!" }
        ]
      },
      "is_interactive": false
    },
    {
      "step_id": "s8",
      "template_id": "choice_battle",
      "slots": {
        "monster": { "id": "snack_thief", "name": "Snack Thief", "hp": 3 },
        "companion": { "id": "foxy", "line": "Answer correctly to fight back!" },
        "rounds": [
          { "question": "What does 'bread' mean?", "options": ["面包", "牛奶", "果汁"], "answer": "面包", "round_type": "text" },
          { "question": "Which picture is 'juice'?", "options": ["juice", "milk", "water"], "answer": "juice", "round_type": "image" },
          { "question": "'Yummy' means...", "options": ["难吃的", "好吃的", "冷的"], "answer": "好吃的", "round_type": "text" }
        ],
        "victory_line": "The Snack Thief ran away!",
        "defeat_line": "The thief escaped, but we'll get him next time!"
      },
      "is_interactive": true,
      "reward_on_complete": { "coins": 10 }
    },
    {
      "step_id": "s9",
      "template_id": "reward_chest",
      "slots": {
        "total_coins": 18,
        "total_food": { "basic_food": 1, "premium_food": 1 },
        "bonus_item": { "key": "bear_badge", "name": "Bear's Friendship Badge" }
      },
      "is_interactive": false
    },
    {
      "step_id": "s10",
      "template_id": "feed_pet",
      "slots": {
        "available_food": { "basic_food": 1, "premium_food": 1 },
        "pet_current_mood": "hungry"
      },
      "is_interactive": true
    },
    {
      "step_id": "s11",
      "template_id": "episode_end",
      "slots": {
        "episode_summary": "You helped Bear find bread and juice, and defeated the Snack Thief!",
        "next_hook": "But the Snack Thief whispered: 'My big brother will come for you...'",
        "next_episode_hint": "Episode 4: The Thief's Big Brother",
        "companion_farewell": { "id": "foxy", "mood": "winking", "line": "See you tomorrow, adventurer!" }
      },
      "is_interactive": false
    }
  ],
  "reward_preview": { "coins": 18, "food": 2 }
}
```

---

## 九、开发优先级

| 顺序 | 任务 | 工作量 | 阻塞关系 |
|------|------|--------|----------|
| 1 | 后端 schema 新增 `GameStep` + `TemplateId` | 0.5 天 | 无 |
| 2 | 后端 step 校验器 | 0.5 天 | 依赖 1 |
| 3 | `RulesLessonPlanner` + `RulesLessonGenerator` 输出 steps | 1 天 | 依赖 1 |
| 4 | 前端 `engine/` 骨架（GameEngine + types + TemplateRegistry） | 1 天 | 依赖 1 |
| 5 | 前端角色系统（CharacterRenderer + SVG 占位素材） | 1 天 | 无 |
| 6 | 前端 CSS 动画库 | 0.5 天 | 无 |
| 7 | 模板：`story_dialogue` | 1 天 | 依赖 4, 5, 6 |
| 8 | 模板：`word_reveal` | 0.5 天 | 依赖 4, 5, 6 |
| 9 | 模板：`listen_pick` | 1 天 | 依赖 4, 5, 6 |
| 10 | 模板：`choice_battle` | 1.5 天 | 依赖 4, 5, 6 |
| 11 | 模板：`drag_match`（需引入 @dnd-kit） | 1 天 | 依赖 4 |
| 12 | 模板：`mission_briefing` + `speak_repeat` | 1 天 | 依赖 4 |
| 13 | 模板：`reward_chest` + `feed_pet` + `episode_end` | 1 天 | 依赖 4 |
| 14 | 前端新路由 `/play` 完整串联 | 0.5 天 | 依赖 7-13 |
| 15 | AI planner + generator prompt 重写 | 1 天 | 依赖 2 |
| 16 | 旧代码清理 | 0.5 天 | 依赖 14 |
