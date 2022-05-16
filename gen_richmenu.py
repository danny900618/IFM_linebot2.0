import configparser

from linebot import LineBotApi
from linebot.models.rich_menu import RichMenu, RichMenuSize, RichMenuBounds, RichMenuArea
from linebot.models.actions import MessageAction, PostbackAction, DatetimePickerAction, URIAction


# rich_menu_alias = "my-richmenu"
rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="my-richmenu",
    chat_bar_text="選單",
    areas=[
        # 左上
        RichMenuArea(
            RichMenuBounds(x=0, y=0, width=1250, height=843),
            MessageAction(label="功能列表", text="功能列表")
        ),
        # 右上
        RichMenuArea(
            RichMenuBounds(x=1251, y=0, width=1250, height=843),
            MessageAction(label="使用說明", text="使用說明")
        )
    ]
)

# channel_access_token = "zjGimgRw+bw/oVn/STJ3j+WyJcoA6NZJvUklw/U8QHPjpdgqFghXUgCq6+hsrGcGCDNrbCt+MLxjVwvnnsbhOfP3iGXbMaBx9zBvIz1Bn3sNbwWlanJ3kkBxALjNI7GDabGEJiEbqDbngi3Gl1y/TwdB04t89/1O/w1cDnyilFU="

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
    
    richmenu_id = line_bot_api.create_rich_menu(rich_menu)
    with open("image.png", "rb") as fp:
        line_bot_api.set_rich_menu_image(
            richmenu_id, content_type="image/png", content=fp)
    # line_bot_api.create_rich_menu_alias(
    #     RichMenuAlias(rich_menu_alias_1, richmenu_id))
    line_bot_api.set_default_rich_menu(richmenu_id)
    
    r_list = line_bot_api.get_rich_menu_list()
    print("-"*20)
    for r in r_list:
        print(r)
    print("-"*20)
    
    # a_list = line_bot_api.get_rich_menu_alias_list()
    # print(a_list)
