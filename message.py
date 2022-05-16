# -*- coding: utf8 -*-
import configparser
from abc import ABC, abstractmethod
from re import A
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, TextSendMessage, PostbackAction, MessageAction, URIAction, CarouselColumn, CarouselTemplate, PostbackTemplateAction, FlexSendMessage, ImageSendMessage
from pymongo import MongoClient
from pymongo import message
from pymongo.message import query

# config 環境設定解析
config = configparser.ConfigParser()
config.read("config.ini")

# mongoDB atlas 連線
myMongoClient = MongoClient(config['connect_config']['Mongodb_atlas_URL'])

# 保金系資料庫
myMongoDb2 = myMongoClient["insurance-data"]
dbUserRequest = myMongoDb2['user-request']
dbQuestion = myMongoDb2['qusetion-database']
dbInsurance = myMongoDb2['insurance-advice']
# 訊息抽象類別


class Message(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def content(self):
        pass

# 適合性分析


class Suitability_analysis():
    def __init__(self, user_id):
        self.user_id = user_id

    def content(self):
        def func_answer_append(user_id):
            # 獲取進行分析的使用者資料
            check_data = {"user_id": user_id}
            user_data = dbUserRequest.find_one(check_data)
            # 獲取當前題目
            check_data = {
                "question_number": user_data["question_number"], "question_group": "Suitability_analysis"}
            qusetion = dbQuestion.find_one(check_data)
            # 初始化答案清單, 答案回傳清單
            answer_list = []
            answer_return_list = []
            # 動態添加答案字串
            for answer_conut in range(0, int(qusetion["answer_sum"])):
                if answer_conut == 0:
                    # 答案清單添加答案字串
                    answer_list.append(qusetion["answer1"])
                elif answer_conut == 1:
                    answer_list.append(qusetion["answer2"])
                elif answer_conut == 2:
                    answer_list.append(qusetion["answer3"])
                elif answer_conut == 3:
                    answer_list.append(qusetion["answer4"])
                elif answer_conut == 4:
                    answer_list.append(qusetion["answer5"])
                # 設定按鈕回傳文字
                answer_text = "ans:" + \
                    str(user_data["question_number"]) + \
                    "-" + str(answer_conut + 1)
                # 答案回傳清單添加回傳文字
                answer_return_list.append(answer_text)
            # 如果當前題目是複選題
            if qusetion["question_type"] == "Suitability_analysis_multiple":
                # 新增確定按鈕
                check_button = "[確定]"
                answer_list.append(check_button)
                answer_return_list.append(
                    "ans:" + str(user_data["question_number"]) + "-" + check_button)
            # 回傳題目字串, 答案清單, 答案回傳清單
            return qusetion["description"], answer_list, answer_return_list
        # 初始化按鈕清單
        data_list = []
        # 進入函式處理資料, 取得題目字串, 答案清單, 答案回傳清單
        description, answer_list, answer_return_list = func_answer_append(
            self.user_id)
        # 迴圈添加答案進入按鈕清單
        for label_text, return_text in zip(answer_list, answer_return_list):
            data_bubble = {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": label_text,
                    "text": return_text
                },
                "style": "primary",
                "color": "#DCC639",
                "adjustMode": "shrink-to-fit"
            }
            data_list.append(data_bubble)
        flex_message = FlexSendMessage(
            alt_text='適合性分析',
            contents={
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "適合性分析",
                            "weight": "bold",
                            "size": "xl"
                        }
                    ],
                    "alignItems": "center"
                },
                "hero": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://imgur.com/xcfPFuT.png",
                            "align": "center",
                            "size": "full",
                            "gravity": "center"
                        },
                        {
                            "type": "text",
                            "text": description,
                            "size": "lg",
                            "wrap": True
                        }
                    ],
                    "alignItems": "center",
                    "paddingStart": "xxl",
                    "paddingEnd": "xxl"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": data_list,
                    "spacing": "xs"
                }
            }
        )
        return flex_message

# 汽車保險規劃


