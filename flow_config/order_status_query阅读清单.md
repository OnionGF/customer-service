# 阅读模板：`order_status_query` YAML 逐步对照代码

以后读别的 flow，按这份清单把「YAML 一步」换成「代码落点」即可。

用户一句话示例：**「帮我查一下订单状态」**

---

## 0. 进门：消息怎么变成这个 flow

| 步骤 | 看哪里 | 你会看到什么 |
|---|---|---|
| 文本消息入口 | `engine/dialogue_engine.py` → `_handle_text_msg` | LLM 出 TurnPlan |
| 规划 | `plan/planner.py` | `available_flows` 里有 `order_status_query` |
| 校验 | `plan/turn_plan_validator.py` | 合法才进 task 轨道 |
| 开流程 | `task/command/processor.py` → `_handle_start_flow` | `start_task(flow_id=order_status_query)`，常再挂 `system_task_started` |
| 真正推进 | `task/flow/executor.py` → `run_task` | 外层循环执行 action，直到 `action_listen` |

记住：YAML 不会自己跑；是 `FlowExecutor` 按 `state` 里的 `flow_id` / `step_id` 去查 YAML 加载后的对象。

---

## 1. YAML 路径一览

```
start
  → ask_order_number   (collect: order_number)
  → lookup_order_status (action_lookup_order_status)
  → show_order_status   (action_response)
  → end
```

对应文件：`flow_config/user_flows.yml` → `flows.order_status_query`

---

## 2. 逐步对照

### Step 1：`start`

```yaml
- id: start
  type: start
  next: ask_order_number
```

| 对照 | 位置 |
|---|---|
| 类 | `StartFlowStep`（`task/flow/steps.py`） |
| 执行 | `FlowExecutor._run_start_step` |
| 行为 | 只把 `step_id` 改成 `ask_order_number`，返回 `None`（继续内层推进） |

---

### Step 2：`ask_order_number`（collect）

```yaml
- id: ask_order_number
  type: collect
  slot_name: order_number
  response:
    text: "请告诉我你的订单号。"
  next: lookup_order_status
```

| 对照 | 位置 |
|---|---|
| 类 | `CollectSlotStep` |
| 执行 | `FlowExecutor._run_collect_slots_step` |
| 自动填槽 | `_try_to_fill_collect_slot_focused_object`（点过订单卡片时） |

**槽还没有值时：**

1. `start_system_task(CollectedSystemContext(...))`  
   - `flow_id = system_collect_information`  
   - `response = {"text": "请告诉我你的订单号。"}`（来自上面 YAML）
2. 返回 `None` → 内层继续推
3. 系统流程优先：`system_flows.yml` → `system_collect_information`  
   - `ask`：`action_response` + `args: context.response`  
   - `listen`：`action_listen` → **外层 break，等用户**

**用户下轮说出订单号后：**

- Planner / command 填 `order_number` 槽（或对象消息 `SetSlotsCommand`）
- 再进 Collect：槽已有值 → `_advance_next_step` → `lookup_order_status`

**槽已有值且无 validate：** 直接跳下一步，不播问询。

---

### Step 3：`lookup_order_status`（业务 action）

```yaml
- id: lookup_order_status
  type: action
  action: action_lookup_order_status
  next: show_order_status
```

| 对照 | 位置 |
|---|---|
| 类 | `ActionFlowStep` |
| 执行 | `_run_action_step` → 先跳到 `show_order_status`，再返回 `ActionCall` |
| 实现类 | `task/action/customer/lookup_order_status.py` → `LookUpOrderStatusAction` |
| 注册 | `task/action/builder.py` |

行为：

1. 从 `state.active_task.slots["order_number"]` 取值
2. `fetch_order(...)` 调电商接口
3. `ActionResult.slot_updates` 写入 `order_status`、`order_summary`
4. 外层 `run_task`：`state.set_slots(...)` 写回

这一步通常**不直接对用户说话**，只填结果槽。

---

### Step 4：`show_order_status`（说话 action）

```yaml
- id: show_order_status
  type: action
  action: action_response
  args:
    text: "订单{{ slots.order_number }}当前状态是：{{ slots.order_status }}。{{ slots.order_summary }}"
  next: end
```

| 对照 | 位置 |
|---|---|
| 执行 | 同样走 `_run_action_step` |
| 实现 | `task/action/.../response.py`（`action_response`） |
| 模板变量 | `slots.*` 来自当前业务任务槽位 |

先跳到 `end`，再执行 response，把渲染后的文本放进 `BotMessage`。

---

### Step 5：`end`

```yaml
- id: end
  type: end
  next: []
```

| 对照 | 位置 |
|---|---|
| 类 | `EndFlowStep` |
| 执行 | `_run_end_step` |
| 行为 | 清掉当前业务任务（或系统任务）上下文，返回 `None` |
| 随后 | 没有 active task → `_advance_until_action` 返回 `action_listen` → 本轮结束 |

---

## 3. 一张总表（可当别的 flow 的填空模板）

| YAML step id | type | 代码入口 | 副作用 |
|---|---|---|---|
| `start` | start | `_run_start_step` | 只改 `step_id` |
| `ask_order_number` | collect | `_run_collect_slots_step` | 可能挂 `system_collect_information` |
| （系统）`ask` | action | `action_response` + `context.response` | 问订单号 |
| （系统）`listen` | action | `action_listen` | **等用户** |
| `lookup_order_status` | action | `LookUpOrderStatusAction` | 写 `order_status` 等槽 |
| `show_order_status` | action | `action_response` | 对用户播结果 |
| `end` | end | `_run_end_step` | 清空任务 |

---

## 4. 读任意新 flow 时照抄这 5 问

1. **入口**：谁 `start_flow` 进来的？（LLM / 对象消息 / 系统触发）
2. **路径**：从 `start` 跟 `next` 画一条线到 `end`
3. **每个 collect**：槽名是什么？没值时系统问询文案在哪？
4. **每个 action**：`action:` 字符串对应哪个 Python 类？改槽还是说话？
5. **停在哪等用户**：哪里会出现 `action_listen`？

把上表的 step 行换成新 flow 的 step，就是下一份阅读清单。
