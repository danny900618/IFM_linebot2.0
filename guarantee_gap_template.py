# -*- coding: utf8 -*-
"""保障缺口計算 模板"""

base_template = {
    "type": "bubble",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "保障缺口分析",
                "weight": "bold",
                "size": "xl"
            }
        ],
        "alignItems": "center"
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "spacing": "md",
        "paddingStart": "md",
        "paddingEnd": "md"
    }
}


title_module = {
    "type": "box",
    "layout": "vertical",
    "contents": [
        {
            "type": "image",
            "url": "https://imgur.com/NQtG7fx.png",
            "align": "center",
            "size": "full",
            "gravity": "center"
        },
        {
            "type": "text",
            "text": " ",
            "size": "lg",
            "wrap": True
        }
    ],
    "alignItems": "center",
    "paddingStart": "xxl",
    "paddingEnd": "xxl"
}


options_module = {
    "type": "button",
    "action": {
        "type": "postback",
        "label": " ",
        "data": "hello",
        "displayText": "displayTexttext"
    },
    "height": "sm",
    "style": "primary",
    "color": "#4D4DFF",
    "adjustMode": "shrink-to-fit"
}


calculate_result_module = {
    "type": "box",
    "layout": "horizontal",
    "contents": [
            {
                "type": "text",
                "text": " ",
                "flex": 1,
                "size": "md",
                "weight": "bold",
                "align": "center",
                "gravity": "center",
                "adjustMode": "shrink-to-fit"
            }, {
                "type": "text",
                "text": " ",
                "flex": 4,
                "size": "md",
                "weight": "bold",
                "align": "center",
                "gravity": "center",
                "adjustMode": "shrink-to-fit"
            }, {
                "type": "text",
                "text": " ",
                "flex": 2,
                "size": "md",
                "weight": "bold",
                "gravity": "center",
                "align": "center",
                "adjustMode": "shrink-to-fit"
            }, {
                "type": "text",
                "text": "萬",
                "flex": 1,
                "size": "md",
                "weight": "bold",
                "align": "center",
                "gravity": "center",
                "adjustMode": "shrink-to-fit"
            }
    ],
    "paddingAll": "sm"
}


insurance_advice_module = {
    "type": "box",
    "layout": "horizontal",
    "contents": [
        {
            "type": "text",
            "text": " ",
            "size": "md",
            "flex": 4,
            "align": "start",
            "gravity": "center",
            "adjustMode": "shrink-to-fit",
            "weight": "bold"
        },
        {
            "type": "text",
            "text": " ",
            "size": "md",
            "flex": 5,
            "align": "end",
            "gravity": "center",
            "adjustMode": "shrink-to-fit",
            "weight": "bold"
        },
        {
            "type": "text",
            "text": " ",
            "size": "md",
            "flex": 3,
            "align": "center",
            "gravity": "center",
            "adjustMode": "shrink-to-fit",
            "weight": "bold"
        }
    ],
    "paddingAll": "sm"
}


totle_result_module = [
    {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "類型：",
                "weight": "bold",
                "gravity": "center",
                "size": "lg",
                "wrap": True
            },
            {
                "type": "text",
                "text": " ",
                "size": "lg",
                "weight": "bold",
                "wrap": True
            }
        ]
    },
    {
        "type": "separator",
        "color": "#000000",
        "margin": "md"
    },
    {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "描述：",
                "weight": "bold",
                "gravity": "center",
                "size": "lg",
                "flex": 1,
                "wrap": True
            },
            {
                "type": "text",
                "text": " ",
                "size": "lg",
                "weight": "bold",
                "flex": 3,
                "wrap": True
            }
        ],
        "margin": "md"
    },
    {
        "type": "separator",
        "color": "#000000",
        "margin": "md"
    },
    {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "建議保險項目：",
                "weight": "bold",
                "gravity": "center",
                "size": "lg",
                "flex": 1,
                "wrap": True
            },
            {
                "type": "text",
                "text": " ",
                "size": "lg",
                "weight": "bold",
                "flex": 3,
                "wrap": True
            }
        ],
        "margin": "md"
    },
    {
        "type": "separator",
        "color": "#000000",
        "margin": "md"
    },
    {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "保費：",
                "weight": "bold",
                "gravity": "center",
                "size": "lg",
                "flex": 1,
                "wrap": True
            },
            {
                "type": "text",
                "text": " ",
                "size": "lg",
                "weight": "bold",
                "flex": 3,
                "wrap": True
            }
        ],
        "margin": "md"
    },
    {
        "type": "separator",
        "color": "#000000",
        "margin": "md"
    },
    {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "說明：",
                "weight": "bold",
                "gravity": "center",
                "size": "lg",
                "flex": 1,
                "wrap": True
            }
        ],
        "margin": "md"
    }
]


insurance_description_module = {
    "type": "box",
    "layout": "horizontal",
    "contents": [
        {
            "type": "text",
            "text": "定期壽險",
            "weight": "bold",
            "gravity": "center",
            "size": "lg",
            "flex": 1,
            "wrap": True
        },
        {
            "type": "text",
            "text": "保障續約的壽險主要幫助家人，如果還沒有家庭要撫養，可以先不買。",
            "weight": "bold",
            "gravity": "center",
            "size": "lg",
            "flex": 3,
            "wrap": True
        }
    ],
    "backgroundColor": "#FFFFFF"
}


quickreply = {
    "items": [
        {
            "action": {
                "label": "功能列表",
                "text": "功能列表",
                "type": "message"
            },
            "type": "action"
        },
        {
            "action": {
                "label": "適合性分析",
                "text": "適合性分析",
                "type": "message"
            },
            "type": "action"
        },
        {
            "action": {
                "label": "汽車保險規劃",
                "text": "汽車保險規劃",
                "type": "message"
            },
            "type": "action"
        },
        {
            "action": {
                "label": "人生保險規劃1",
                "text": "人生保險規劃1",
                "type": "message"
            },
            "type": "action"
        },
        {
            "action": {
                "label": "人生保險規劃2",
                "text": "人生保險規劃2",
                "type": "message"
            },
            "type": "action"
        },
        {
            "action": {
                "label": "保障缺口分析",
                "text": "保障缺口分析",
                "type": "message"
            },
            "type": "action"
        },
        {
            "action": {
                "label": "退休財務規劃",
                "text": "退休財務規劃",
                "type": "message"
            },
            "type": "action"
        }
    ]
}
