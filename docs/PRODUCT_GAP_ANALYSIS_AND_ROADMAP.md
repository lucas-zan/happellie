# HappyEllie 产品差距分析与实施路线图

> 文档生成时间：2026-04-13
> 基于当前代码库完整审计后编写
> 
> 配套架构文档：[GAME_ENGINE_ARCHITECTURE.md](./GAME_ENGINE_ARCHITECTURE.md)——游戏模板引擎详细设计

---

## 一、核心问题回答

### 1. 能否做到生成真实剧情类游戏？

**可以，而且当前架构已经为此做了正确的铺垫。**

当前系统已实现的剧情基础：

- `StoryThread` 数据结构已存在，包含 `arc_key`（故事弧线）、`episode_index`（集数）、`recap`（回顾）、`current_mission`（当前任务）、`next_hook`（下集预告）、`characters`（角色列表）
- `ProfileSnapshot` 已持久化剧情状态字段（`story_arc_key`、`story_episode_index`、`story_last_scene`、`story_next_hook`、`story_characters`）
- `SessionService.complete_session` 会将剧情状态写回画像
- `AILessonPlanner` 的 prompt 中已包含"Continue the existing story arc when profile story fields are present"指令
- 下一课生成时，`LessonService` 会读取 `ProfileSnapshot`，将剧情上下文传入 planner

**但当前实现仍然是"轻量连续"而非"真实剧情"，差距在于：**

| 已有 | 缺失 |
|------|------|
| 单线剧情弧线（snack_scouts） | 多条可切换的剧情弧线模板 |
| episode_index 递增 | 剧情分支和选择后果 |
| recap + next_hook 文本 | 跨课程角色记忆和关系演变 |
| 2 个角色（伙伴 + 怪物） | 角色成长、性格变化、新角色解锁 |
| 固定 6 页线性流程 | 基于剧情的动态页面编排 |
| 文本级连续 | 视觉级连续（角色形象稳定识别） |

### 2. 每次生成的游戏能否基于前几次剧情产生关联？

**当前已部分实现，但关联深度不够。**

当前链路：

```
课程完成 → SessionService 将 story 字段写入 ProfileSnapshot
→ 下次请求课程时 LessonService 读取 ProfileSnapshot
→ 将 story_arc_key / episode_index / next_hook / characters 传入 AILessonPlanner
→ planner prompt 要求"延续已有剧情弧"
```

需要增强的关联维度：

| 维度 | 当前状态 | 目标状态 |
|------|----------|----------|
| 剧情线索 | 只有 next_hook 文本 | 结构化的剧情事件日志 |
| 角色记忆 | 只存 name 列表 | 角色关系图谱 + 好感度 |
| 词汇复现 | 无 | 错误词自动在后续剧情中复现 |
| 场景连续 | 无 | 上一课的场景可被引用（"还记得上次在森林里吗？"） |
| 情感连续 | 无 | 孩子的选择影响后续角色态度 |
| 难度渐进 | 固定 starter | 基于历史表现动态调整 |

---

## 二、小学生视角的产品设计分析

### 心理学依据

小学生（6-12 岁）的核心心理特征：

1. **即时反馈依赖**：这个年龄段的注意力窗口约 8-15 分钟，需要每 15-30 秒有一次正向反馈
2. **角色认同感**：会将虚拟宠物当作"自己的朋友"，投入真实情感
3. **收集欲和成长感**：对"变多、变强、变大"有天然的满足感
4. **社交展示欲**：想让同学看到自己的宠物有多酷
5. **故事沉浸感**：愿意为"救朋友""帮助小动物"而主动学习
6. **恐惧厌学**：任何"像考试"的东西都会触发抵触

### 产品设计合理性评估

