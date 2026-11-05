from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import yaml

from atguigu.task.flow.flows import FlowsList, FlowSlot, Flow
from atguigu.task.flow.steps import FlowStep, CollectSlotStep

YAML_PATH = Path(__file__).resolve().parents[3] / "flow_config" / "user_flows.yml"

"""
yaml（多个）--->dict---->数据模型

"""


class FlowLoader:
    """
    流程加载器（加载两个yaml文件）
    """
    def load(self, path: Path) -> FlowsList:
        # 1. 打开文件
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # 2. 加载slots部分
        slots: Dict[str, FlowSlot] = self._load_slots(data.get('slots', {}))

        # 3. 加载flows部分
        flows = self._load_flows(data.get('flows', {}), slots)

        return FlowsList(slots=slots, flows=flows)

    def _load_slots(self, yaml_slots_data: Dict[str, Any]) -> Dict[str, FlowSlot]:
        """
         {
         "order_number":FlowSlot(),
         "order_status":FlowSlot(),
         ...
         }
        :param yaml_slots_data:
        :return:
        """
        slots = {}
        for slot_name, slot_dict in yaml_slots_data.items():
            slots[slot_name] = FlowSlot(name=slot_name, **slot_dict)

        return slots

    def _load_flows(self, yaml_flows_data: Dict[str, Any], slots_definition: Dict[str, FlowSlot]) -> List[Flow]:
        """
        加载流程
        :param yaml_flows_data:
        :param slots_definition:
        :return:
        """
        flows: List[Flow] = []
        for flow_id, flow_dict in yaml_flows_data.items():
            steps = [FlowStep.from_dict(step) for step in flow_dict.get('steps', [])]
            flow_slots: list[FlowSlot] = []
            for step in steps:
                if isinstance(step, CollectSlotStep):
                    flow_slots.append(slots_definition[step.slot_name])
            flows.append(
                Flow(
                    id=flow_id,
                    description=flow_dict.get('description', ''),
                    name=flow_dict.get('name'),
                    steps=steps,
                    slots=flow_slots
                )
            )

        return flows


    def load_many(self, paths: List[Path]) -> FlowsList:
        flows: List[Flow] = []
        slots: Dict[str, FlowSlot] = {}  # set()集合找重复的 set1("order_name","11111")  set2("order_name"，“2222”)----找交集
        for path in paths:
            # 1. 加载单个yaml文件的flow_list
            single_flows_list = self.load(path)
            # 2. 获取单个yaml的flows
            flows.extend(single_flows_list.flows)
            # 更新slots 合并slots
            slots.update(single_flows_list.slots)
        return FlowsList(flows=flows, slots=slots)

if __name__ == '__main__':
    base_path = Path(__file__).parents[3]
    flow_paths = sorted((base_path / 'flow_config').glob('*.yml'))
    loader = FlowLoader()
    flows_list = loader.load_many(flow_paths)
    print(flows_list)
