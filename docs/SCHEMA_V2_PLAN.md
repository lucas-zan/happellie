# HappyEllie Schema V2 Plan

## 目标

在不破坏当前可运行系统的前提下，完成从「旧 pages/block_results 模型」向「steps/events/profile intelligence 模型」的增量迁移。

原则：

- 增量迁移，绝不一次性推翻
- 新路径双写（old + new）
- 读路径逐步切换，最终清理旧字段

## V2 核心表

### 1) `sessions`（保留）

用途：会话总览（课程级汇总）

关键字段：

- `student_id`
- `lesson_id`
- `duration_seconds`
- `total_score`
- `earned_food`
- `earned_coins`
- `wrong_count`
- `created_at`

备注：`block_results_json` 后续将被 `session_steps` 替代，仅作为兼容字段保留。

### 2) `session_steps`（新增）

用途：每个 step 的结构化结果（模板引擎主数据）

关键字段：

- `student_id`
- `lesson_id`
- `step_id`
- `template_id`
- `correct`
- `score`
- `duration_ms`
- `details_json`
- `created_at`

索引：

- `idx_session_steps_student_created`
- `idx_session_steps_lesson`

### 3) `learning_events`（已存在）

用途：细粒度行为流（点击、选择、拖拽、完成等）

关键字段：

- `event_id`
- `session_id`
- `student_id`
- `lesson_id`
- `step_id`
- `template_id`
- `event_type`
- `payload_json`
- `event_at`

### 4) `vocab_mastery`（已存在）

用途：词级掌握度

关键字段：

- `student_id`
- `vocab_key`
- `attempts`
- `correct_count`
- `wrong_count`
- `last_result_correct`
- `last_score`
- `updated_at`

排序策略：错误率 + 遗忘权重（基于 `updated_at`）

### 5) `story_state`（新增）

用途：剧情连续状态（从 profile_json 拆出结构化查询字段）

关键字段：

- `student_id`
- `arc_key`
- `chapter_key`
- `episode_index`
- `last_choice_key`
- `last_choice_tag`
- `unresolved_hooks_json`
- `state_json`
- `updated_at`

## 当前迁移状态

已完成：

- 新表创建：`session_steps`、`story_state`
- 会话完成时双写：
  - 写 `sessions`
  - 写 `session_steps`
  - 写 `vocab_mastery`
  - 写 `story_state`

仍待完成：

- 读取路径优先改读 `session_steps`（替代 `block_results_json`）
- planner 读取 `story_state`（替代 profile 中部分故事字段）
- `sessions.block_results_json` 下线计划

## 迁移阶段

### Phase A（现在）

- 新表就绪
- 双写稳定运行

### Phase B

- 读路径切到新表
- 新增管理面板用于检查 `session_steps` / `story_state` 数据质量

### Phase C

- 旧字段冻结（不再写入）
- 删除或归档旧字段（`block_results_json` 等）

## 验收标准

- 每个 `SessionCompleteRequest` 都能在 `session_steps` 看到对应行
- 每次 story_choice 后，`story_state.last_choice_key/tag` 更新
- 下一课推荐词能从 `vocab_mastery` 稳定回流