| 设计决策 | 评价 | 说明 |
|----------|------|------|
| 宠物作为核心情感锚点 | 优秀 | 电子宠物是当前小学生群体最强的情感连接载体，拓麻歌子/旅行青蛙式的"养成牵挂"能产生每日打开的动力 |
| 学习换虚拟币换粮食 | 合理 | 将"不得不学"转化为"我想喂它"，动机从外部转为内部 |
| 闯关/情景/角色扮演 | 优秀 | 游戏化包装是这个年龄段最有效的学习伪装 |
| AI 个性化分析 | 有前景 | 但需要让孩子感知到"这个游戏懂我"，而不是冷冰冰的标签 |
| 剧情连续 | 关键差异点 | 市面上绝大多数教育产品是"一次性关卡"，连续剧情是竞争壁垒 |

### 产品前景评估

**有前景，但有前提条件。**

利好因素：

- 双减政策后，家长对"快乐学习"的需求大增
- 电子宠物热潮在小学生群体中持续
- AI 个性化是教育产品的核心趋势
- 剧情 + 宠物 + 英语的交叉定位目前市场空白

风险因素：

- 内容质量（AI 生成的游戏是否真的好玩）
- 视觉体验（小朋友对"好看"的要求极高）
- 家长信任（需要证明学习效果，不只是玩）
- 留存挑战（7 天后孩子是否还想回来）

### 当前产品与小学生期望的差距

**从一个 8 岁孩子的视角体验当前产品：**

1. **打开 App**："这是什么？看起来像大人用的程序"——当前 UI 无低龄化设计，文字为主，缺乏色彩和动画
2. **开始学习**："要我自己打字输入单词？太难了"——需要手动输入逗号分隔词
3. **游戏过程**："就是看文字然后点按钮，和做题一样无聊"——缺乏听音、拖拽、收集等互动
4. **角色形象**："Ellie 在哪里？我只看到 emoji"——无真实角色图形
5. **完成课程**："就显示了一行字？我的奖励呢？"——无结算动画、无奖励演出
6. **看宠物**："它也不动，喂了也没反应"——无宠物动画和情绪反馈
7. **第二天**："昨天的故事是什么来着？跟今天有关系吗？"——剧情连续感不够强

---

## 三、完整差距清单

### A. 剧情系统差距

| ID | 差距项 | 当前状态 | 目标状态 | 优先级 |
|----|--------|----------|----------|--------|
| S1 | 剧情弧线模板库 | 只有 snack_scouts 一条线 | 至少 5 条不同主题的弧线模板 | P1 |
| S2 | 剧情事件日志 | 无 | `story_events` 表记录每课剧情事件 | P1 |
| S3 | 角色关系图谱 | 只存 name 列表 | 角色 + 好感度 + 互动记录 | P2 |
| S4 | 剧情分支机制 | 线性固定 | 基于孩子选择产生分支 | P2 |
| S5 | 词汇-剧情融合选词 | 分离 | 薄弱词自动编入下一课剧情 | P1 |
| S6 | 跨课场景引用 | 无 | recap 引用具体上次场景 | P1 |
| S7 | 多季多章结构 | 无 | season → chapter → episode 三层结构 | P2 |

### B. 游戏互动差距

| ID | 差距项 | 当前状态 | 目标状态 | 优先级 |
|----|--------|----------|----------|--------|
| G1 | 互动组件数量 | 9 种（多为展示型） | 至少 15 种（含 6 种强互动） | P0 |
| G2 | listen_pick（听音选图） | 缺失 | 播放单词音频，点选对应图片 | P0 |
| G3 | drag_match（拖拽匹配） | 缺失 | 将单词拖到对应图片/中文 | P0 |
| G4 | story_choice（剧情选择） | 缺失 | 2-3 个选项影响剧情走向 | P1 |
| G5 | collect_item（收集道具） | 缺失 | 答对后收集剧情道具 | P1 |
| G6 | mini_battle（怪物挑战） | 缺失 | 答题打败怪物的战斗演出 | P1 |
| G7 | sentence_build（造句拼装） | 缺失 | 拖拽单词组成句子 | P2 |
| G8 | 页面类型扩展 | 6 种固定页面 | 至少 10 种页面类型 | P1 |
| G9 | 动态页面编排 | 固定 6 页顺序 | planner 根据剧情和难度动态编排 | P1 |

### C. 视觉与体验差距