class Car_insurance_planning():
    def __init__(self, user_id):
        self.user_id = user_id

    def content(self):
        def func_answer_append(user_id):
            # 獲取進行規劃的使用者資料
            check_data = {"user_id": user_id}
            user_data = dbUserRequest.find_one(check_data)
            # 獲取當前題目
            check_data = {
                "question_number": user_data["question_number"], "question_group": "Car_insurance_planning"}
            qusetion = dbQuestion.find_one(check_data)
            # 初始化答案清單, 答案回傳清單
            answer_list = []
            answer_return_list = []
            # 動態添加答案字串
            for answer_conut in range(0, int(qusetion["answer_sum"])):
                if answer_conut == 0:
                    # 答案清單添加答案字串
                    answer_list.append(qusetion["answerA"])
                    # 回傳文字尾端字母
                    letter = "A"
                elif answer_conut == 1:
                    answer_list.append(qusetion["answerB"])
                    letter = "B"
                elif answer_conut == 2:
                    answer_list.append(qusetion["answerC"])
                    letter = "C"
                elif answer_conut == 3:
                    answer_list.append(qusetion["answerD"])
                    letter = "D"
                elif answer_conut == 4:
                    answer_list.append(qusetion["answerE"])
                    letter = "E"
                # 設定按鈕回傳文字
                answer_text = "ans:" + \
                    str(user_data["question_number"]) + "-" + letter
                # 答案回傳清單添加回傳文字
                answer_return_list.append(answer_text)
            # 回傳題目字串, 答案清單, 答案回傳清單
            return qusetion["description"], answer_list, answer_return_list
        # 初始化按鈕清單
        data_list = []
        # 進入函式處理資料, 取得題目字串, 答案清單, 答案回傳清單
        description, answer_list, answer_return_list = func_answer_append(
            self.user_id)
        # 迴圈添加答案進入按鈕清單
        for label_text, return_text in zip(answer_list, answer_return_list):
            data_bubble = {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": label_text,
                    "text": return_text
                },
                "style": "primary",
                "color": "#D34149",
                "adjustMode": "shrink-to-fit"
            }
            data_list.append(data_bubble)
        flex_message = FlexSendMessage(
            alt_text='汽車保險規劃',
            contents={
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "汽車保險規劃",
                            "weight": "bold",
                            "size": "xl"
                        }
                    ],
                    "alignItems": "center"
                },
                "hero": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://imgur.com/QxcwBuz.png",
                            "align": "center",
                            "size": "full",
                            "gravity": "center"
                        },
                        {
                            "type": "text",
                            "text": description,
                            "size": "lg",
                            "wrap": True
                        }
                    ],
                    "alignItems": "center",
                    "paddingStart": "xxl",
                    "paddingEnd": "xxl"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": data_list,
                    "spacing": "xs"
                }
            }
        )
        return flex_message

 # 結果模板


