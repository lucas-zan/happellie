# HappyEllie 游戏页面生成差距说明

## 状态快照

以下能力已经完成：

- `LessonPackage` 已从扁平 `blocks` 升级为 `pages + components`
- 前端已实现页面级渲染器
- 已有可游玩的分页流程：`hero -> learn -> quiz -> repeat -> settlement -> feed_pet`
- 模型/规则生成结果仍然是结构化 JSON，不是任意 HTML
- 已接入轻量剧情线，可根据上一课的剧情状态延续下一课
- 已加入伙伴动物和柔和怪物遭遇卡

以下能力仍未完成：

- 固定宠物与角色视觉素材系统
- 更强的互动机制，如拖拽、听音选图、收集玩法
- 细粒度页面事件流和后台重分析 job
- 更完整的奖励演出和宠物成长单元

本文件下面的“差距”内容保留，作为下一阶段的设计参考。

## 背景

当前项目已经实现了一个可运行的闭环：

1. 选择一组单词
2. 后端生成一个分页课程/游戏包
3. 前端按固定页面和组件合同渲染
4. 提交结果后发放 food / coin
5. 喂宠物并查看画像与统计

这套实现已经证明“学习 -> 奖励 -> 喂养 -> 下次剧情延续”的基本链路，但还没有达到“完整低龄儿童英语剧情游戏”的目标。

当前点击“生成课程”后，已经会返回页面级游戏包并进入分页游玩流程。但仍缺完整角色视觉系统、更丰富玩法和更强的剧情分支能力。

## 目标定义

这里的“生成游戏页面”不建议理解为：

- 让模型直接生成任意 HTML
- 让模型直接生成前端代码
- 让前端执行模型返回的脚本

更稳的做法应当是：

1. 后端生成受约束的 `LessonPackage` 页面 DSL
2. 前端只渲染白名单页面类型和组件类型
3. 前端负责互动、反馈、埋点和状态机
4. 后端负责选词、出课、奖励、画像和宠物状态更新

这样才能保证：

- UI 风格稳定
- 页面结构可缓存、可回放
- 模型输出可校验
- 宠物资产不会被课程生成污染

## 当前实现与目标的核心差距

### 1. 固定视觉资产体系还未完成

页面级 DSL 已完成，当前差距不在合同本身，而在视觉资产层。

需要补齐：

- `base_avatar_key`
- 伙伴动物固定形象 key
- 怪物固定形象 key
- 角色分层素材
- 表情和成长状态的渲染规则

目标是保证剧情延续时，Ellie、伙伴和怪物都保持稳定识别度。

### 2. 前端仍缺更强的游戏演出层

当前前端已有 `PageRenderer` 和分页推进逻辑，但演出仍偏轻。

需要补齐：

- 页面转场动画
- 结算动画
- 角色反应动画
- 页面资源预加载
- 更明确的低龄化视觉节奏

### 3. 互动组件仍然偏少，不足以构成更强游戏感

当前已有剧情、遭遇、选择、跟读、奖励、喂食，但互动深度还不够。

至少应补齐这些组件类型：

- `listen_pick`
- `drag_match`
- `result_badge`
- `pet_reaction`
- `collect_item`
- `story_choice`
- `mini_battle_prompt`

每个组件需要定义：

- 输入 payload schema
- 前端交互规则
- 正误反馈样式
- 是否上报事件
- 是否依赖音频 / 图片资源

### 4. 课程生成链路仍然过于固定

当前虽然已经是页面包，但主流程仍然基本固定在 6 页线性顺序里，剧情变化还不够大。

需要补齐：

- 更丰富的 page plan 组合
- 剧情节奏模板
- 怪物/伙伴的章节变化
- 更灵活的奖励节奏
- package 生成后做 schema 校验
- 未通过校验时回退到缓存或安全模板

建议链路改为：

1. `candidate_vocab` 选词候选集
2. planner 生成 `LessonBlueprint`
3. generator 生成 `LessonPackage`
4. validator 校验 package
5. cache 存储 package
6. frontend 渲染 package

### 5. 学习过程仍缺少细粒度事件采集

当前只有课程完成时统一提交 `block_results`，还没有页面级、组件级事件流。

要做游戏页面，至少需要记录：

- 页面进入
- 音频播放
- 选项点击
- 拖拽完成
- 跟读提交
- 页面完成
- 退出中断

建议新增：

- `learning_events` 表
- `session/start`
- `session/step`
- `session/finish`
- 前端事件缓冲与批量提交

推荐事件结构：

```json
{
  "event_id": "evt_123",
  "session_id": "sess_001",
  "student_id": "stu_001",
  "package_id": "lesson_20260412_ab12",
  "page_id": "p3",
  "component_id": "quiz_1",
  "event_type": "answer_submitted",
  "payload": {
    "selected_key": "apple",
    "is_correct": true,
    "duration_ms": 4200
  }
}
```

### 6. 奖励和宠物联动仍不够细

当前奖励能发放，但“游戏页面 -> 奖励面板 -> 喂食 -> 成长反馈”的演出不够完整。