| ID | 差距项 | 当前状态 | 目标状态 | 优先级 |
|----|--------|----------|----------|--------|
| V1 | 角色视觉资产 | emoji 占位 | Ellie + 伙伴 + 怪物的真实图形素材 | P0 |
| V2 | 宠物 avatar 系统 | 无 | base_avatar_key + 表情 + 成长阶段分层渲染 | P0 |
| V3 | 页面转场动画 | 无 | 页面切换时滑动/淡入效果 | P1 |
| V4 | 奖励演出动画 | 无 | 金币飞入、食物弹出、星星闪烁 | P1 |
| V5 | 宠物喂食动画 | 无 | 喂食时宠物张嘴吃东西 + 表情变化 | P1 |
| V6 | 答题反馈动画 | 无 | 正确时绿色闪光 + 伙伴欢呼；错误时温柔鼓励 | P1 |
| V7 | 低龄化 UI 主题 | 开发者风格 | 圆角、大字、鲜艳配色、卡通风格 | P0 |
| V8 | 资源预加载 | 无 | asset_manifest + 预取策略 | P2 |

### D. 音频差距

| ID | 差距项 | 当前状态 | 目标状态 | 优先级 |
|----|--------|----------|----------|--------|
| A1 | TTS 真实接入 | mock/disabled | 接入真实 TTS（如 Azure/OpenAI） | P0 |
| A2 | 单词发音播放 | 无 | word_card 和 listen_pick 点击播放 | P0 |
| A3 | 背景音效 | 无 | 答对/答错/翻页/奖励音效 | P1 |
| A4 | 音频缓存 | 无 | audio_cache 避免重复合成 | P1 |

### E. 学习系统差距

| ID | 差距项 | 当前状态 | 目标状态 | 优先级 |
|----|--------|----------|----------|--------|
| L1 | 细粒度事件采集 | 仅课程结束提交 | 页面级、组件级事件流 | P1 |
| L2 | learning_events 表 | 缺失 | event_type + payload + timestamp | P1 |
| L3 | 画像快慢更新 | 仅同步重算 | 快更新（计数） + 慢更新（AI 分析） | P2 |
| L4 | 词汇掌握度追踪 | 无 | 每个词的正确率、遗忘曲线位置 | P1 |
| L5 | 下节课自动建议 | 弱 | next_lesson_hint 含词+主题+难度 | P1 |
| L6 | 画像可视化 | 无前端页面 | 家长可查看孩子学习标签和进度 | P2 |

### F. 奖励与宠物差距

| ID | 差距项 | 当前状态 | 目标状态 | 优先级 |
|----|--------|----------|----------|--------|
| R1 | 虚拟币兑换粮食 | 链路断裂 | coins 通过 shop 购买不同 food | P1 |
| R2 | 多种粮食类型 | 仅 basic_food | 至少 4 种（对应不同成长效果） | P1 |
| R3 | 宠物经验值 | 无 | growth_exp 累积升级 growth_stage | P1 |
| R4 | 宠物情绪系统 | 无 | emotion_state 受喂食/互动影响 | P2 |
| R5 | 宠物装扮系统 | 无 | equipped_items 可用 coins 购买 | P2 |
| R6 | 过程奖励 | 无 | 答对即时获得小奖励 | P1 |
| R7 | 独立 RewardService | 混在 SessionService | 单独服务管理奖励发放和消费 | P1 |

### G. 产品入口差距

| ID | 差距项 | 当前状态 | 目标状态 | 优先级 |
|----|--------|----------|----------|--------|
| P1 | 词库选择页 | 手动输入逗号分隔 | 可视化勾选 + 智能推荐 | P1 |
| P2 | 自动开始下一课 | 需重新手动操作 | 完课后一键开始推荐的下一课 | P1 |
| P3 | 家长画像面板 | 无 | 展示学习标签、薄弱词、进度 | P2 |
| P4 | 课后复盘页 | 无 | 展示本课学了什么、哪里错了 | P2 |
| P5 | 每日任务 | 无 | "今天的冒险" 入口 | P2 |

---

## 四、实施路线图

### Phase 0：让游戏"看得见"（预计 1-2 周）

