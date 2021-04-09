from tqdm import tqdm
from pyrogram import Client
from config import *
from collections import namedtuple
import pandas as pd
import datetime
import matplotlib.pyplot as pl


Chat = namedtuple("chat", "chat_id name num")


def get_all_chats(dialogs) -> list[Chat]:
    """Get list of Chats (namedtuples). Takes list of dialogs got by app.get_dialogs()"""
    res = []
    for i, dialog in enumerate(dialogs):
        if dialog['chat']['type'] == "private":
            chat = Chat(dialog['chat']["id"], dialog['chat']['first_name'], i)
        elif dialog['chat']['type'] == "bot":
            chat = Chat(dialog['chat']["id"], dialog['chat']['username'], i)
        else:
            chat = Chat(dialog['chat']["id"], dialog['chat']['title'], i)
        res.append(chat)
    return res


def get_averaging_seconds(aver_type :int) -> int:
    """Get time duration in seconds. convert from type"""
    day = 60*60*24
    week = 7 * day
    month = 30 * day # TODO
    month3 = 3 * month
    if aver_type == 1:
        return day
    if aver_type == 2:
        return week
    if aver_type == 3:
        return month
    if aver_type == 4:
        return month3


with Client("my_account", api_id, api_hash) as app:
    user_name = app.get_me()["first_name"]
    print(f"Hello {user_name}. Select chat to analise:")
    dialogs_list = app.get_dialogs()
    chats = get_all_chats(dialogs_list)
    for i, chat in enumerate(chats):
        print(f"({chat.num}) {chat.name}")

    try:
        num = int(input("Input chat num please: "))
        selected_chat = chats[num]
    except IndexError:
        print("Number you have write is not correct")  # TODO

    print(f'There are {app.get_history_count(selected_chat.chat_id)} msgs in dialog!')
    messages = []
    for page in tqdm(range(0, app.get_history_count(selected_chat.chat_id)//100)):
        messages += app.get_history(chat_id=selected_chat.chat_id, limit=100, offset=page*100)
    message_dicts = []
    date_list = []
    a_time = get_averaging_seconds(2)
    for message in tqdm(messages):
        date_list.append(message["date"] // a_time)
        message_dict = dict(message)
        message_dicts.append(message_dict)

    df_1 = pd.DataFrame(message_dicts)
    df = pd.DataFrame(date_list)
    df = df.rename(columns={0: 'date'})
    df_1.to_csv("res1.csv")
    fig = pl.hist(df)
    pl.title('date')
    pl.xlabel("value")
    pl.ylabel("Frequency")
    pl.savefig("ExampleAnalise.png")
    print("All data will be saved to res.csv file.")