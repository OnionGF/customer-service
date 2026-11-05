from dataclasses import dataclass


@dataclass(slots=True)
class FlowStepLink:
    """
    模版边（基类）
    """
    target: str  # 下一条步骤（节点）的ID


# 无条件跳转
@dataclass(slots=True)
class StaticLink(FlowStepLink):
    """
    对应的是next:"ask_order_number"
    """
    pass

# 有条件跳转 condition
@dataclass(slots=True)
class ConditionalLink(FlowStepLink):
    """
    对应的是next:"[{"if":"xxxxxx","then":"step_id"}]"
    """
    condition: str  # 接收if 中的xxxxx

# 条件不满足 跳转
@dataclass(slots=True)
class FallbackLink(FlowStepLink):
    """"
      对应的是next:"[{"else":"step_id"}]"
    """
    pass
