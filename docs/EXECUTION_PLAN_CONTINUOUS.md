# HappyEllie 持续推进执行计划

## 目标定义

围绕最终目标持续推进：  
**用户画像分析 -> 薄弱点定位 -> 个性化剧情剧本 -> 可互动动画游戏 -> 奖励与宠物养成闭环 -> 下一课自动优化。**

本计划只保留与目标一致的能力，不再扩展旧的卡片式课程流程。

## 当前基线（已完成）

- 前端以 `/play` 为主入口，采用 step-based 模板引擎
- 后端输出 `steps`（`template_id + slots`），并带校验兜底
- 已支持核心模板：`story_dialogue`、`word_reveal`、`listen_pick`、`drag_match`、`choice_battle`、`reward_chest`、`feed_pet_step`、`episode_end`
- 已支持事件上报：`/sessions/events` + `learning_events` 存储

## 里程碑计划

### M1：剧情与动画可感知升级（1-2 周）

**目标**：让孩子感知“在玩游戏”，不是“在点表单”。

- 实现 `story_choice` 真分支模板（替换占位实现）
- 增加场景层：森林/校园/夜晚背景 key + 角色站位
- 增加角色状态机：基础情绪切换（happy/curious/worried/excited）
- 增强动效：入场、转场、结算、战斗命中反馈
- 增加音效素材：正确/错误/奖励/转场（先轻量包）

**验收标准**

- 同一课内至少出现 1 次分支选择
- 至少 4 个步骤带明显动画反馈
- 家长和学生能区分“剧情步骤”和“练习步骤”

### M2：画像与薄弱点闭环（1-2 周）

**目标**：课程生成真正由学习表现驱动。

- 引入 `vocab_mastery`（词级掌握度）
- 在画像中增加：薄弱词、兴趣标签、推荐难度
- 将 `learning_events` 转换为快更新信号
- planner 使用最近 3-5 次会话摘要和薄弱词生成剧情

**验收标准**

- 连续 3 次课后，系统能输出稳定的薄弱词列表
- 下一课至少 60% 目标词来自薄弱词 + 复习词策略

### M3：养成系统强化（1-2 周）

**目标**：学习驱动宠物长期成长，而不是一次性奖励。

- 增加 `growth_exp`、`emotion_state`、`equipped_items`
- 上线 `shop`（coins -> food/items）
- 喂养后实时反馈成长和情绪变化
- 结算页展示“本课对宠物成长的影响”

**验收标准**

- 币/粮食/喂养/成长四段链路完整
- 宠物状态变化可被学生直观看到

**当前状态：已完成（核心链路）**

- 已增加 `growth_exp`、`emotion_state`、`equipped_items`
- 已上线 `shop`（支持 food 与 item 购买）
- `feed_pet_step` 已接入真实 API，喂养后实时回传情绪与成长变化
- 结算阶段可展示本课宠物影响（`episode_end` 读取喂养结果）

### M4：多课剧情连续（2 周）

**目标**：形成可持续追更的故事线。

- 新增 `story_events` 持久化
- 引入剧情弧线库（至少 3 条）
- 分支结果可影响下一课任务与角色台词
- 增加章节结构：chapter/episode

**验收标准**

- 连续 5 课能保持同一剧情弧线并有前后呼应
- 分支选择会改变下一课至少 2 处内容

**当前状态：已完成（核心链路）**

- 已完成 `story_events` 持久化，并提供查询接口 `/api/v1/profiles/{student_id}/story-events`
- 已引入 3 条剧情弧线库：`snack_scouts`、`moon_garden`、`ocean_picnic`
- 分支结果已影响下一课任务文案 + 模板路径 + 角色台词
- 已引入 `chapter_key` 结构并随 episode 递进（`chapter_1/2/3`）

## 开发纪律（必须遵守）

- 不再新增旧 `pages/components` 路线功能
- 所有新玩法走模板引擎：`template_id + slots`
- 所有模型输出先校验再渲染
- 所有新交互必须上报事件
- 每个里程碑完成后必须通过构建与 API 烟测

## 风险与应对

- **剧情质量波动**：使用模板+校验+回退文案
- **动画资产不足**：先用统一 SVG 占位，后续替换正式素材
- **画像不稳定**：快更新 + 慢更新双轨，避免一次性重算抖动
- **功能蔓延**：严格按里程碑推进，不平行开新大功能

## 下一步（立即执行）

已完成：

1. 完成 `story_choice` 真分支模板与后端 slots 生成
2. 实装角色站位与情绪渲染
3. 增加 `vocab_mastery` 表并接入画像快更新
4. 产出第一个“连续 3 课剧情”可演示样例数据（`docs/samples/three_lesson_story_demo.json`）

下一批立即执行：

1. ✅ `story_state` 读取回流到 planner（不仅改文案，还影响模板路径）
   - 已落地：`story_last_choice_tag` 直接影响 steps 编排，按分支插入 `word_in_scene` / `mission_briefing` 路径
2. ✅ 增加 `story_events` 表用于章节化剧情回放
   - 已落地：会话完成时写入 `lesson_completed` 事件，形成章节回放数据源
3. ✅ 实装 `shop` API（coins -> food）并改造 `feed_pet_step` 为真实消费链路
   - 已落地：新增 `/api/v1/pets/shop/buy-food`，前端 `feed_pet_step` 先买粮再喂养并上报链路细节
4. ✅ 增加角色资产 manifest（emoji fallback + sprite path），为后续美术替换做零改动接入
   - 已落地：角色渲染由 `characterManifest` 驱动，可直接替换 sprite 路径而无需改模板逻辑

