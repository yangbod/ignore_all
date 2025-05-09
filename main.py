import os
import json
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import At

@register("astrbot_plugin_ignore_at", "Cl_Fu", "", "1.0.0")
class IgnoreAtAllPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.ignore_all_at = True
        self.config_file = os.path.join(os.path.dirname(__file__), "ignore_at_config.json")
        self.load_config()

    def load_config(self):
        """加载上次的配置（如果有）"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.ignore_all_at = config.get("ignore_all_at", False)
                    logger.info(f"加载上次的设置：无视@功能 {'开启' if self.ignore_all_at else '关闭'}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"读取配置文件时发生错误: {e}")

    def save_config(self):
        """保存当前配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({"ignore_all_at": self.ignore_all_at}, f, ensure_ascii=False, indent=4)
                logger.info(f"保存当前设置：无视@功能 {'开启' if self.ignore_all_at else '关闭'}")
        except IOError as e:
            logger.error(f"保存配置文件时发生错误: {e}")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def ignore_at_all(self, event: AstrMessageEvent):
        logger.info(f"raw_message type: {type(event.message_obj.raw_message)}")
        logger.info(f"raw_message content: {event.message_obj.raw_message}")
        raw_message = event.message_obj.raw_message

# 如果 raw_message 是 tuple，取出其中的字典部分
        if isinstance(raw_message, tuple) and len(raw_message) > 2 and isinstance(raw_message[2], dict):
            raw_message = raw_message[2]  # 取第三个元素（字典）

        # 确保 raw_message 是字典
        if isinstance(raw_message, dict):
            message_content = raw_message.get("Content", {}).get("string", "")
        else:
            message_content = ""
            

        if "@所有人" in message_content:
            event.stop_event()
            return
           

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ignore_open")
    async def ignore_at_on(self, event: AstrMessageEvent):
        """开启无视@功能"""
        self.ignore_all_at = True
        self.save_config()  # 保存配置
        yield event.plain_result("无视@功能已开启。")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("ignore_on")
    async def ignore_at_off(self, event: AstrMessageEvent):
        """关闭无视@功能"""
        self.ignore_all_at = False
        self.save_config()  # 保存配置
        yield event.plain_result("无视@功能已关闭。")
