# flow_config YAML 配置说明

YAML 不是神秘配置，而是**流程说明书**。代码是引擎，YAML 是剧本。

| 文件 | 角色 | 例子 |
|---|---|---|
| `user_flows.yml` | **业务目标**：用户要办的事 | 查订单、查物流、退款、推荐商品、转人工 |
| `system_flows.yml` | **系统过场**：引擎自己播的话术/问询 | 开始了、中断了、恢复了、请填槽、取消了 |

- `user_flows.yml` 里还有 `slots`：这件事需要收集哪些字段（订单号、退款原因等）
- 两个文件都会被 `FlowLoader` 加载进同一个 `FlowsList`
- 执行时系统流程优先于业务任务（`current_active_task()` = 系统 or 业务）

---

## 两个文件里的 flows 有什么区别

结构写法一样（都是 `flows` + `steps`），差别在**谁触发、干什么**。

### user_flows：办什么事

给 LLM 选、用户能直接进入，进 `active_task`：

| flow_id | 干什么 |
|---|---|
| `onboarding` | 欢迎引导 |
| `order_status_query` | 查订单状态 |
| `logistics_tracking` | 查物流 |
| `refund_request` | 退款申请 |
| `similar_product_recommendation` | 相似商品推荐 |
| `human_handoff` | 转人工 |

特点：常有 `collect` 收槽、业务 `action_xxx`。

### system_flows：办事时系统怎么接话

代码内部挂上，用户不能 `start_flow("system_...")`，进 `active_system_task`：

| flow_id | 干什么 |
|---|---|
| `system_task_started` | 「好的，我们先处理某某」 |
| `system_task_resumed` | 「继续刚才的某某」 |
| `system_task_interrupted` | 「先把某某放一放」 |
| `system_task_canceled` | 「某某先取消」 |
| `system_collect_information` | 问槽位（请告诉我订单号） |
| `system_cannot_handle` | 搞不定时的兜底话术 |

特点：几乎只有 `action_response` + `listen` / `end`。

一句话：**user = 办什么事；system = 办事时系统怎么接话。**

---

## 怎么读 YAML（不要整文件扫）

用「一条用户路径」追，例如只追查订单：

1. 打开 `order_status_query`
2. 从 `start` 跟着 `next` 走
3. 遇到 `collect` → 看 `slot_name` + `response`
4. 遇到 `action` → 看 `action` 名，再去 `atguigu/task/action` 找实现
5. 槽没填时，对照 `system_collect_information`

一边读 YAML，一边对照 `atguigu/task/flow/FlowExecutor执行逻辑.md`，会快很多。

典型挂钩：

```
user_flows 里 collect order_number
  → 槽没值
  → 启动 system_collect_information
  → 问「请告诉我你的订单号」
  → listen 等用户
  → 填完后再继续 user flow 下一步
```

---

## 记住 4 种 step 就够

| type | 作用 |
|---|---|
| `start` | 入口，马上跳下一步 |
| `collect` | 收槽；没有就拉系统问询 |
| `action` | 说话或调业务（查订单等） |
| `end` | 结束当前系统/业务任务 |

`next` 三种边：

- **固定跳**：`next: lookup_order_status`
- **条件跳**：`if: ...` / `then: ...`
- **兜底**：`else: ...`

---

## YAML 和代码的对应关系

```
YAML step.type=collect  → CollectSlotStep → _run_collect_slots_step
YAML step.type=action   → ActionFlowStep  → action_runner.run(...)
YAML action: action_xxx → task/action 里同名 Action 类
```

加载入口：`FlowLoader` + `engine/builder.py` 扫 `flow_config/*.yml`。

---

## 改 YAML 的安全练法

1. 先只改文案：`response.text`、`action_response` 的 `text`
2. 再改顺序：调 `next`，看执行路径变没变
3. 最后才加新 step / 新 flow
4. 每改一次就跑一轮对话验证（比空想有效）

实用习惯：

- 给每个 flow 画 5 个框的小路径：`start → … → end`
- 新 flow 先抄一个最像的（如 `order_status_query`），再改
- 业务逻辑尽量放 action 代码；YAML 只描述「顺序和话术」
- 不确定时看当前 `flow_id` + `step_id`，确认卡在哪一步
