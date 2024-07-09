import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

# 感谢pearAPI
GOLD_PRICE_URL = "https://api.pearktrue.cn/api/goldprice/"

@plugins.register(name="gold_price_query",
                  desc="查询当前金价及相关信息",
                  version="1.0",
                  author="azad",
                  desire_priority=100)
class gold_price_query(Plugin):

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = "发送【金价】查询当前金价及相关信息"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        content = e_context["context"].content.strip()

        # 检查是否是金价查询的指令
        if content == "金价":
            reply = Reply()
            result = self.get_gold_price()
            if result:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "金价查询失败，请稍后再试。"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def get_gold_price(self):
        try:
            response = requests.get(url=GOLD_PRICE_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    return self.format_gold_price_data(data)
                else:
                    logger.error(f"API返回错误信息: {data.get('msg')}")
                    return None
            else:
                logger.error(f"API返回状态码异常: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"API请求异常：{e}")
            return None

    def format_gold_price_data(self, data):
        # 格式化金价数据，这里只返回部分信息作为示例
        formatted_data = f"今日金价信息（{data['time']}）:\n"
        for item in data['data']:
            formatted_data += f"{item['title']} - 价格: {item['price']}, 涨跌幅: {item['changepercent']}, 开盘价: {item['openingprice']}, 昨收价: {item['lastclosingprice']}\n"
        return formatted_data
