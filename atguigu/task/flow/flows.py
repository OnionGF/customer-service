from dataclasses import dataclass, field
from typing import List, Dict

from atguigu.task.flow.steps import FlowStep, StartedFlowStep


@dataclass(slots=True)
class FlowSolt:
    name: str           # 槽位的名字
    type: str = "any"   # 槽位的类型
    label: str = ""     # 槽位的标签
    description: str = ""   # 槽位的描述

@dataclass(slots=True)
class Flow:
    id: str     # 流程的ID
    description: str
    steps: List[FlowStep] = field(default_factory=list)     # 步骤
    slots: List[FlowSolt] = field(default_factory=list)     # 槽位
    name: str | None = None         # 流程名字

    def start_step(self):
        """
        返回流程的开始步骤
        :return:
        """
        for step in self.steps:
            if isinstance(step, StartedFlowStep):
                return step
        return None

    def get_step_by_id(self, step_id: str) -> FlowStep | None:

        for step in self.steps:
            if step.id == step_id:
                return step
        return None

@dataclass(slots=True)
class FlowList:
    """
    存放两个yaml文件的流程（业务流程以及系统流程）
    """
    flows: List[Flow] = field(default_factory=list)
    slots: Dict[str, FlowSolt] = field(default_factory=dict)

    def get_flow_by_id(self, flow_id: str) -> Flow | None:
        for flow in self.flows:
            if flow.id == flow_id:
                return flow
        return None