**目标：从开发者 demo 变成小朋友愿意看的界面。**

| 序号 | 任务 | 说明 | 涉及文件/模块 |
|------|------|------|--------------|
| 0.1 | 设计低龄化 UI 主题 | 圆角卡片、大字体、鲜艳配色、卡通图标 | `frontend/src/styles.css` + 新主题文件 |
| 0.2 | 建立角色素材系统 | 为 Ellie、伙伴动物、怪物建立 avatar_key → 图片映射 | 新建 `frontend/src/assets/characters/` + `CharacterRegistry` |
| 0.3 | 宠物 avatar 渲染 | 替换 emoji 为分层图片渲染（base + 表情 + 成长阶段） | `PetAvatarCard.tsx` 重构 |
| 0.4 | 接入真实 TTS | 选择一个 TTS 服务商（推荐 Azure/OpenAI），实现 `TextToSpeechProvider` | `backend/app/infra/tts/` 新增实现 |
| 0.5 | 前端音频播放 | word_card 和 repeat_prompt 支持点击播放音频 | `PageRenderer.tsx` + 新 `AudioPlayer` 组件 |

### Phase 1：让游戏"好玩"（预计 2-3 周）

**目标：补齐核心互动组件，让一节课的游戏感显著增强。**

| 序号 | 任务 | 说明 | 涉及文件/模块 |
|------|------|------|--------------|
| 1.1 | 新增 `listen_pick` 组件 | 后端：schema 增加类型 + generator prompt；前端：播放音频 → 点选图片 | `lesson.py` + `PageRenderer.tsx` |
| 1.2 | 新增 `drag_match` 组件 | 后端：schema + prompt；前端：拖拽单词到对应含义 | 同上 + 前端拖拽库 |
| 1.3 | 新增 `story_choice` 组件 | 后端：schema + prompt；前端：展示 2-3 个剧情选项，选择后影响后续 | 同上 |
| 1.4 | 新增 `mini_battle` 组件 | 后端：schema + prompt；前端：答题打败怪物的简单战斗演出 | 同上 |
| 1.5 | 新增 `collect_item` 组件 | 答对后收集一个剧情道具，课后在宠物页展示 | 同上 |
| 1.6 | 扩展 PageType | 新增 `challenge`、`story_branch`、`boss`、`recap` 页面类型 | `lesson.py` PageType |
| 1.7 | 动态页面编排 | planner 根据剧情和难度选择不同 page 组合模板 | `AILessonPlanner` prompt 重构 |
| 1.8 | 基础动画系统 | 页面转场（slide）、答题反馈（shake/glow）、奖励飞入 | 前端 CSS/JS 动画 |

### Phase 2：让剧情"连起来"（预计 2-3 周）

**目标：实现跨课程的真实剧情连续。**

| 序号 | 任务 | 说明 | 涉及文件/模块 |
|------|------|------|--------------|
| 2.1 | 剧情弧线模板库 | 设计至少 5 条主题弧线（森林探险、海洋冒险、太空旅行、校园故事、美食大赛） | 新建 `backend/config/story_arcs/` |
| 2.2 | 剧情事件日志 | 新建 `story_events` 表，记录每课的关键剧情节点 | `schema.py` + 新 `StoryRepository` |
| 2.3 | 增强 StoryThread | 增加 `previous_episodes_summary`、`character_relationships`、`unresolved_hooks` | `lesson.py` StoryThread |
| 2.4 | planner 多课剧情上下文 | planner 接收最近 3-5 课的剧情摘要，生成真正有延续感的剧本 | `AILessonPlanner` prompt 增强 |
| 2.5 | 词汇-剧情融合 | 薄弱词自动作为下一课剧情的关键词编入 | `LessonPlanner.plan` 逻辑 |
| 2.6 | 角色成长系统 | 伙伴角色有好感度，不同课之间关系会变化 | `ProfileSnapshot` + `StoryCharacter` 增强 |

### Phase 3：让闭环"转起来"（预计 2 周）

**目标：完善奖励 → 宠物成长的完整激励闭环。**

