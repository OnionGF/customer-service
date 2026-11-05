"""兼容参考项目的 import 路径：from atguigu.infrastructure import http"""

from atguigu.infrastructure.http_client import (
    http_client,
    init_http_client,
    close_http_client,
)

__all__ = ["http_client", "init_http_client", "close_http_client"]