class Result_template():
    def __init__(self, myReply):
        self.myReply = myReply

    def content(self, title, image_url):
        # 分割字串成列表
        reply_list = self.myReply.split("\n")
        # 初始化回傳列表
        data_list = []
        button_list = []
        # 迴圈添加答案進入按鈕清單
        for reply_text in reply_list:
            # 略過空字串
            if reply_text == "":
                continue
            if "其他保險建議" in reply_text:
                # 分割保險細項
                insurance_list = reply_text.split("：")[1]
                insurance_list = insurance_list.split(",")
                # 開頭文字
                data_bubble = {
                    "type": "text",
                    "text": reply_text.split("：")[0] + "：",
                    "wrap": True
                }
                data_list.append(data_bubble)
                # 迴圈添加險種按鈕
                for insurance_text in insurance_list:
                    if "加總分數" in self.myReply:
                        button_bubble = {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": insurance_text,
                                "text": "適合性ex:" + insurance_text
                            },
                            "color": "#0367D3",
                            "adjustMode": "shrink-to-fit"
                        }
                    else:
                        button_bubble = {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": insurance_text,
                                "text": "車險ex:" + insurance_text
                            },
                            "color": "#0367D3",
                            "adjustMode": "shrink-to-fit"
                        }
                    button_list.append(button_bubble)
                # 險種按鈕顯示
                try:
                    # 如果列表中可取出兩筆資料, 一列添加兩個按鈕
                    for i in range(0, len(button_list), 2):
                        data_bubble = {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [button_list[i], button_list[i+1]],
                            "backgroundColor": "#ffffff"
                        }
                        data_list.append(data_bubble)
                except:
                    # 如果列表中不可取出兩筆資料, 一列添加一個按鈕
                    data_bubble = {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [button_list[-1]],
                        "backgroundColor": "#ffffff"
                    }
                    data_list.append(data_bubble)
            elif "網址" in reply_text:
                data_bubble = {
                    "type": "button",
                    "style": "link",
                    "action": {
                        "type": "uri",
                        "label": "參考網址",
                        "uri": str(reply_text.split("：")[1])
                    }
                }
                data_list.append(data_bubble)
            else:
                data_bubble = {
                    "type": "text",
                    "text": reply_text,
                    "wrap": True
                }
                data_list.append(data_bubble)
        flex_message = FlexSendMessage(
            alt_text='分析結果',
            contents={
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "xl"
                        }
                    ],
                    "alignItems": "center"
                },
                "hero": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": image_url,
                            "align": "center",
                            "size": "full",
                            "gravity": "center"
                        }
                    ],
                    "alignItems": "center",
                    "paddingStart": "xxl",
                    "paddingEnd": "xxl"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": data_list,
                    "spacing": "xs"
                }
            }
        )
        return flex_message

# 人生保險規劃(正式)


class Life_stage1():

    def __init__(self, user_id):
        self.user_id = user_id

    def content(self):
        def func_answer_append(user_id):
            # 獲取進行規劃的使用者資料
            check_data = {"user_id": user_id}
            user_data = dbUserRequest.find_one(check_data)
            # 獲取當前題目
            check_data = {
                "question_number": user_data["question_number"], "question_group": "Life_stage1"}
            qusetion = dbQuestion.find_one(check_data)
            # 初始化答案清單, 答案回傳清單
            answer_list = []
            answer_return_list = []
            # 動態添加答案字串
            for answer_conut in range(0, int(qusetion["answer_sum"])):
                if answer_conut == 0:
                    # 答案清單添加答案字串
                    answer_list.append(qusetion["answer1"])
                elif answer_conut == 1:
                    answer_list.append(qusetion["answer2"])
                elif answer_conut == 2:
                    answer_list.append(qusetion["answer3"])
                elif answer_conut == 3:
                    answer_list.append(qusetion["answer4"])
                elif answer_conut == 4:
                    answer_list.append(qusetion["answer5"])
                elif answer_conut == 5:
                    answer_list.append(qusetion["answer6"])
                # 設定按鈕回傳文字
                answer_text = "ans:" + \
                    str(user_data["question_number"]) + \
                    "-" + str(answer_conut + 1)
                # 答案回傳清單添加回傳文字
                answer_return_list.append(answer_text)
            # 如果當前題目是複選題
            if qusetion["question_type"] == "Life_stage1_multiple":
                # 新增確定按鈕
                check_button = "[確定]"
                answer_list.append(check_button)
                answer_return_list.append(
                    "ans:" + str(user_data["question_number"]) + "-" + check_button)
            # 回傳題目字串, 答案清單, 答案回傳清單
            return qusetion["description"], answer_list, answer_return_list
        # 初始化按鈕清單
        data_list = []
        # 進入函式處理資料, 取得題目字串, 答案清單, 答案回傳清單
        description, answer_list, answer_return_list = func_answer_append(
            self.user_id)
        # 迴圈添加答案進入按鈕清單
        for label_text, return_text in zip(answer_list, answer_return_list):
            data_bubble = {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": label_text,
                    "text": return_text
                },
                "style": "primary",
                "color": "#81C25E",
                "adjustMode": "shrink-to-fit"
            }
            data_list.append(data_bubble)
        flex_message = FlexSendMessage(
            alt_text='人生保險規劃',
            contents={
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "人生保險規劃",
                            "weight": "bold",
                            "size": "xl"
                        }
                    ],
                    "alignItems": "center"
                },
                "hero": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://imgur.com/FUwl0XE.png",
                            "align": "center",
                            "size": "full",
                            "gravity": "center"
                        },
                        {
                            "type": "text",
                            "text": description,
                            "size": "lg",
                            "wrap": True
                        }
                    ],
                    "alignItems": "center",
                    "paddingStart": "xxl",
                    "paddingEnd": "xxl"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": data_list,
                    "spacing": "xs"
                }
            }
        )
        return flex_message