| 序号 | 任务 | 说明 | 涉及文件/模块 |
|------|------|------|--------------|
| 3.1 | 独立 RewardService | 从 SessionService 中拆出奖励逻辑 | 新建 `reward_service.py` |
| 3.2 | 虚拟币商店 | coins 购买不同类型粮食的 API 和前端页面 | 新 API + 前端 `ShopPage` |
| 3.3 | 多种粮食类型 | basic_food / premium_food / treat / special_item | `pet.py` 增强 |
| 3.4 | 宠物经验值系统 | growth_exp 累积，达到阈值升级 growth_stage | `PetService` + `PetSummary` |
| 3.5 | 宠物情绪系统 | emotion_state（开心/饿了/想你了），影响前端表情渲染 | `PetSummary` + `PetAvatarCard` |
| 3.6 | 过程奖励 | 答对单题即获得小额 coins，前端即时动画反馈 | `PageRenderer` + `SessionService` |
| 3.7 | 喂食动画和反馈 | 喂食时播放宠物吃东西动画 + 满足度变化 | `PetCarePanel` 重构 |

### Phase 4：让个性化"准起来"（预计 2-3 周）

**目标：学习系统真正了解每个孩子。**

| 序号 | 任务 | 说明 | 涉及文件/模块 |
|------|------|------|--------------|
| 4.1 | 细粒度事件采集 | 前端记录 page_enter / answer / drag / audio_play 等事件 | 前端事件收集器 + 新 API |
| 4.2 | learning_events 表 | 存储所有学习事件 | `schema.py` |
| 4.3 | 词汇掌握度追踪 | 每个词的正确率、出现次数、最后答对时间 | 新建 `vocab_mastery` 表 |
| 4.4 | 画像快慢更新 | 快更新（每次事件）+ 慢更新（定时 AI 重分析） | `ProfileAnalyzer` 分层 |
| 4.5 | 词库扩充 | 从 15 词扩展到覆盖小学 1-6 年级核心词汇（约 800-1200 词） | `vocab_library.json` 或迁移到数据库 |
| 4.6 | 词库选择页 | 可视化选词 + 基于画像的智能推荐候选 | 前端 `VocabSelectPage` + API |
| 4.7 | 下节课自动建议 | 基于画像 + 剧情 + 遗忘曲线自动推荐下一课内容 | `LessonPlanner` + 前端展示 |

### Phase 5：让产品"活起来"（预计 2-3 周）

**目标：补齐产品化功能。**

| 序号 | 任务 | 说明 | 涉及文件/模块 |
|------|------|------|--------------|
| 5.1 | 家长画像面板 | 展示学习标签、薄弱点、进步趋势 | 前端 `ParentDashboard` |
| 5.2 | 课后复盘页 | 本课学了什么、哪里答错、剧情回顾 | 前端 `LessonReviewPage` |
| 5.3 | 每日任务入口 | "今天的冒险" 一键开始 | 前端 `HomePage` 重构 |
| 5.4 | 宠物装扮系统 | coins 购买装饰品 | `PetSummary` + 前端 |
| 5.5 | LessonPackage 校验器 | AI 生成后 schema 校验，不通过回退安全模板 | 新建 `PackageValidator` |
| 5.6 | 推送/提醒系统 | "Ellie 饿了，快来喂它" | 通知接口 |

---

## 五、技术实施指南

> 完整技术选型和架构设计见 [GAME_ENGINE_ARCHITECTURE.md](./GAME_ENGINE_ARCHITECTURE.md)

### 核心架构决策：游戏模板引擎

**AI 不生成游戏，AI 填充游戏。**

每个游戏模板（`story_dialogue` / `listen_pick` / `choice_battle` 等）是前端预先编码好的完整组件，自带布局、动画、交互逻辑和音效。AI 只输出 `template_id` + `slots`（填什么内容）。

技术选型：
- 后端不新增依赖，Pydantic v2 做 slots 校验
- 前端只新增 @dnd-kit/core（拖拽交互），其余全部零依赖
- 动画全部纯 CSS @keyframes，不引入动画库
- 音效用原生 `<audio>` + 小体积 mp3
- 角色初期用 SVG 矢量插画，后续可替换原画

