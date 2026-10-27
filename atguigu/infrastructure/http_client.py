
"""
未来调用中台接口查询订单数据、商品数据...

"""

import asyncio
from httpx import AsyncClient

from atguigu.config.config import settings

http_client: AsyncClient | None = None  # 全局变量


def init_http_client():
    global http_client
    # trust_env=False：不走系统代理。浏览器会绕过 *.local，httpx 默认不会，
    # 经 127.0.0.1:12450 访问 app.web.orb.local 会拿到空 body 的 502。
    http_client = AsyncClient(timeout=10.0, trust_env=False)


async def close_http_client():
    await http_client.aclose()


async def main():
    # 1. 初始化http_client
    init_http_client()

    url = f"{settings.commerce_api_base_url}/orders/B20260409001"
    response = await http_client.get(url=url)
    print(response.json())


if __name__ == '__main__':
    asyncio.run(main())