需要补齐：

- `reward_service`
- 课内奖励预览与结算一致性
- 多种 food 类型
- `shop` 或 food purchase 逻辑
- `feed_panel` 页面组件
- 宠物喂食后的即时视觉反馈

至少应支持：

- 学完立刻获得 food / coin
- 进入结算页展示奖励
- 点击喂食按钮消耗 food
- 返回最新宠物快照
- 前端按快照显示宠物反馈

### 7. 宠物模型仍不够支撑“形象一致 + 成长单元”

当前宠物只有：

- `species`
- `hunger`
- `weight`
- `affection`
- `growth_stage`

这还不够支撑“宠物形象长期稳定”和“成长最小单元”的目标。

需要补齐的宠物字段：

- `base_avatar_key`
- `body_params`
- `growth_stage`
- `growth_exp`
- `satiety`
- `weight_score`
- `emotion_state`
- `food_inventory`
- `equipped_items`

成长建议拆成两层：

- 长期成长：`growth_exp` 达阈值后提升 `growth_stage`
- 短期状态：`satiety / emotion_state / weight_score`

原则：

- 课程不能直接修改宠物外观资源
- 课程只能产出 reward event
- 宠物页只根据 `PetProfile` 快照渲染

### 8. 画像更新还没进入“快更新 + 慢更新”结构

当前画像主要在 `session complete` 后同步重算一次，还没有独立的慢更新机制。

需要补齐：

- 实时轻更新
- 定时重分析 job
- `profile/recompute` 调试接口
- `next_lesson_hint`
- 更明确的标签到课程选择映射

建议分层：

- 快更新：错误计数、完成率、偏好组件、退出率
- 慢更新：薄弱点、兴趣标签、推荐难度、下节课建议

### 9. 资源系统还不完整

低龄儿童向游戏页面通常依赖：

- 音频
- 图片
- 宠物反应资源
- 页面插图

当前 TTS 仍是 disabled / mock 为主，也没有图片缓存和资源索引。

需要补齐：

- `audio_cache`
- `image_cache`
- `asset_manifest`
- 页面加载前的资源预取
- 音频播放状态管理

### 10. 词库选择和家长控制页还不完整

你提出的是“第一次根据选择的单词开始生成游戏”，但当前前端还是手工输入逗号分隔词。

需要补齐：

- 词库查询接口
- 词库选择页
- 已学 / 未学 / 薄弱词筛选
- 家长固定词入口
- 下节课词组确认页

最低可用版本应支持：

- 勾选 3 到 5 个词
- 预览本课主题和时长
- 点击生成游戏

## 建议的功能拆分

### P0：先让“课程预览”变成“可玩的页面”

必须完成：

- 升级 `LessonPackage` 为页面级 DSL
- 前端新增页面渲染器和状态机
- 新增 `hero / learn / quiz / settlement / feed_pet` 页面类型
- 新增 `choice_quiz / reward_panel / feed_panel / pet_reaction` 组件
- 增加页面级事件采集

完成标准：

- 一节课至少 4 页
- 每页只有一个主要动作
- 小朋友可连续点下一页完成一局
- 完成后能结算并喂宠物

### P1：补足“生成感”和“复用能力”

必须完成：

- planner / generator 输出真实 page plan
- package schema 校验
- package 缓存
- prompt_version / model_name 持久化
- 词库选择页

完成标准：

- 不同词组可以生成不同课程页面
- 同样输入可以命中缓存
- 生成结果可复盘

### P2：补足“成长”和“个性化”

必须完成：

- 宠物成长最小单元
- 多 food 类型和购买逻辑
- learning_events 表
- profile 快慢更新
- 下节课自动建议

完成标准：

- 喂食后不只是数值变化，而是有持续成长逻辑
- 下一课内容能体现孩子弱项和兴趣

## 推荐的开发顺序

1. 先改后端 schema，把 `LessonPackage` 升级为 `pages + components`
2. 再改前端渲染器，让一节课真正按页进行
3. 然后补齐 `session/start`、`session/step`、`session/finish`
4. 再补 `reward_panel + feed_panel + pet_reaction`
5. 再重构 `PetProfile`，加入成长单元
6. 最后补 `learning_events + profile recompute + next lesson hint`

## 不建议的做法

- 不要让模型直接生成 HTML / React 代码
- 不要让模型直接决定宠物外观资源
- 不要在首版就做完全自由的课程流程
- 不要把画像做成长篇报告后再让前端自己理解

## 结论

要把当前项目升级成“点击生成后，真正出现可玩的游戏页面”，核心不是再多加几个 block，而是补齐这 5 个基础能力：

1. 页面级 `LessonPackage` 合同
2. 前端页面渲染器和状态机
3. 组件级互动与事件采集
4. 奖励到宠物的完整演出链路
5. 宠物独立资产和成长最小单元

只有这几个底座补齐后，模型生成的内容才会真正落到“游戏页面”上，而不是继续停留在“课程块预览”。
