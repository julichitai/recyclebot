import config
import sqlite3
import telebot
from telebot import types

class UserInfo:
	user_location=types.Location(0,0)
	item=''
	city_id=0
	def __init__(self):
		self.list=[]
	def set_user_loc(self, loc):
		self.user_location=loc
		print("from class")
		print(self.user_location)

bot=telebot.TeleBot(config.token)
us=UserInfo()

@bot.message_handler(commands=['start'])
def handle_start(message):
    us.item=''
    ul=types.Location(0,0)
    us.user_location=ul
    keyboard = types.InlineKeyboardMarkup(3)
    callback_data=''
    callback_button1 = types.InlineKeyboardButton(text="Бумага", callback_data="paper")
    callback_button2 = types.InlineKeyboardButton(text="Стекло", callback_data="glass")
    callback_button3 = types.InlineKeyboardButton(text="Пластик", callback_data="plastic")
    callback_button4 = types.InlineKeyboardButton(text="Металл", callback_data="metall")
    callback_button5 = types.InlineKeyboardButton(text="Одежда", callback_data="clothes")
    callback_button6 = types.InlineKeyboardButton(text="Батарейки", callback_data="battery")
    callback_button7 = types.InlineKeyboardButton(text="Опасные отходы", callback_data="danger")
    callback_button8 = types.InlineKeyboardButton(text="Иное", callback_data="other")
    keyboard.add(callback_button1, callback_button2)
    keyboard.add(callback_button3, callback_button4)
    keyboard.add(callback_button5, callback_button6)
    keyboard.add(callback_button7, callback_button8)
    bot.send_message(message.chat.id, "Что хочешь сдать?", reply_markup=keyboard)
    kbitem=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    callbackbtn1=types.KeyboardButton(text='Закончить выбор')
    kbitem.add(callbackbtn1)
    bot.send_message(message.chat.id, "Нажмите \"Закончить выбор\", когда выберите необходимое", reply_markup=kbitem)
	
@bot.message_handler(commands=['help'])
def handler_help(message):
	bot.send_message(message.chat.id, "Этот бот поможет тебе найти ближайший пункт раздельного сбора отходов\n\nнабери /start для начала работы с ботом\n")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
	if call.message:
		if call.data=="again":
			handle_start(call.message)
		i=0
		while i<8:
			if call.data==config.callbackdata[i]:
				if us.item!='':
					us.item=us.item+", "+config.item[i]
				else:
					us.item=config.item[i]
			i+=1
		

def send(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    kb=types.InlineKeyboardMarkup()
    btn = types.KeyboardButton('Отправить мое местоположение', request_location=True)
    markup.add(btn)
    bot.send_message(message.chat.id, 'Отправьте мне свое местоположение', reply_markup=markup)    
    
@bot.message_handler(func=lambda message: True, content_types=["text"])
def handler_city(message):
    if message.text=="Закончить выбор":
        bot.send_message(message.chat.id, 'Ваш выбор: '+us.item)
        send(message)
    i=0
    while i<31:
        if message.text==config.city_name[i]:
            us.user_location=config.location[i]
            geo(message)
        i+=1
				
@bot.message_handler(content_types=['location'])
def handle_location(message):
	us.set_user_loc(message.location)
	print('долгота', us.user_location.longitude)
	print('широта', us.user_location.latitude)
	define_location(message,us.user_location)

def define_location(message,loc):
	i=0
	while i<31:
		if int(loc.latitude*100) in range (int(config.location[i].latitude*100-20), int(config.location[i].latitude*100+20)):
			if int(loc.longitude*100) in range (int(config.location[i].longitude*100-20), int(config.location[i].longitude*100+20)):
				us.city_id=i+1
				break;
		i+=1
	
	geo(message)

def geo(message):	
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM users')
    cur.execute('SELECT * FROM users')
    index=[]
    result=[]
    ff=False
    for row in cur:
        item=us.item
        itembd=row[4]
        s=item.split(', ')
        leng=len(s)
        i=0
        k=0
        while i<leng:
            if itembd.find(s[i])>-1:
                k+=1
                if k==leng:
                   index.append(row[0])
            else:
                break
            i+=1
        loc=types.Location(0,0)
        loc.lat=us.user_location.latitude
        loc.lon=us.user_location.longitude
        k=1
        f=False
        while k<100:
            if int(loc.lat*1000) in range(int(row[1]*1000-1*k), int(row[1]*1000+1*k)):
                if int(loc.lon*1000) in range(int(row[2]*1000-1*k), int(row[2]*1000+1*k)):
                    i=0
                    while i<len(index):
                        if index[i]==row[0]:
                           result.append(row[0])
                        i+=1
            if len(result)==0:
                k+=2
            else:
                ff=True
                break
        if ff:
            break		
    print(result)
    if result!=[]:
        printfind(message, result)
    else:
        bot.send_message(message.chat.id, "Вблизи вас пунктов сбора отходов не найдено")
        keyboard = types.InlineKeyboardMarkup()
        callbackbtn = types.InlineKeyboardButton(text="Начать", callback_data="again")
        keyboard.add(callbackbtn)
        bot.send_message(message.chat.id, "Начать поиск сначала?", reply_markup=keyboard)
        
		
def printfind(msg,ind):
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM users')
    cur.execute('SELECT * FROM users')
    bot.send_message(msg.chat.id, "Результаты:")
    for row in cur:
        leng=len(ind)
        i=0
        if ind[i]==row[0]:
            bot.send_location(msg.chat.id, row[1], row[2])
            bot.send_message(msg.chat.id, "Название: "+row[3]+ "\nДоп. информация: "+row[5])

    keyboard = types.InlineKeyboardMarkup()
    callbackbtn = types.InlineKeyboardButton(text="Начать", callback_data="again")
    keyboard.add(callbackbtn)
    bot.send_message(msg.chat.id, "Начать поиск сначала?", reply_markup=keyboard)
	
if __name__ == '__main__':
	bot.polling(none_stop=True)
	