改动量：60% 保留 / 25% 重写 / 15% 新增。

### 剧情连续系统的具体实现方案

#### 5.1 数据模型增强

```python
# backend/app/schemas/lesson.py 增强

class StoryThread(BaseModel):
    arc_key: str = "snack_scouts"
    season: int = 1
    chapter: int = 1
    episode_index: int = 1
    episode_title: str = ""
    recap: str = ""
    previous_episodes_summary: list[str] = []     # 最近 3-5 课摘要
    current_mission: str = ""
    next_hook: str = ""
    unresolved_hooks: list[str] = []               # 未解决的伏笔
    characters: list[StoryCharacter] = []
    character_relationships: dict = {}             # {char_id: {mood, trust_level}}
    collected_items: list[str] = []                # 本弧线收集的道具
    branching_context: dict = {}                   # 上一课的选择及后果
```

#### 5.2 剧情弧线模板结构

```json
{
  "arc_key": "forest_adventure",
  "title": "森林大冒险",
  "description": "Ellie 和朋友们探索神秘森林，寻找丢失的宝藏",
  "target_age": [6, 9],
  "total_episodes": 12,
  "chapters": [
    {
      "chapter": 1,
      "title": "初入森林",
      "episodes": 4,
      "vocab_themes": ["animal", "nature", "greeting"],
      "key_characters": ["fox_helper", "bear_rival"],
      "tension_curve": "gentle_rise"
    }
  ],
  "recurring_characters": [
    {
      "character_id": "fox_helper",
      "name": "Foxy",
      "kind": "companion",
      "personality": "curious and helpful",
      "growth_arc": "from shy to brave"
    }
  ]
}
```

#### 5.3 planner prompt 重写方案

从"输出 pages + components"改为"输出 steps + template_id + slots"。

详见 [GAME_ENGINE_ARCHITECTURE.md 第六节](./GAME_ENGINE_ARCHITECTURE.md)。

#### 5.4 每个模板的 slots 规范

详见 [GAME_ENGINE_ARCHITECTURE.md 第四节](./GAME_ENGINE_ARCHITECTURE.md)。

### 虚拟币 → 粮食 → 宠物的完整闭环实现

```
答对单题 → 获得 3 coins（即时，模板内奖励动画）
完成练习步骤 → 获得 5 coins（step.reward_on_complete）
Boss 战胜利 → 获得 10 coins（+ 特殊食物）
完成整课 → reward_chest 模板展示总奖励

商店：
  basic_food:    10 coins  → hunger +10, growth_exp +5
  premium_food:  25 coins  → hunger +20, growth_exp +15
  treat:         15 coins  → affection +15, emotion → happy
  special_item:  50 coins  → equipped_items（装扮）

宠物成长：
  growth_exp 0-100:   stage 1 (baby)
  growth_exp 100-300: stage 2 (child)
  growth_exp 300-600: stage 3 (teen)
  growth_exp 600+:    stage 4 (adult)
```

---

## 六、我（AI 助手）可以直接帮你实现的部分

| 类别 | 可实现 | 说明 |
|------|--------|------|
| 后端 schema 增强 | 全部 | StoryThread、PetSummary、新组件类型、新表 |
| 后端接口与服务 | 全部 | RewardService、ShopAPI、事件采集 API、剧情日志 |
| AI planner/generator prompt | 全部 | 剧情增强 prompt、新组件生成规则 |
| 前端新组件开发 | 全部 | listen_pick、drag_match、story_choice 等渲染 |
| 前端页面重构 | 全部 | 词库选择页、商店页、家长面板 |
| CSS/动画 | 大部分 | 低龄化主题、转场动画、基础反馈动画 |
| 数据库迁移 | 全部 | 新表、字段迁移 |
| 词库扩充 | 全部 | 结构化词库数据生成 |
| TTS 接入 | 全部 | 对接 Azure/OpenAI TTS |
| LessonPackage 校验器 | 全部 | schema 校验 + 回退逻辑 |