class Life_stage1_result():
    @ staticmethod
    def record(check_data, event):
        user_data = dbUserRequest.find(check_data)
        if user_data.count() != 0:
            # 回傳分析結果
            answer_record_life_stage_list = user_data[0]["answer_record_life_stage"].split(
                "-")
            # 獲取投資類型對應的投資建議
            check_data = {
                "life_stage1_type": user_data[0]["life_stage1_type"]}
            # 回傳資料格式
            # myReply = "上次人生保險規劃結果：\n"
            myReply = "人生階段：" + \
                user_data[0]["life_stage1_type"] + "\n"
            myReply += "加總分數：" + user_data[0]["score"] + "\n"
            myReply += "選項紀錄：" + "\n"
            for i in range(len(answer_record_life_stage_list)):
                if (i > 0):
                    check_data = {"question_number": str(i),
                                  "question_group": "Life_stage1"}
                    question = dbQuestion.find_one(check_data)
                    myReply += answer_record_life_stage_list[i] + "\n"
                    myReply += "題目:" + question['description'] + "\n"
                    myReply += "選項:"
                    if (question['question_type'] == "Life_stage1_multiple"):
                        if answer_record_life_stage_list[i].split(":")[1] == "":
                            myReply += "無選擇"
                        for j in range(len(answer_record_life_stage_list[i].split(":")[1])):
                            multiple_answer = ",".join(
                                answer_record_life_stage_list[i].split(":")[1])  # 1,4
                            multiple_answer = multiple_answer.split(
                                ",")
                            answer = "answer"+multiple_answer[j]
                            myReply += question[answer]+" "
                        myReply += "\n"
                    else:
                        answer = "answer" + \
                            str(answer_record_life_stage_list[i].split(
                                ":")[1])
                        myReply += question[answer] + "\n"
            check_data = {"user_id": event.source.user_id}
            check_options = dbUserRequest.find_one(check_data)
            if check_options["gender"] == "1":
                sex = "男"
            else:
                sex = "女"
            check_data = {"type_name": user_data[0]["life_stage1_type"],
                          "insurance_group": "life_stage1_result", "gender": sex}
            question = dbInsurance.find_one(check_data)
            myReply += question["guarantee_direction"] + "\n"

        else:
            myReply = "尚未進行適合性分析"
        return myReply

    @ staticmethod
    def result_button(check_data, event):
        user_data = dbUserRequest.find(check_data)
        check_data = {"user_id": event.source.user_id}
        check_options = dbUserRequest.find_one(check_data)
        if check_options["gender"] == "1":
            sex = "男"
        else:
            sex = "女"
        check_data = {"type_name": user_data[0]["life_stage1_type"],
                      "insurance_group": "life_stage1_result", "gender": sex}
        question = dbInsurance.find_one(check_data)
        advice = question["insurance_list"].split(",")  # 險種
        data_list = []
        for i in range(len(advice)):
            contents = {
                "type": "button",
                "style": "link",
                "action": {
                        "type": "message",
                        "label": advice[i],
                        "text":  advice[i]
                },
                "height": "sm",
                "style": "primary",
                "color": "#81C25E" if event.message.text == "人生保險規劃紀錄" else "#674A8A"
            }
            data_list.append(dict(contents))

        link = {
            "type": "button",
            "style": "link",
            "action": {
                "type": "uri",
                "label": "網址",
                "uri": question["link_1"]
            },
            "height": "sm",
            "style": "primary",
            "color": "#81C25E" if event.message.text == "人生保險規劃紀錄" else "#674A8A"
        }
        data_list.append(dict(link))
        advice_button = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "人生保險規劃紀錄" if event.message.text == "人生保險規劃紀錄" else "人生保險規劃 退休規劃紀錄",
                        "weight": "bold",
                        "size": "xl"
                    }
                ],
                "alignItems": "center"
            },
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": "https://imgur.com/FUwl0XE.png" if event.message.text == "人生保險規劃紀錄" else "https://imgur.com/5zEa62b.png",
                        "align": "center",
                        "size": "full",
                        "gravity": "center"
                    },
                    {
                        "type": "text",
                        "text": "保險列表",
                        "size": "lg",
                        "wrap": True
                    }
                ],
                "alignItems": "center",
                "paddingStart": "xxl",
                "paddingEnd": "xxl"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": data_list
            }
        }
        return advice_button

    @ staticmethod
    def result_button2(check_data, event):
        user_data = dbUserRequest.find(check_data)
        check_data = {"user_id": event.source.user_id}
        check_options = dbUserRequest.find_one(check_data)

        check_data = {"type_name": user_data[0]["life_stage2_type"],
                      "insurance_group": "life_stage1_result", "gender": check_options["gender"]}
        question = dbInsurance.find_one(check_data)
        advice = question["insurance_list"].split(",")  # 險種
        data_list = []
        for i in range(len(advice)):
            contents = {
                "type": "button",
                "style": "link",
                "action": {
                    "type": "message",
                    "label": advice[i],
                    "text":  advice[i]
                },
                "height": "sm",
                "style": "primary",
                "color": "#81C25E" if event.message.text == "人生保險規劃紀錄" else "#674A8A"
            }
            data_list.append(dict(contents))

        link = {
            "type": "button",
            "style": "link",
            "action": {
                "type": "uri",
                "label": "網址",
                "uri": question["link_1"]
            },
            "height": "sm",
            "style": "primary",
            "color": "#81C25E" if event.message.text == "人生保險規劃紀錄" else "#674A8A"
        }
        data_list.append(dict(link))
        advice_button = {
            "type": "bubble",
            "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "人生保險規劃 退休規劃",
                            "weight": "bold",
                            "size": "xl"
                        }
                    ],
                "alignItems": "center"
            },
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                        {
                            "type": "image",
                            "url": "https://imgur.com/5zEa62b.png",
                            "align": "center",
                            "size": "full",
                            "gravity": "center"
                        },
                    {
                            "type": "text",
                            "text": "保險推薦",
                            "size": "lg",
                            "wrap": True
                    }
                ],
                "alignItems": "center",
                "paddingStart": "xxl",
                "paddingEnd": "xxl"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": data_list,
                "spacing": "md",
                "paddingStart": "md",
                "paddingEnd": "md"
            }
        }
        return advice_button

    @ staticmethod
    def first_time_reply(check_data, myReply):
        question = dbInsurance.find_one(check_data)
        advice = question["insurance_list"].split(",")  # 險種
        data_list = []
        for i in range(len(advice)):
            contents = {
                "type": "button",
                "style": "link",
                "action": {
                    "type": "message",
                    "label": advice[i],
                    "text":  advice[i]
                },
                "height": "sm",
                "style": "primary",
                "color": "#81C25E"
            }
            data_list.append(dict(contents))

        link = {
            "type": "button",
            "style": "link",
            "action": {
                "type": "uri",
                "label": "網址",
                "uri": question["link_1"]
            },
            "height": "sm",
            "style": "primary",
            "color": "#81C25E"
        }
        data_list.append(dict(link))
        advice_button = {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": data_list
        }

        first_Reply = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": myReply,
                        "wrap": True
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    advice_button
                ]
            }
        }
        return first_Reply

    @ staticmethod
    def insurance_1(user_id):  # 意外險
        question = dbUserRequest.find_one(user_id)
        if question["current_Q"] == "1":
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        else:
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage2_type"], "button_insurance": "1"})
        return advice["意外險"]

    @ staticmethod
    def insurance_2(user_id):  # 失能險
        question = dbUserRequest.find_one(user_id)
        if question["current_Q"] == "1":
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        else:
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage2_type"], "button_insurance": "1"})
        return advice["失能險"]

    @ staticmethod
    def insurance_3(user_id):  # 重大疾病險
        question = dbUserRequest.find_one(user_id)
        if question["current_Q"] == "1":
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        else:
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage2_type"], "button_insurance": "1"})
        return advice["重大疾病險"]

    @ staticmethod
    def insurance_4(user_id):  # 醫療險
        question = dbUserRequest.find_one(user_id)
        if question["life_stage1_type"] == "親親寶貝" or question["life_stage2_type"] == "親親寶貝":
            message = ImageSendMessage(
                original_content_url="https://i.imgur.com/Ioo0wm7.jpg",
                preview_image_url="https://i.imgur.com/99BQcEj.jpg"
            )
            return message
        advice = dbInsurance.find_one(
            {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        return advice["醫療險"]

    @ staticmethod
    def insurance_5(user_id):  # 壽險
        question = dbUserRequest.find_one(user_id)
        if question["current_Q"] == "1":
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        else:
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage2_type"], "button_insurance": "1"})
        return advice["壽險"]

    @ staticmethod
    def insurance_6(user_id):  # 癌症險
        question = dbUserRequest.find_one(user_id)
        if question["current_Q"] == "1":
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        else:
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage2_type"], "button_insurance": "1"})
        return advice["癌症險"]

    @ staticmethod
    def insurance_7(user_id):  # 終身定期
        question = dbUserRequest.find_one(user_id)
        if question["current_Q"] == "1":
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        else:
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage2_type"], "button_insurance": "1"})
        return advice["終身定期"]

    @ staticmethod
    def insurance_8(user_id):  # 婦嬰險
        question = dbUserRequest.find_one(user_id)
        if question["current_Q"] == "1":
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage1_type"], "button_insurance": "1"})
        else:
            advice = dbInsurance.find_one(
                {"type_name": question["life_stage2_type"], "button_insurance": "1"})
        return advice["婦嬰險"]

# 人生保險規劃2(測試_商院資料5)


class Life_stage2():
    def __init__(self, user_id):
        self.user_id = user_id

    def content(self):
        def func_answer_append(user_id):
            # 獲取進行規劃的使用者資料
            check_data = {"user_id": user_id}
            user_data = dbUserRequest.find_one(check_data)
            # 獲取當前題目
            check_data = {
                "question_number": user_data["question_number"], "question_group": "Life_stage2"}
            qusetion = dbQuestion.find_one(check_data)
            # 初始化答案清單, 答案回傳清單
            answer_list = []
            answer_return_list = []
            # 動態添加答案字串
            for answer_conut in range(0, int(qusetion["answer_sum"])):
                if answer_conut == 0:
                    # 答案清單添加答案字串
                    answer_list.append(qusetion["answer1"])
                elif answer_conut == 1:
                    answer_list.append(qusetion["answer2"])
                elif answer_conut == 2:
                    answer_list.append(qusetion["answer3"])
                elif answer_conut == 3:
                    answer_list.append(qusetion["answer4"])
                elif answer_conut == 4:
                    answer_list.append(qusetion["answer5"])
                elif answer_conut == 5:
                    answer_list.append(qusetion["answer6"])
                elif answer_conut == 6:
                    answer_list.append(qusetion["answer7"])
                elif answer_conut == 7:
                    answer_list.append(qusetion["answer8"])
                # 設定按鈕回傳文字
                answer_text = "ans:" + \
                    str(user_data["question_number"]) + \
                    "-" + str(answer_conut + 1)
                # 答案回傳清單添加回傳文字
                answer_return_list.append(answer_text)
            # 回傳題目字串, 答案清單, 答案回傳清單
            return qusetion["description"], answer_list, answer_return_list
        # 初始化按鈕清單
        data_list = []
        # 進入函式處理資料, 取得題目字串, 答案清單, 答案回傳清單
        description, answer_list, answer_return_list = func_answer_append(
            self.user_id)
        # 迴圈添加答案進入按鈕清單
        for label_text, return_text in zip(answer_list, answer_return_list):
            data_bubble = {
                "type": "button",
                "action": {
                    "type": "message",
                    "label": label_text,
                    "text": return_text
                },
                "style": "primary",
                "color": "#674A8A",
                "adjustMode": "shrink-to-fit"
            }
            data_list.append(data_bubble)
        flex_message = FlexSendMessage(
            alt_text='人生保險規劃 退休規劃',
            contents={
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "人生保險規劃 退休規劃",
                            "weight": "bold",
                            "size": "xl"
                        }
                    ],
                    "alignItems": "center"
                },
                "hero": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://imgur.com/5zEa62b.png",
                            "align": "center",
                            "size": "full",
                            "gravity": "center"
                        },
                        {
                            "type": "text",
                            "text": description,
                            "size": "lg",
                            "wrap": True
                        }
                    ],
                    "alignItems": "center",
                    "paddingStart": "xxl",
                    "paddingEnd": "xxl"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": data_list,
                    "spacing": "md",
                    "paddingStart": "md",
                    "paddingEnd": "md"
                }
            }
        )
        return flex_message

    def reply_result(line_bot_api, event):
        check_data = {"user_id": event.source.user_id}
        request_data = dbUserRequest.find_one(check_data)
        check_data = {"insurance_group": "life_stage1_result",
                      "age": "年齡"+request_data["age"]+"歲"}
        reply_data = dbInsurance.find_one(check_data)
        myReply = ""
        myReply += "選擇階段題目："+request_data["life_stage2_type"]+'\n'
        myReply += reply_data["guarantee_direction"]
        check_data = {"user_id": event.source.user_id}
        button_result = Life_stage1_result().result_button2(check_data, event)
        myReply = Result_template(myReply).content(
            "人生保險規劃 退休規劃紀錄", "https://imgur.com/5zEa62b.png")
        line_bot_api.reply_message(
            event.reply_token,
            [myReply, FlexSendMessage(
                alt_text='險種按鈕', contents=button_result)]
        )
        # TextSendMessage(text=myReply)

    def multiple_button():
        flex_message = FlexSendMessage(
            alt_text='青春活力',
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "青春活力",
                                "text": "青春活力"
                            },
                            "style": "primary",
                            "color": "#674A8A"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "青春活力_基本型",
                                "text": "青春活力_基本型"
                            },
                            "style": "primary",
                            "color": "#674A8A"
                        }
                    ],
                    "spacing": "md",
                    "paddingStart": "md",
                    "paddingEnd": "md"
                }
            }
        )
        return flex_message

    def multiple_button2():
        flex_message = FlexSendMessage(
            alt_text='單身貴族',
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "單身貴族",
                                "text": "單身貴族"
                            },
                            "style": "primary",
                            "color": "#674A8A"
                        },
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "單身貴族_小資族",
                                "text": "單身貴族_小資族"
                            },
                            "style": "primary",
                            "color": "#674A8A"
                        }
                    ],
                    "spacing": "md",
                    "paddingStart": "md",
                    "paddingEnd": "md"
                }
            }
        )
        return flex_message
