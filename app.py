# -*- coding: utf8 -*-
from decimal import Context
from flask import Flask, request, abort
import flask_mail
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, PostbackEvent, TextMessage, TextSendMessage, ImageSendMessage, FlexSendMessage
from linebot.models.flex_message import BubbleContainer, BubbleStyle, BoxComponent, ButtonComponent, TextComponent, BlockStyle
from linebot.models.actions import MessageAction, PostbackAction
from message import *
from pymongo import MongoClient
import configparser
import re
import os

from guarantee_gap import Guarantee_gap
from joint_financial_planning import Joint_financial


app = Flask(__name__)
app.config["ENV"] = "development"
app.config["DEBUG"] = True

# config 環境設定解析
config = configparser.ConfigParser()
config.read("config.ini")

# Linebot 金鑰
line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])

# mongoDB atlas 連線
myMongoClient = MongoClient(config['connect_config']['Mongodb_atlas_URL'])
myMongoDb = myMongoClient["insurance-data"]

# 使用者請求
dbUserRequest = myMongoDb['user-request']
# 適合性分析題庫
dbQuestion = myMongoDb['qusetion-database']
# 投資建議資料庫
dbAdvice = myMongoDb['investment-advice']
# 車險種類資料庫
dbCar_insurance = myMongoDb['car_insurance_type']
# 保險建議資料庫
dbInsurance = myMongoDb['insurance-advice']


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config['flask_mail']['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = config['flask_mail']['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail_object = flask_mail.Mail(app)

# 退休財務規劃 問題模式
joint_financial_question_mode = "question"
# 模糊搜尋表
word_mapping = {
    "功能列表": ["功能列表"],
    "使用說明": ["使用說明"],
    "適合性": ["適合性分析", "適合性分析結果"],
    "分析": ["適合性分析", "適合性分析結果", "保障缺口分析"],
    "結果": ["適合性分析結果", "汽車保險規劃結果"],
    "汽車": ["汽車保險規劃", "汽車保險規劃結果"],
    "保": ["汽車保險規劃", "汽車保險規劃結果", "人生保險規劃", "人生保險規劃 退休規劃", "人生保險規劃紀錄", "人生保險規劃 退休規劃紀錄", "保障缺口分析", "保障缺口紀錄"],
    "險": ["汽車保險規劃", "汽車保險規劃結果", "人生保險規劃", "人生保險規劃 退休規劃", "人生保險規劃紀錄", "人生保險規劃 退休規劃紀錄"],
    "規劃": ["汽車保險規劃", "汽車保險規劃結果", "人生保險規劃", "人生保險規劃 退休規劃", "人生保險規劃紀錄", "人生保險規劃 退休規劃紀錄", "退休財務規劃"],
    "人生": ["人生保險規劃", "人生保險規劃 退休規劃", "人生保險規劃紀錄", "人生保險規劃 退休規劃紀錄"],
    "退休": ["人生保險規劃 退休規劃", "人生保險規劃 退休規劃紀錄", "退休財務規劃", "退休財務紀錄", "退休資產"],
    "紀錄": ["人生保險規劃紀錄", "人生保險規劃 退休規劃紀錄", "保障缺口紀錄", "退休財務紀錄"],
    "障缺口": ["保障缺口分析", "保障缺口紀錄"],
    "財務": ["退休財務規劃", "退休財務紀錄"],
    "資產": ["退休資產"]
}


# Line bot 的主要 function，以下設定如非必要最好別動


@app.route("/callback", methods=['POST'])
def callback():
    # 抓 X-Line-Signature 標頭的值
    signature = request.headers['X-Line-Signature']
    # 抓 request body 的文字
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        # 把文字和標頭存進handler
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'ok'

# message bot 接收到使用者資料時跑的 function


@handler.add(MessageEvent, message=(TextMessage))
def handle_message(event):
    # 檢查使用者ID是否存在於資料庫
    check_data = {"user_id": event.source.user_id}
    user_data = dbUserRequest.find(check_data)
    # 初始化回傳文字
    myReply = "請輸入正確的關鍵字！"
    # 如果使用者輸入文字
    if event.message.type == "text":
        typing_field = Joint_financial.on_typing(event.source.user_id)
        if not typing_field:
            # 功能列表
            if re.compile("[功]+[能]+[列]+[表]+").search(event.message.text) is not None:
                # 回復「功能列表」按鈕樣板訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    function_list().content()
                )
                return
            elif re.compile("[使]+[用]+[說]+[明]+").search(event.message.text) is not None:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="使用說明\n\n點擊選單中的功能列表，會顯示六種不同類型的問卷，可以依照您的需求，並得到適合您的投資方式。\n\n適合性分析：根據自身的投資習慣，分析出適合您的投資類型，並得到相關的保險建議。\n\n汽車保險規劃：根據題目選擇與自身相符的選項，機器人會自動計算結果並推薦給您最適合的汽車保險。\n\n人生保險規劃：依照您的實際情況，機器人會計算不同結果的權重，給予現階段推薦的保險種類及建議。\n\n人生保險規劃 退休規劃：機器人依照您的年齡和性別，給予現階段推薦的保險種類及建議。\n\n保障缺口分析：根據題目選擇與自身相符的選項，機器人會自動計算保障缺口並推薦適合的保險給您。\n\n退休財務規劃：根據題目回覆自己的資訊，機器人會自動計算並寄送試算結果，使您能夠提前規劃退休生活。")
                )
            # 使用者適合性分析
            elif re.compile("適合性分析").search(event.message.text) is not None and re.compile("適合性分析結果").search(event.message.text) is None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Suitability_analysis", "question_number": "1",
                                                                                      "score": "0", "answer_record_suitability": "", "suitability_analysis_type": "", "multiple_options": "", "current_Q": "1"}}, upsert=True)
                # 回傳適合性分析題目
                myReply = Suitability_analysis(event.source.user_id).content()
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 使用者汽車保險規劃
            elif re.compile("汽車保險規劃").search(event.message.text) is not None and re.compile("汽車保險規劃結果").search(event.message.text) is None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {
                    "status": "Car_insurance_planning", "question_number": "1", "answer_record_car_insurance": "", "current_Q": "1"}}, upsert=True)
                # 回傳汽車保險規劃題目
                myReply = Car_insurance_planning(
                    event.source.user_id).content()
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 使用者汽車保險規劃結果
            elif re.compile("汽車保險規劃結果").search(event.message.text) is not None:
                # 如果使用者使用過汽車保險規劃
                if user_data.count() != 0 and user_data[0]["answer_record_car_insurance"] != "":
                    # 分割每題題號和選項
                    answer_record_list = user_data[0]["answer_record_car_insurance"].split(
                        "-")
                    # 回傳資料格式
                    insurance_record_list = user_data[0]["insurance_record"].split(
                        "-")
                    myReply = ""
                    for record in insurance_record_list:
                        if record != "":
                            myReply += "車險建議：" + record + "\n"
                    # 獲取人生階段建議
                    check_data = {
                        "type_name": user_data[0]["life_stage_type_car_insurance"], "insurance_group": "joint_financial_planning"}
                    life_stage = dbInsurance.find_one(check_data)
                    myReply += "人生階段：" + life_stage["type_name"] + "\n"
                    myReply += "適用人群：" + \
                        life_stage["guarantee_direction"] + "\n"
                    myReply += "選項紀錄：" + "\n"
                    for record in answer_record_list:
                        if record != "":
                            myReply += record + "\n"
                            ans = record.split(":")
                            # 獲取題庫資料
                            check_data = {
                                "question_number": ans[0], "question_group": "Car_insurance_planning"}
                            qusetion = dbQuestion.find_one(check_data)
                            # 回傳題目字串
                            myReply += "題目:" + qusetion["description"] + "\n"
                            # 依答案選項回傳答案字串
                            myReply += "選項:"
                            if ans[1] == "A":
                                myReply += qusetion["answerA"] + "\n"
                            elif ans[1] == "B":
                                myReply += qusetion["answerB"] + "\n"
                            elif ans[1] == "C":
                                myReply += qusetion["answerC"] + "\n"
                            elif ans[1] == "D":
                                myReply += qusetion["answerD"] + "\n"
                            elif ans[1] == "E":
                                myReply += qusetion["answerE"] + "\n"
                            # 結尾分行
                            myReply += "\n"
                    myReply += "其他保險建議：" + life_stage["insurance_list"] + "\n"
                    myReply += "網址：" + life_stage["url"] + "\n"
                    myReply += "保費：" + str(life_stage["cost"]) + "\n"
                    myReply = Result_template(myReply).content(
                        "汽車保險規劃結果", "https://imgur.com/QxcwBuz.png")
                    line_bot_api.reply_message(
                        event.reply_token,
                        myReply
                    )
                    return
                else:
                    myReply = "尚未進行汽車保險規劃"
            # 人生保險規劃
            elif re.compile("人生保險規劃").search(event.message.text) is not None and re.compile("人生保險規劃紀錄").search(event.message.text) is None and re.compile("退休規劃").search(event.message.text) is None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Life_stage1", "question_number": "1", "gender": "",
                                         "score": "0", "answer_record_life_stage": "", "life_stage1_type": "", "multiple_options": "", "current_Q": "1"}}, upsert=True)
                # 回傳人生保險規劃題目
                myReply = Life_stage1(event.source.user_id).content()
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 人生保險規劃 退休規劃
            elif re.compile("人生保險規劃 退休規劃").search(event.message.text) is not None and re.compile("人生保險規劃 退休規劃紀錄").search(event.message.text) is None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Life_stage2", "question_number": "1", "gender": "",
                                         "score": "0", "answer_record_life_stage2": "", "age": "", "life_stage2_type": "", "multiple_options": "", "current_Q": "2", "answered": "0"}}, upsert=True)
                myReply = Life_stage2(event.source.user_id).content()
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 保障缺口分析
            elif re.compile("保障缺口分析").search(event.message.text) is not None:
                # 回傳退休財務分析
                myReply = Guarantee_gap.content(event.source.user_id)
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 退休財務規劃
            elif re.compile("退休財務規劃").search(event.message.text) is not None:
                # 回傳退休財務規劃
                myReply = Joint_financial.content(
                    event.source.user_id, mode=joint_financial_question_mode)
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 保障缺口紀錄
            elif re.compile("保障缺口紀錄").search(event.message.text) is not None:
                # 回傳保障缺口紀錄
                myReply = Guarantee_gap.content(event.source.user_id, False)
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 退休財務紀錄
            elif re.compile("退休財務紀錄").search(event.message.text) is not None:
                # 回傳退休財務規劃
                myReply = Joint_financial.content(
                    event.source.user_id, mode=joint_financial_question_mode, calculate=False, mail=mail_object)
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            # 退休資產
            elif re.compile("退休資產").search(event.message.text) is not None:
                # 回傳退休資產
                myReply = Joint_financial.content(
                    event.source.user_id, mode=joint_financial_question_mode, calculate=False, get_asset=True)
                line_bot_api.reply_message(
                    event.reply_token,
                    myReply
                )
                return
            elif re.compile("ex:").search(event.message.text) is not None:
                question = dbUserRequest.find_one(check_data)
                if question["current_Q"] == "1":
                    if event.message.text.split(":")[0] == "適合性ex":
                        advice = dbInsurance.find_one(
                            {"type_name": user_data[0]["life_stage_type_suitability"], "button_insurance": "1"})
                    elif event.message.text.split(":")[0] == "車險ex":
                        advice = dbInsurance.find_one(
                            {"type_name": user_data[0]["life_stage_type_car_insurance"], "button_insurance": "1"})
                    if event.message.text.split(":")[1] == "實支實付醫療險":
                        myReply = advice["醫療險"]
                    elif event.message.text.split(":")[1] == "終身險" or event.message.text.split(":")[1] == "定期險":
                        myReply = advice["終身定期"]
                    else:
                        myReply = advice[event.message.text.split(":")[1]]
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("婦嬰險").search(event.message.text) is not None:
                myReply = Life_stage1_result.insurance_8(check_data)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("醫療險").search(event.message.text) is not None:
                question = dbUserRequest.find_one(check_data)
                myReply = Life_stage1_result.insurance_4(check_data)
                if question["life_stage_type"] == "親親寶貝":
                    line_bot_api.reply_message(
                        event.reply_token,
                        myReply
                    )
                elif question["life_stage1_type"] == "親親寶貝":
                    line_bot_api.reply_message(
                        event.reply_token,
                        myReply
                    )
                elif question["life_stage2_type"] == "親親寶貝":
                    line_bot_api.reply_message(
                        event.reply_token,
                        myReply
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=myReply)
                    )
                return
            elif re.compile("終身定期").search(event.message.text) is not None:
                myReply = Life_stage1_result.insurance_7(check_data)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("癌症險").search(event.message.text) is not None:
                myReply = Life_stage1_result.insurance_6(check_data)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("重大疾病險").search(event.message.text) is not None:
                myReply = Life_stage1_result.insurance_3(check_data)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("意外險").search(event.message.text) is not None:
                myReply = Life_stage1_result.insurance_1(check_data)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("失能險").search(event.message.text) is not None:
                myReply = Life_stage1_result.insurance_2(check_data)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("壽險").search(event.message.text) is not None:
                myReply = Life_stage1_result.insurance_5(check_data)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=myReply)
                )
                return
            elif re.compile("單身貴族_小資族").search(event.message.text) is not None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {
                    "$set": {"life_stage2_type": "單身貴族_小資族"}}, upsert=True)
                Life_stage2.reply_result(line_bot_api, event)
                return
            elif re.compile("單身貴族").search(event.message.text) is not None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {
                    "$set": {"life_stage2_type": "單身貴族"}}, upsert=True)
                Life_stage2.reply_result(line_bot_api, event)
                return
            elif re.compile("青春活力_基本型").search(event.message.text) is not None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {
                    "$set": {"life_stage2_type": "青春活力_基本型"}}, upsert=True)
                Life_stage2.reply_result(line_bot_api, event)
                return
            elif re.compile("青春活力").search(event.message.text) is not None:
                dbUserRequest.update_one({"user_id": event.source.user_id}, {
                    "$set": {"life_stage2_type": "青春活力"}}, upsert=True)
                Life_stage2.reply_result(line_bot_api, event)
                return
            # 使用者適合性分析結果
            elif re.compile("適合性分析結果").search(event.message.text) is not None:
                # 如果使用者使用過適合性分析
                if user_data.count() != 0 and user_data[0]["answer_record_suitability"] != "":
                    # 回傳分析結果
                    answer_record_suitability_list = user_data[0]["answer_record_suitability"].split(
                        "-")
                    # 獲取投資類型對應的投資建議
                    check_data = {
                        "suitability_analysis_type": user_data[0]["suitability_analysis_type"]}
                    advice_data = dbAdvice.find(check_data)
                    # 回傳資料格式
                    myReply = "投資類型：" + \
                        user_data[0]["suitability_analysis_type"] + "\n"
                    myReply += "投資建議：" + advice_data[0]["advice"] + "\n"
                    myReply += "加總分數：" + user_data[0]["score"] + "\n"
                    # 獲取人生階段建議
                    check_data = {
                        "type_name": user_data[0]["life_stage_type_suitability"], "insurance_group": "joint_financial_planning"}
                    life_stage = dbInsurance.find_one(check_data)
                    myReply += "人生階段：" + life_stage["type_name"] + "\n"
                    myReply += "適用人群：" + \
                        life_stage["guarantee_direction"] + "\n"
                    myReply += "選項紀錄：" + "\n"
                    for record in answer_record_suitability_list:
                        if record != "":
                            myReply += record + "\n"
                            ans = record.split(":")
                            check_data = {
                                "question_number": ans[0], "question_group": "Suitability_analysis"}
                            qusetion = dbQuestion.find_one(check_data)
                            # 回傳題目字串
                            myReply += "題目:" + qusetion["description"] + "\n"
                            # 依答案選項回傳答案字串
                            myReply += "選項:"
                            if ans[1] == "1":
                                myReply += qusetion["answer1"] + "\n"
                            elif ans[1] == "2":
                                myReply += qusetion["answer2"] + "\n"
                            elif ans[1] == "3":
                                myReply += qusetion["answer3"] + "\n"
                            elif ans[1] == "4":
                                myReply += qusetion["answer4"] + "\n"
                            elif ans[1] == "5":
                                myReply += qusetion["answer5"] + "\n"
                            else:
                                for i in ans[1]:
                                    if i == "1":
                                        myReply += qusetion["answer1"] + "\n"
                                    elif i == "2":
                                        myReply += qusetion["answer2"] + "\n"
                                    elif i == "3":
                                        myReply += qusetion["answer3"] + "\n"
                                    elif i == "4":
                                        myReply += qusetion["answer4"] + "\n"
                                    elif i == "5":
                                        myReply += qusetion["answer5"] + "\n"
                            # 結尾分行
                            myReply += "\n"
                    myReply += "其他保險建議：" + life_stage["insurance_list"] + "\n"
                    myReply += "網址：" + life_stage["url"] + "\n"
                    myReply += "保費：" + str(life_stage["cost"]) + "\n"
                    myReply = Result_template(myReply).content(
                        "適合性分析結果", "https://imgur.com/xcfPFuT.png")
                    line_bot_api.reply_message(
                        event.reply_token,
                        myReply
                    )
                    return
                else:
                    myReply = "尚未進行適合性分析"
            elif re.compile("人生保險規劃紀錄").search(event.message.text) is not None:
                check_data = {"user_id": event.source.user_id}
                request_data = dbUserRequest.find_one(check_data)
                if request_data["life_stage1_type"] == "":
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請先完成人生保險規劃")
                    )
                    return
                myReply = Life_stage1_result().record(check_data, event)
                myReply = Result_template(myReply).content("人生保險規劃紀錄", "https://imgur.com/FUwl0XE.png")
                button_result = Life_stage1_result().result_button(check_data, event)
                line_bot_api.reply_message(
                    event.reply_token,
                    [myReply, FlexSendMessage(
                        alt_text='險種按鈕', contents=button_result)]
                )
                return
            elif re.compile("人生保險規劃 退休規劃紀錄").search(event.message.text) is not None:
                check_data = {"user_id": event.source.user_id}
                request_data = dbUserRequest.find_one(check_data)
                if request_data["life_stage2_type"] == "":
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請先完成人生保險規劃 退休規劃")
                    )
                    return
                Life_stage2.reply_result(line_bot_api, event)
                return
            # 使用者點選答案按鈕
            elif "ans:" in event.message.text:
                # 如果使用者正在進行適合性分析
                if user_data.count() != 0 and user_data[0]["status"] == "Suitability_analysis":
                    # 最後一題總結函式
                    def Suitability_analysis_final_question(sum_score, answer_record_suitability):
                        if sum_score < 14:
                            suitability_analysis_type = "保守型"
                        elif sum_score < 22:
                            suitability_analysis_type = "非常謹慎型"
                        elif sum_score < 31:
                            suitability_analysis_type = "謹慎型"
                        elif sum_score < 40:
                            suitability_analysis_type = "穩健型"
                        elif sum_score < 50:
                            suitability_analysis_type = "積極型"
                        else:
                            suitability_analysis_type = "冒險型"
                        # 獲取投資類型對應的投資建議
                        check_data = {
                            "suitability_analysis_type": suitability_analysis_type}
                        advice_data = dbAdvice.find(check_data)
                        # 回傳分析結果
                        answer_record_suitability_list = answer_record_suitability.split(
                            "-")
                        # 回傳資料格式
                        myReply = "投資類型：" + suitability_analysis_type + "\n"
                        myReply += "投資建議：" + advice_data[0]["advice"] + "\n"
                        myReply += "加總分數：" + str(sum_score) + "\n"
                        myReply_record = ""
                        myReply_record += "選項紀錄：" + "\n"
                        for record in answer_record_suitability_list:
                            if record != "":
                                myReply_record += record + "\n"
                                ans = record.split(":")
                                # 獲取題目資料
                                check_data = {
                                    "question_number": ans[0], "question_group": "Suitability_analysis"}
                                qusetion = dbQuestion.find_one(check_data)
                                # 如果題目為年齡區間
                                if ans[0] == "7":
                                    # 70歲以上
                                    if ans[1] == "1":
                                        age_range = qusetion["answer1"]
                                    # 69-60歲
                                    elif ans[1] == "2":
                                        age_range = qusetion["answer2"]
                                    # 59-45歲
                                    elif ans[1] == "3":
                                        age_range = qusetion["answer3"]
                                    # 44-29歲
                                    elif ans[1] == "4":
                                        age_range = qusetion["answer4"]
                                    # 28-20歲
                                    elif ans[1] == "5":
                                        age_range = qusetion["answer5"]
                                # 如果題目為投保傾向
                                elif ans[0] == "13":
                                    if age_range == "70歲以上" or age_range == "69-60歲":
                                        # 設定人生階段
                                        life_stage_type = "退休"
                                    elif age_range == "59-45歲":
                                        life_stage_type = "開始退休規劃"
                                    elif age_range == "44-29歲":
                                        if ans[1] == "1":
                                            life_stage_type = "成家立業"
                                        elif ans[1] == "2":
                                            life_stage_type = "為人父母"
                                    elif age_range == "28-20歲":
                                        if ans[1] == "1":
                                            life_stage_type = "單身貴族_小資族"
                                        elif ans[1] == "2":
                                            life_stage_type = "單身貴族"
                                    # 獲取人生階段建議
                                    check_data = {
                                        "type_name": life_stage_type, "insurance_group": "joint_financial_planning"}
                                    life_stage = dbInsurance.find_one(
                                        check_data)
                                    myReply += "人生階段：" + life_stage_type + "\n"
                                    myReply += "適用人群：" + \
                                        life_stage["guarantee_direction"] + "\n"
                                # 回傳題目字串
                                myReply_record += "題目:" + \
                                    qusetion["description"] + "\n"
                                # 依答案選項回傳答案字串
                                myReply_record += "選項:"
                                if ans[1] == "1":
                                    myReply_record += qusetion["answer1"] + "\n"
                                elif ans[1] == "2":
                                    myReply_record += qusetion["answer2"] + "\n"
                                elif ans[1] == "3":
                                    myReply_record += qusetion["answer3"] + "\n"
                                elif ans[1] == "4":
                                    myReply_record += qusetion["answer4"] + "\n"
                                elif ans[1] == "5":
                                    myReply_record += qusetion["answer5"] + "\n"
                                else:
                                    for i in ans[1]:
                                        if i == "1":
                                            myReply_record += qusetion["answer1"] + "\n"
                                        elif i == "2":
                                            myReply_record += qusetion["answer2"] + "\n"
                                        elif i == "3":
                                            myReply_record += qusetion["answer3"] + "\n"
                                        elif i == "4":
                                            myReply_record += qusetion["answer4"] + "\n"
                                        elif i == "5":
                                            myReply_record += qusetion["answer5"] + "\n"
                                # 結尾分行
                                myReply_record += "\n"
                        myReply += myReply_record
                        myReply += "其他保險建議：" + \
                            life_stage["insurance_list"] + "\n"
                        myReply += "網址：" + life_stage["url"] + "\n"
                        myReply += "保費：" + str(life_stage["cost"]) + "\n"
                        # 回傳文字轉換成模板格式
                        myReply = Result_template(myReply).content("適合性分析結果", "https://imgur.com/xcfPFuT.png")
                        # 清空請求、紀錄答案及計算分數
                        dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "0", "question_number": "0", "score": str(
                            sum_score), "answer_record_suitability": answer_record_suitability, "suitability_analysis_type": suitability_analysis_type, "multiple_options": "", "life_stage_type_suitability": life_stage_type}}, upsert=True)
                        return myReply
                    # 題目代號
                    question_number = event.message.text.split(":")[
                        1].split("-")[0]
                    # 嘗試取出下列資料
                    try:
                        # 使用者答案
                        answer = event.message.text.split(":")[1].split("-")[1]
                        # 如果當前題目不是最後一題([13]投保傾向不計分數)
                        if question_number != "13":
                            # 加總新的分數
                            sum_score = int(
                                user_data[0]["score"]) + int(answer)
                        # 如果當前題目是最後一題
                        else:
                            # [13]投保傾向不計分數, 分數維持不變
                            sum_score = int(user_data[0]["score"])
                        # 紀錄選取答案
                        answer_record_suitability = user_data[0]["answer_record_suitability"] + \
                            "-" + question_number + ":" + answer
                    # 取出資料失敗表示答案不是"ans:1-1"格式, 如:"ans:[確定]"
                    except:
                        pass
                    # 檢查該問題是否已經回答過
                    record_list = []
                    record_data = user_data[0]["answer_record_suitability"].split(
                        "-")
                    for record in record_data:
                        # 如果暫存結果內存在相同題號
                        if record.split(":")[0] == question_number:
                            # 設定警告訊息
                            myReply = "不可重複回答"
                            # 傳送訊息給使用者
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text=myReply)
                            )
                            return
                    # 獲取當前題目
                    check_data = {"question_number": question_number,
                                  "question_group": "Suitability_analysis"}
                    qusetion = dbQuestion.find_one(check_data)
                    # 如果當前題目不是最後一題且是單選題
                    if qusetion["final_question"] != "1" and qusetion["question_type"] == "Suitability_analysis":
                        # 更換題目、紀錄答案及計算分數
                        dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Suitability_analysis", "question_number": str(
                            int(question_number)+1), "score": str(sum_score), "answer_record_suitability": answer_record_suitability}}, upsert=True)
                        # 回傳適合性分析題目
                        myReply = Suitability_analysis(
                            event.source.user_id).content()
                        line_bot_api.reply_message(
                            event.reply_token,
                            myReply
                        )
                        return
                    # 如果當前題目是最後一題且是單選題
                    elif qusetion["final_question"] == "1" and qusetion["question_type"] == "Suitability_analysis":
                        # 進行最後一題總結
                        myReply = Suitability_analysis_final_question(
                            sum_score, answer_record_suitability)
                        line_bot_api.reply_message(
                            event.reply_token,
                            myReply
                        )
                        return
                    # 如果當前題目是複選題
                    elif qusetion["question_type"] == "Suitability_analysis_multiple":
                        # 如果使用者點選確定之外的選項
                        if "[確定]" not in event.message.text:
                            # 如果答案還沒選過
                            if answer not in user_data[0]["multiple_options"]:
                                # 添加複選答案
                                multiple_options = user_data[0]["multiple_options"] + answer
                            # 如果答案已經選過
                            else:
                                # 刪除複選答案
                                multiple_options = user_data[0]["multiple_options"].replace(
                                    answer, "")
                            # 回傳已選擇的複選答案提示
                            myReply = "已選擇：" + multiple_options
                            # 暫存答案
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {
                                                     "status": "Suitability_analysis", "multiple_options": multiple_options}}, upsert=True)
                        # 如果使用者點選確定
                        else:
                            # 檢查是否有暫存複選題選項
                            check_data = {"user_id": event.source.user_id}
                            check_options = dbUserRequest.find_one(check_data)
                            # 如果複選題選項不為空
                            if check_options["multiple_options"] != "":
                                # 紀錄選取答案
                                answer_record_suitability = user_data[0]["answer_record_suitability"] + \
                                    "-" + question_number + ":" + \
                                    user_data[0]["multiple_options"]
                                # 計算複選答案總分數
                                sub_score = 0
                                for i in range(len(user_data[0]["multiple_options"])):
                                    sub_score += int(user_data[0]
                                                     ["multiple_options"][i])
                                # 添加複選答案總分數
                                sum_score = int(
                                    user_data[0]["score"]) + sub_score
                                # 如果當前題目不是最後一題
                                if qusetion["final_question"] != "1":
                                    # 更換題目、紀錄答案及計算分數
                                    dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Suitability_analysis", "question_number": str(int(
                                        question_number)+1), "score": str(sum_score), "answer_record_suitability": answer_record_suitability, "multiple_options": ""}}, upsert=True)
                                    # 回傳適合性分析題目
                                    myReply = Suitability_analysis(
                                        event.source.user_id).content()
                                    line_bot_api.reply_message(
                                        event.reply_token,
                                        myReply
                                    )
                                    return
                                # 如果當前題目是最後一題
                                else:
                                    # 進行最後一題總結
                                    myReply = Suitability_analysis_final_question(
                                        sum_score, answer_record_suitability)
                            # 如果複選題選項為空
                            else:
                                myReply = "請選擇至少一項複選題選項"

                # 如果使用者正在進行汽車保險規劃
                elif user_data.count() != 0 and user_data[0]["status"] == "Car_insurance_planning":
                    # 最後一題總結函式
                    def Car_insurance_planning_final_question(answer_record_car_insurance):
                        # 初始化選項計數器
                        A_count = 0
                        B_count = 0
                        C_count = 0
                        D_count = 0
                        E_count = 0
                        # 分割每題題號和選項
                        answer_record_list = answer_record_car_insurance.split(
                            "-")
                        for answer_record in answer_record_list:
                            # 如果當前題目是最後一題([12]投保傾向不計分數)
                            if answer_record.split("-")[0] == "12":
                                # 跳出迴圈不計數
                                break
                            # 如果該選項存在於分割後的字串裡
                            if "A" in answer_record:
                                # 該選項計數器遞增
                                A_count += 1
                            elif "B" in answer_record:
                                B_count += 1
                            elif "C" in answer_record:
                                C_count += 1
                            elif "D" in answer_record:
                                D_count += 1
                            elif "E" in answer_record:
                                E_count += 1
                        # 取出所有車險種類
                        car_insurance_list = dbCar_insurance.find()
                        # 初始化優先權暫存清單
                        insurance_list = []
                        for car_insurance in car_insurance_list:
                            # 如果五個計數器的值均大於車險底值
                            if A_count >= int(car_insurance["A_count"]) and B_count >= int(car_insurance["B_count"]) and C_count >= int(car_insurance["C_count"]) and D_count >= int(car_insurance["D_count"]) and E_count >= int(car_insurance["E_count"]):
                                # 暫存該筆資料的優先權
                                insurance_list.append(
                                    car_insurance["priority"])
                        # 將優先權暫存清單由大到小排列
                        insurance_list.sort(reverse=True)
                        # 用第一筆車險的優先權獲取車險資料
                        check_data = {"priority": insurance_list[0]}
                        car_insurance = dbCar_insurance.find_one(check_data)
                        # 存取該筆資料推薦的車險
                        insurance_type_list = car_insurance["car_insurance"].split(
                            "-")
                        # 初始化車險險種
                        insurance_record = ""
                        myReply = ""
                        # 回傳資料格式
                        for insurance_type in insurance_type_list:
                            myReply += "車險建議：" + insurance_type + "\n"
                            insurance_record += "-" + insurance_type
                        myReply_record = ""
                        myReply_record += "選項紀錄：" + "\n"
                        for record in answer_record_list:
                            if record != "":
                                myReply_record += record + "\n"
                                ans = record.split(":")
                                # 獲取題目資料
                                check_data = {
                                    "question_number": ans[0], "question_group": "Car_insurance_planning"}
                                qusetion = dbQuestion.find_one(check_data)
                                # 如果題目為年齡區間
                                if ans[0] == "1":
                                    # 57歲以上
                                    if ans[1] == "A":
                                        age_range = qusetion["answerA"]
                                    # 57-46歲
                                    elif ans[1] == "B":
                                        age_range = qusetion["answerB"]
                                    # 45-34歲
                                    elif ans[1] == "C":
                                        age_range = qusetion["answerC"]
                                    # 33-22歲
                                    elif ans[1] == "D":
                                        age_range = qusetion["answerD"]
                                    # 22歲以下
                                    elif ans[1] == "E":
                                        age_range = qusetion["answerE"]
                                # 如果題目為投保傾向
                                elif ans[0] == "12":
                                    if age_range == "57歲以上":
                                        # 設定人生階段
                                        life_stage_type = "退休"
                                    elif age_range == "57-46歲":
                                        life_stage_type = "開始退休規劃"
                                    elif age_range == "45-34歲":
                                        if ans[1] == "A":
                                            life_stage_type = "成家立業"
                                        elif ans[1] == "B":
                                            life_stage_type = "為人父母"
                                    elif age_range == "33-22歲":
                                        if ans[1] == "A":
                                            life_stage_type = "單身貴族_小資族"
                                        elif ans[1] == "B":
                                            life_stage_type = "單身貴族"
                                    elif age_range == "22歲以下":
                                        if ans[1] == "A":
                                            life_stage_type = "青春活力_基本型"
                                        elif ans[1] == "B":
                                            life_stage_type = "青春活力"
                                    # 獲取人生階段建議
                                    check_data = {
                                        "type_name": life_stage_type, "insurance_group": "joint_financial_planning"}
                                    life_stage = dbInsurance.find_one(
                                        check_data)
                                    myReply += "人生階段：" + life_stage_type + "\n"
                                    myReply += "適用人群：" + \
                                        life_stage["guarantee_direction"] + "\n"
                                # 回傳題目字串
                                myReply_record += "題目:" + \
                                    qusetion["description"] + "\n"
                                # 依答案選項回傳答案字串
                                myReply_record += "選項:"
                                if ans[1] == "A":
                                    myReply_record += qusetion["answerA"] + "\n"
                                elif ans[1] == "B":
                                    myReply_record += qusetion["answerB"] + "\n"
                                elif ans[1] == "C":
                                    myReply_record += qusetion["answerC"] + "\n"
                                elif ans[1] == "D":
                                    myReply_record += qusetion["answerD"] + "\n"
                                elif ans[1] == "E":
                                    myReply_record += qusetion["answerE"] + "\n"
                                # 結尾分行
                                myReply_record += "\n"
                        myReply += myReply_record
                        myReply += "其他保險建議：" + \
                            life_stage["insurance_list"] + "\n"
                        myReply += "網址：" + life_stage["url"] + "\n"
                        myReply += "保費：" + str(life_stage["cost"]) + "\n"
                        # 回傳文字轉換成模板格式
                        myReply = Result_template(myReply).content("汽車保險規劃結果", "https://imgur.com/QxcwBuz.png")
                        # 清空請求、紀錄答案及計算分數
                        dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "0", "question_number": "0", "answer_record_car_insurance":
                                                 answer_record_car_insurance, "insurance_record": insurance_record, "life_stage_type_car_insurance": life_stage_type}}, upsert=True)
                        return myReply
                    # 題目代號
                    question_number = event.message.text.split(":")[
                        1].split("-")[0]
                    # 使用者答案
                    answer = event.message.text.split(":")[1].split("-")[1]
                    # 紀錄選取答案
                    answer_record_car_insurance = user_data[0]["answer_record_car_insurance"] + \
                        "-" + question_number + ":" + answer
                    # 檢查該問題是否已經回答過
                    record_list = []
                    record_data = user_data[0]["answer_record_car_insurance"].split(
                        "-")
                    for record in record_data:
                        # 如果暫存結果內存在相同題號
                        if record.split(":")[0] == question_number:
                            # 設定警告訊息
                            myReply = "不可重複回答"
                            # 傳送訊息給使用者
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text=myReply)
                            )
                            return
                    # 獲取當前題目
                    check_data = {"question_number": question_number,
                                  "question_group": "Car_insurance_planning"}
                    qusetion = dbQuestion.find_one(check_data)
                    # 如果當前題目不是最後一題
                    if qusetion["final_question"] != "1":
                        # 更換題目、紀錄答案及計算分數
                        dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Car_insurance_planning", "question_number": str(
                            int(question_number)+1), "answer_record_car_insurance": answer_record_car_insurance}}, upsert=True)
                        # 回傳汽車保險規劃題目
                        myReply = Car_insurance_planning(
                            event.source.user_id).content()
                        line_bot_api.reply_message(
                            event.reply_token,
                            myReply
                        )
                        return
                    # 如果當前題目是最後一題
                    elif qusetion["final_question"] == "1":
                        # 進行最後一題總結
                        myReply = Car_insurance_planning_final_question(
                            answer_record_car_insurance)
                        line_bot_api.reply_message(
                            event.reply_token,
                            myReply
                        )
                        return

                # 如果使用者正在進行人生保險規劃
                elif user_data.count() != 0 and user_data[0]["status"] == "Life_stage1":
                    # 最後一題總結函式
                    def Life_stage_final_question(sum_score, answer_record_life_stage):
                        if sum_score < 4:
                            life_stage1_type = "親親寶貝"
                        elif sum_score < 21:
                            life_stage1_type = "青春活力"
                        elif sum_score < 31:
                            life_stage1_type = "單身貴族"
                        elif sum_score < 41:
                            life_stage1_type = "成家立業"
                        elif sum_score < 51:
                            life_stage1_type = "為人父母"
                        else:
                            life_stage1_type = "開始退休規劃"
                        # 獲取投資類型對應的投資建議
                         # 回傳分析結果
                        answer_record_life_stage_list = answer_record_life_stage.split(
                            "-")
                        myReply = "本次適合性分析結果：\n"
                        # # 回傳資料格式
                        myReply = "人生階段:" + life_stage1_type + "\n"
                        myReply += "加總分數：" + str(sum_score) + "\n"
                        # # 清空請求、紀錄答案及計算分數
                        dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "0", "question_number": "0", "score": str(
                            sum_score), "answer_record_life_stage": answer_record_life_stage, "life_stage1_type": life_stage1_type, "multiple_options": ""}}, upsert=True)
                        myReply += "選項紀錄：" + "\n"
                        for i in range(len(answer_record_life_stage_list)):
                            if (i > 0):
                                check_data = {"question_number": str(i),
                                              "question_group": "Life_stage1"}
                                question = dbQuestion.find_one(check_data)
                                myReply += answer_record_life_stage_list[i] + "\n"
                                myReply += "題目:" + \
                                    question['description'] + "\n"
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
                        check_data = {
                            "type_name": user_data[0]["life_stage1_type"], "insurance_group": "life_stage1_result", "gender": sex}
                        question = dbInsurance.find_one(check_data)
                        myReply += question["guarantee_direction"] + "\n"
                        first_Reply = Life_stage1_result.first_time_reply(
                            check_data, myReply)
                        line_bot_api.reply_message(
                            event.reply_token,
                            FlexSendMessage(alt_text='險種按鈕',
                                            contents=first_Reply)
                        )
                        return

                    # 題目代號
                    question_number = event.message.text.split(":")[
                        1].split("-")[0]
                    # 嘗試取出下列資料
                    check_data = {"question_number": question_number,
                                  "question_group": "Life_stage1"}
                    qusetion = dbQuestion.find_one(check_data)
                    try:
                        # 使用者答案
                        answer = event.message.text.split(":")[1].split("-")[1]
                        # 加總新的分數(權重)
                        if int(answer) == 1:
                            newanswer = qusetion["answer1_count"]
                        elif int(answer) == 2:
                            newanswer = qusetion["answer2_count"]
                        elif int(answer) == 3:
                            newanswer = qusetion["answer3_count"]
                        elif int(answer) == 4:
                            newanswer = qusetion["answer4_count"]
                        elif int(answer) == 5:
                            newanswer = qusetion["answer5_count"]
                        else:
                            newanswer = qusetion["answer6_count"]
                        sum_score = int(user_data[0]["score"]) + int(newanswer)
                        # 紀錄選取答案
                        answer_record_life_stage = user_data[0]["answer_record_life_stage"] + \
                            "-" + question_number + ":" + str(answer)
                    # 取出資料失敗表示答案不是"ans:1-1"格式, 如:"ans:[確定]"
                    except:
                        pass
                    # 取得使用者性別
                    if (question_number == "2"):
                        if (answer == "1"):  # 男
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                                     "$set": {"gender": "1", }}, upsert=True)
                        elif (answer == "2"):  # 女
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                                     "$set": {"gender": "2", }}, upsert=True)
                    # 檢查該問題是否已經回答過
                    record_list = []
                    record_data = user_data[0]["answer_record_life_stage"].split(
                        "-")
                    for record in record_data:
                        # 如果暫存結果內存在相同題號
                        if record.split(":")[0] == question_number:
                            # 設定警告訊息
                            myReply = "不可重複回答"
                            # 傳送訊息給使用者
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text=myReply)
                            )
                            return
                    # 獲取當前題目
                    check_data = {"question_number": question_number,
                                  "question_group": "Life_stage1"}
                    qusetion = dbQuestion.find_one(check_data)
                    # 如果當前題目不是最後一題且是單選題
                    if qusetion["final_question"] != "1" and qusetion["question_type"] == "Life_stage1":
                        # 更換題目、紀錄答案及計算分數
                        dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Life_stage1", "question_number": str(
                            int(question_number)+1), "score": str(sum_score), "answer_record_life_stage": answer_record_life_stage}}, upsert=True)
                        # 回傳適合性分析題目
                        myReply = Life_stage1(event.source.user_id).content()
                        line_bot_api.reply_message(
                            event.reply_token,
                            myReply
                        )
                        return
                    # 如果當前題目是最後一題且是單選題
                    elif qusetion["final_question"] == "1" and qusetion["question_type"] == "Life_stage1":
                        # 進行最後一題總結
                        myReply = Life_stage_final_question(
                            sum_score, answer_record_life_stage)
                    # 如果當前題目是複選題
                    elif qusetion["question_type"] == "Life_stage1_multiple":
                        # 如果使用者點選確定之外的選項
                        if "[確定]" not in event.message.text:
                            # 使用者答案
                            answer = event.message.text.split(
                                ":")[1].split("-")[1]
                            # 加總新的分數(權重)
                            if int(answer) == 1:
                                newanswer = qusetion["answer1_count"]
                            elif int(answer) == 2:
                                newanswer = qusetion["answer2_count"]
                            elif int(answer) == 3:
                                newanswer = qusetion["answer3_count"]
                            elif int(answer) == 4:
                                newanswer = qusetion["answer4_count"]
                            elif int(answer) == 5:
                                newanswer = qusetion["answer5_count"]
                            else:
                                newanswer = qusetion["answer6_count"]
                            sum_score = int(
                                user_data[0]["score"]) + int(newanswer)

                            if answer not in user_data[0]["multiple_options"]:
                                # 添加複選答案
                                multiple_options = user_data[0]["multiple_options"] + answer
                            # 如果答案已經選過
                            else:
                                # 刪除複選答案
                                multiple_options = user_data[0]["multiple_options"].replace(
                                    answer, "")
                                sum_score = int(
                                    user_data[0]["score"]) - int(newanswer)
                            # 回傳已選擇的複選答案提示
                            myReply = "已選擇：" + multiple_options
                            # 暫存答案
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {
                                "status": "Life_stage1", "multiple_options": multiple_options, "score": str(sum_score)}}, upsert=True)
                        # 如果使用者點選確定
                        else:
                            # 紀錄選取答案
                            answer_record_life_stage = user_data[0]["answer_record_life_stage"] + \
                                "-" + question_number + ":" + \
                                user_data[0]["multiple_options"]
                            # 計算複選答案總分數
                            sub_score = 0

                            for i in range(len(user_data[0]["multiple_options"])):
                                sub_score += int(user_data[0]
                                                 ["multiple_options"][i])
                            # 添加複選答案總分數
                            sum_score = int(user_data[0]["score"]) + sub_score
                            # 如果當前題目不是最後一題
                            if qusetion["final_question"] != "1":
                                # 更換題目、紀錄答案及計算分數
                                dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"status": "Life_stage1", "question_number": str(
                                    int(question_number)+1), "answer_record_life_stage": answer_record_life_stage, "multiple_options": ""}}, upsert=True)
                                # 回傳適合性分析題目
                                myReply = Life_stage1(
                                    event.source.user_id).content()
                                line_bot_api.reply_message(
                                    event.reply_token,
                                    myReply
                                )
                                return
                            # 如果當前題目是最後一題
                            else:
                                # 進行最後一題總結
                                myReply = Life_stage_final_question(
                                    sum_score, answer_record_life_stage)

                # 如果使用者正在進行人生保險規劃 退休規劃
                elif user_data.count() != 0 and user_data[0]["status"] == "Life_stage2":
                    question_number = event.message.text.split(
                        ":")[1].split("-")[0]  # 題號
                    answer_number = event.message.text.split(
                        ":")[1].split("-")[1]  # 答案選項
                    check_data = {"question_number": question_number,
                                  "question_group": "Life_stage2"}
                    qusetion = dbQuestion.find_one(check_data)
                    if question_number == "1":
                        if answer_number == "1":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"age": "0-2", "life_stage2_type": "親親寶貝"}}, upsert=True)
                        if answer_number == "2":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"age": "3-21", "multiple_options": "1"}}, upsert=True)
                        if answer_number == "3":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"age": "22-30", "multiple_options": "1"}}, upsert=True)
                        if answer_number == "4":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"age": "28-35", "life_stage2_type": "成家立業"}}, upsert=True)
                        if answer_number == "5":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"age": "30-44", "life_stage2_type": "為人父母"}}, upsert=True)
                        if answer_number == "6":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"age": "45-65", "life_stage2_type": "開始退休規劃"}}, upsert=True)
                        if answer_number == "7":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"age": "66+", "life_stage2_type": "退休"}}, upsert=True)
                    if question_number == "2" and qusetion["final_question"] == "1":
                        check_data = {"user_id": event.source.user_id}
                        request_data = dbUserRequest.find_one(check_data)
                        if answer_number == "1":
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"gender": "男"}}, upsert=True)
                        else:
                            dbUserRequest.update_one({"user_id": event.source.user_id}, {
                                "$set": {"gender": "女"}}, upsert=True)
                        if request_data["age"] == "3-21":
                            myReply = Life_stage2.multiple_button()
                        elif request_data["age"] == "22-30":
                            myReply = Life_stage2.multiple_button2()
                        else:
                            check_data = {"user_id": event.source.user_id}
                            request_data = dbUserRequest.find_one(check_data)
                            check_data = {
                                "insurance_group": "life_stage1_result", "age": "年齡"+request_data["age"]+"歲"}
                            reply_data = dbInsurance.find_one(check_data)
                            myReply = ""
                            myReply += "選擇階段題目：" + \
                                request_data["life_stage2_type"]+'\n'
                            myReply += reply_data["guarantee_direction"]
                            check_data = {"user_id": event.source.user_id}
                            button_result = Life_stage1_result().result_button2(check_data, event)
                            line_bot_api.reply_message(
                                event.reply_token,
                                [TextSendMessage(text=myReply), FlexSendMessage(
                                    alt_text='險種按鈕', contents=button_result)]
                            )
                            return

                        line_bot_api.reply_message(
                            event.reply_token,
                            myReply
                        )
                        return
                    dbUserRequest.update_one({"user_id": event.source.user_id}, {"$set": {"question_number": str(
                        int(question_number)+1)}}, upsert=True)
                    myReply = Life_stage2(event.source.user_id).content()
                    line_bot_api.reply_message(
                        event.reply_token,
                        myReply
                    )
                    return

                else:
                    myReply = "尚未進行任何操作"
            else:
                # 模糊搜尋
                myReply_body_contents = []
                for words, map_func in word_mapping.items():
                    for single_word in words:
                        if single_word in event.message.text:
                            for single_func_name in map_func:
                                myReply_body_contents.append(
                                    ButtonComponent(
                                        action=MessageAction(
                                            label=single_func_name,
                                            text=single_func_name
                                        ),
                                        height="sm",
                                        style="primary",
                                        color="#FF000077",
                                        adjust_mode="shrink-to-fit"
                                    )
                                )
                            break
                if len(myReply_body_contents) == 0:
                    myReply_body_contents = [
                        ButtonComponent(
                            action=MessageAction(
                                label="功能列表",
                                text="功能列表",
                                displayText="功能列表"
                            ),
                            height="sm",
                            style="primary",
                            color="#FF000077",
                            adjust_mode="shrink-to-fit"
                        )
                    ]
                myReply = BubbleContainer(
                    header=BoxComponent(
                        layout="vertical",
                        contents=[
                            TextComponent(
                                text="推薦功能", size="xl", weight="bold"
                            )
                        ],
                        align_items="center"
                    ),
                    body=BoxComponent(
                        layout="vertical",
                        contents=myReply_body_contents,
                        spacing="md",
                        padding_start="md",
                        padding_end="md"
                    )
                )
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage("推薦功能", myReply)
                )
                return
        # 正在輸入退休財務規劃資料
        else:
            if typing_field == "asset":
                myReply = Joint_financial.content(
                    event.source.user_id, mode=joint_financial_question_mode, calculate=False, get_asset=True, data=event.message.text)
            else:
                myReply = Joint_financial.content(
                    event.source.user_id, mode=joint_financial_question_mode, data=event.message.text, mail=mail_object)
            line_bot_api.reply_message(
                event.reply_token,
                myReply
            )
            return None

        # 傳送訊息給使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=myReply)
        )
        return


@handler.add(PostbackEvent)
def handle_postback(event):
    postback_data = eval(event.postback.data)
    if postback_data['group'] == "Guarantee_gap":
        myReply = Guarantee_gap.content(event.source.user_id,
                                        postback_data=postback_data)
    elif postback_data['group'] == "Joint_financial":
        myReply = Joint_financial.content(event.source.user_id,
                                          mode=joint_financial_question_mode,
                                          data=postback_data,
                                          mail=mail_object)
    else:
        myReply = None

    if myReply is None:
        myReply = TextSendMessage(text="Error")

    line_bot_api.reply_message(
        event.reply_token,
        myReply
    )
    return None


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