| 类别 | 需要你参与 | 说明 |
|------|------------|------|
| 角色原画设计 | 需美术设计 | Ellie、伙伴、怪物的视觉设计稿 |
| 音效素材 | 需素材采购 | 答对/答错/翻页/BGM |
| 精细动画 | 需动效设计 | Lottie/Spine 等复杂角色动画 |
| 剧情弧线文案 | 可 AI 生成初稿，需审核 | 确保内容适合低龄儿童 |
| TTS 服务商账号 | 需你注册 | API key 配置 |
| 真实用户测试 | 需你组织 | 找几个小朋友试玩反馈 |

---

## 七、建议的启动顺序

> 详细架构设计和技术选型见 [GAME_ENGINE_ARCHITECTURE.md](./GAME_ENGINE_ARCHITECTURE.md)

架构决策结论：**不是推倒重来，而是在稳固地基上换上层建筑。**
- 约 60% 代码保留不动（接口层、仓库、配置、DI 容器、基础 UI 组件）
- 约 25% 代码重写/扩展（planner prompt、generator prompt、schema、前端游戏页面）
- 约 15% 代码新增（GameEngine、游戏模板、角色系统、CSS 动画库）

```
第 1 步：后端 schema 升级 → GameStep + TemplateId + 校验器
       ↓ 所有后续工作的数据基础

第 2 步：前端 GameEngine 骨架 + CSS 动画库 + 角色占位系统
       ↓ 游戏容器就位

第 3 步：实现 3 个核心模板（story_dialogue + listen_pick + choice_battle）
       ↓ 一节最小可玩的真正游戏

第 4 步：Rules planner/generator 输出 steps，前端 /play 路由串联
       ↓ 端到端跑通新架构

第 5 步：AI planner/generator prompt 重写，输出 template_id + slots
       ↓ AI 生成的内容也走模板引擎

第 6 步：补齐其余模板（drag_match + word_reveal + reward_chest + feed_pet + episode_end）
       ↓ 完整游戏体验

第 7 步：剧情弧线模板库 + planner 多课上下文增强
       ↓ 跨课剧情真正连续

第 8 步：奖励闭环（RewardService + 商店 + 多种粮食 + 宠物 exp）
       ↓ 激励系统完整跑通

第 9 步：事件采集 + 词汇掌握度 + 画像增强
       ↓ 个性化系统上线

第 10 步：接入真实 TTS + 音频播放
       ↓ 英语学习核心体验补齐

第 11 步：家长面板 + 课后复盘 + 每日任务
        ↓ 产品化收尾
```

---

## 八、关键风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| AI 生成的剧情质量不稳定 | 孩子遇到荒谬剧情失去兴趣 | LessonPackage 校验器 + 安全回退模板 |
| TTS 延迟影响体验 | 点击后等太久孩子失去耐心 | 音频预生成 + 缓存 + 离线包 |
| 宠物新鲜感衰减 | 2 周后孩子不再关心宠物 | 定期引入新物种/新装扮/限时活动 |
| 词库覆盖不全 | 学校课本的词没有覆盖到 | 支持家长自定义词库 + 教材对齐 |
| 家长对"玩游戏"的抵触 | 觉得孩子是在玩不是在学 | 家长面板展示学习数据 + 每课复盘 |

---

## 九、竞品差异化总结

| 维度 | 典型竞品（如某某英语/某某口语） | HappyEllie 的定位 |
|------|-------------------------------|-------------------|
| 课程形态 | 固定课件 + 录播 + 跟读 | AI 生成的个性化剧情游戏 |
| 激励系统 | 积分 + 勋章 | 电子宠物养成（情感连接） |
| 个性化 | 按年级分班 | 按个人画像和薄弱点动态调整 |
| 故事连续性 | 无 / 弱 | 多课连续剧情，选择影响后续 |
| 游戏感 | 偏教育 | 偏游戏（学习被剧情包装） |

这是 HappyEllie 最大的差异化机会：**不是"教育产品加了游戏元素"，而是"游戏产品里内嵌了学习"**。