# 「功能列表」按鈕樣板訊息


class function_list():

    def content(self):
        flex_message = FlexSendMessage(
            alt_text='hello',
            contents={
                "type": "carousel",
                "contents": [
                    {
                        "type": "bubble",
                        "direction": "ltr",
                        "hero": {
                            "type": "image",
                            "url": "https://imgur.com/xcfPFuT.png",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover",
                            "backgroundColor": "#FFFFFFFF"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "backgroundColor": "#FFFFFFFF",
                            "borderColor": "#FFFFFFFF",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "適合性分析",
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "gravity": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "backgroundColor": "#FFFFFFFF",
                            "borderColor": "#FFFFFFFF",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "適合性分析",
                                        "text": "適合性分析"
                                    },
                                    "color": "#DCC639",
                                    "style": "primary"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "適合性分析結果",
                                        "text": "適合性分析結果"
                                    },
                                    "color": "#DCC639",
                                    "style": "primary"
                                }
                            ]
                        },
                        "styles": {
                            "hero": {
                                "backgroundColor": "#FFFFFFFF"
                            }
                        }
                    },
                    {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://imgur.com/QxcwBuz.png",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "汽車保險規劃",
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "gravity": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "汽車保險規劃",
                                        "text": "汽車保險規劃"
                                    },
                                    "color": "#D34149",
                                    "style": "primary"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "汽車保險規劃結果",
                                        "text": "汽車保險規劃結果"
                                    },
                                    "color": "#D34149",
                                    "style": "primary"
                                }
                            ]
                        }
                    },
                    {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://imgur.com/FUwl0XE.png",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "人生保險規劃",
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "gravity": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "人生保險規劃",
                                        "text": "人生保險規劃"
                                    },
                                    "color": "#81C25E",
                                    "style": "primary"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "人生保險規劃紀錄",
                                        "text": "人生保險規劃紀錄"
                                    },
                                    "color": "#81C25E",
                                    "style": "primary"
                                }
                            ]
                        }
                    },
                    {
                        "type": "bubble",
                        "hero": {
                            "type": "image",
                            "url": "https://imgur.com/5zEa62b.png",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "人生保險規劃 退休規劃",
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "gravity": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "人生保險規劃 退休規劃",
                                        "text": "人生保險規劃 退休規劃"
                                    },
                                    "color": "#674A8A",
                                    "style": "primary"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "人生保險規劃 退休規劃紀錄",
                                        "text": "人生保險規劃 退休規劃紀錄"
                                    },
                                    "color": "#674A8A",
                                    "style": "primary"
                                }
                            ]
                        }
                    },
                    {
                        "type": "bubble",
                        "direction": "ltr",
                        "hero": {
                            "type": "image",
                            "url": "https://imgur.com/NQtG7fx.png",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "保障缺口分析",
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "gravity": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "保障缺口分析",
                                        "text": "保障缺口分析"
                                    },
                                    "color": "#4D4DFF",
                                    "style": "primary"
                                },
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "保障缺口紀錄",
                                        "text": "保障缺口紀錄"
                                    },
                                    "color": "#4D4DFF",
                                    "style": "primary"
                                }
                            ]
                        }
                    },
                    {
                        "type": "bubble",
                        "direction": "ltr",
                        "hero": {
                            "type": "image",
                            "url": "https://imgur.com/Cs0E3oS.png",
                            "size": "full",
                            "aspectRatio": "20:13",
                            "aspectMode": "cover"
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "退休財務規劃",
                                    "weight": "bold",
                                    "size": "xl",
                                    "align": "center",
                                    "gravity": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "退休財務規劃",
                                        "text": "退休財務規劃"
                                    },
                                    "color": "#6A4616",
                                    "style": "primary"
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "button",
                                            "action": {
                                                "type": "message",
                                                "label": "退休財務紀錄",
                                                "text": "退休財務紀錄"
                                            },
                                            "color": "#6A4616",
                                            "style": "primary",
                                            "gravity": "bottom",
                                            "position": "relative"
                                        },
                                        {
                                            "type": "button",
                                            "action": {
                                                "type": "message",
                                                "label": "退休資產",
                                                "text": "退休資產"
                                            },
                                            "color": "#6A4616",
                                            "style": "primary"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        )
        return flex_message
