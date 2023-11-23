from datetime import datetime, timezone
import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
import os
import pickle


admin_id = #Your numerical id as an int
channel_id = #Your numerical channel id as an int

msg_list_fname = 'msg_li'
posts_list_fname = 'posts_li'
r_msg_list_fname = 'r_msg_li'
signid = '——————————————————\n📚@Channel_id -- 🤖@bot_id_Bot'

bot_token = #your bot token that you've recived from botfather

bot = telebot.TeleBot(token=bot_token)

connection = sqlite3.connect('main.db', check_same_thread=False)
crsr = connection.cursor()
connection.commit()

#openning some files to restore information (if bot has stopped before)

global msg_list
msg_list = []
try:
    with open(msg_list_fname,'rb') as f:
        msg_list = pickle.load(f)
except:
    pass

global posts_list
posts_list = []
try:
    with open(posts_list_fname,'rb') as fh:
        posts_list = pickle.load(fh)
except:
    pass


global r_msg_list
r_msg_list = []
try:
    with open(r_msg_list_fname,'rb') as ff:
        r_msg_list = pickle.load(ff)
except:
    pass

#defining some buttons

def btns(x = 1):
    if x == 1:
        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton(text='Accept', callback_data='Accept'),
               InlineKeyboardButton(text='Reject', callback_data='Reject'))
    elif x == 2:
        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton(text='حذف آگهی', callback_data='Change'))
    elif x == 3:
        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton(text='Accept', callback_data='rAccept'),
               InlineKeyboardButton(text='Reject', callback_data='rReject'))
    elif x == 4:
        markup = InlineKeyboardMarkup()

        markup.add(InlineKeyboardButton(text='حذف آگهی', callback_data='rChange'))
    return markup

#message handlers

@bot.message_handler(commands=['Start','start'])
def send_welcome(message):

    #because of bot functionality every user must have a username so here bot doesn't run if they don't have one
    
    if message.from_user.username == None:
        mm = bot.send_message(message.from_user.id,'❌برای استفاده از روبات، نام کاربری تلگرام خود را فعال کنید. برای این کار به تنظیمات (settings) رفته و بر روی گزینه تعریف نام کاربری (set a username) بزنید و یک نام کاربری برای خود تعریف کنید.')
        bot.register_next_step_handler(mm, send_welcome)

    else:

        bot.reply_to(message, 'سلام✋🏻\n🤖به روبات Ketaab خوش اومدی!\n✅برای ثبت کتاب از دستور \n/Insert\n✅و برای ثبت درخواست یک کتاب یا جزوه، دستور\n/Require\nرو انتخاب کنید.\n❗️توجه کنید که آیدی تلگرام شما زیر پست درخواستتان در کانال قرار خواهد گرفت و درصورت فشردن دکمه (حذف آگهی) که در انتهای ثبت درخواستتان، توسط روبات برای شما ارسال میشود، آیدی شما از کانال حذف خواهد شد.\n‼️همچنین قبل از استفاده از روبات توجه کنید که این روبات و کانال مذکور و سازنده آنها هیچ مسئولیتی نسبت به اطلاعات آگهی های ثبت شده ندارند و صرفا یک راه ارتباطی را فراهم کرده اند و نه بیشتر!!!')

        #getting user info

        tel_id = int(message.from_user.id)
        username = str(message.from_user.username)
        name = str(message.from_user.first_name) +' '+ str(message.from_user.last_name)
        first_use = datetime.now(timezone.utc).strftime('%B %d, %Y %I:%M%p')#a date format

        #see if user exists in our database

        params = (tel_id, username, name, first_use)
        user_exists = crsr.execute('SELECT id FROM users WHERE tel_id = ?;',(tel_id,)).fetchall()

        #if the user is new, add him in database

        if user_exists == []:
            crsr.execute('INSERT INTO users (tel_id, username, name, first_use) VALUES (?, ?, ?, ?);', params)
            connection.commit()



@bot.message_handler(commands=['Insert','insert'])
def book_info(message):
    
    m = bot.send_message(message.from_user.id, '📖لطفا نام کتاب رو برام بفرست\n /Cancel')
    
    bot.register_next_step_handler(m,handle_book_name)
    
def handle_book_name(message):
    if str(message.text) == '/Cancel' or str(message.text) == '/cancel': #handels Cancel operation
        bot.send_message(message.chat.id,'Canceled!')
    else:
        global book_name
        book_name = str(message.text) #get the book name

        #sending the next message

        m = bot.send_message(message.from_user.id, '💵 لطفا قیمت کتاب رو برام بفرست\n❕قیمت باید فقط عدد باشه مثلا واسه بیست هزار تومان بفرست: ۲۰\n❕اگه میخوای کتاب رو رایگان بدی به کسی، عدد صفر رو بفرست: ۰\n /Cancel')
    
        #calling next handler

        bot.register_next_step_handler(m,handle_book_price)


def handle_book_price(message):
    if str(message.text) == '/Cancel' or str(message.text) == '/cancel':
        bot.send_message(message.chat.id,'Canceled!')
    else:
        
        #trying to get just a number from user

        try:
            global book_price
            book_price = int(message.text)
            fff = ''
        except:
            fff = bot.send_message(message.chat.id,'لطفا فقط عدد بفرست:')
            bot.register_next_step_handler(fff,handle_book_price)

        #if we,ve got a number from user we go to next step

        if fff == '':

            m = bot.send_message(message.from_user.id, '❇️لطفا توضیح کوتاهی راجع به کتاب بده یا اگه نکته ای هست بنویس \n /Cancel')
        
            bot.register_next_step_handler(m,handle_book_description)

def handle_book_description(message):
    if str(message.text) == '/Cancel' or str(message.text) == '/cancel':
        bot.send_message(message.chat.id,'Canceled!')
    else:
        global book_description
        book_description = str(message.text)

        m = bot.send_message(message.from_user.id, '📷لطفا یه عکس از کتاب بفرست\n /Cancel')

        bot.register_next_step_handler(m, handle_book_picture)
    
def handle_book_picture(message):
    if str(message.text) == '/Cancel' or str(message.text) == '/cancel':
        bot.send_message(message.chat.id,'Canceled!')
    else:
        #triying to get picture from telegram server
        try:
            file_info = bot.get_file(message.photo[3].file_id)
            book_picture = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
            picture = open(f'{message.id}', 'wb').write(book_picture.content)
            picture = open(f'{message.id}', 'rb')
            ttt = ''
        except:
            ttt = bot.send_message(message.chat.id,'‼️خطایی رخ داد، لطفا از داخل اپلیکیشن تلگرام یه عکس از کتاب بگیر و بفرست( از بخش سنجاق 📎همین کنار و سپس گزینه دوربین 📷)')
            bot.register_next_step_handler(ttt,handle_book_picture)
            
        if ttt == '': #inserting data into database
            crsr.execute('INSERT INTO books (user_id, name, description, price, photo) VALUES (?, ?, ?, ?, ?);',(message.from_user.id, book_name, book_description, book_price, str(message.id)))
            connection.commit()

            bot.send_message(message.from_user.id,'کتاب شما ثبت شد و بزودی در کانال قرار خواهد گرفت. ✅')

            if message.from_user.username != None:
                if book_price == 0:
                    text_msg = '\n'+'#فروشی'+'\n\n'+f'📖{book_name}' + '\n' + f'📄{book_description}' + '\n' + '💵قیمت: رایگان!' +'\n🆔@'+ str(message.from_user.username)+'\n'+signid
                else:
                    text_msg = '\n'+'#فروشی'+'\n\n'+f'📖{book_name}' + '\n' + f'📄{book_description}' + '\n' + f'💵قیمت: {str(book_price)} هزار تومان' +'\n🆔@'+ str(message.from_user.username)+'\n'+signid
            else:
                text_msg = book_name + '\n' + book_description + '\n' + 'قیمت: ' + str(book_price)

            #sending the order to admin to see if he accepts the order
            m = bot.send_photo(admin_id, picture, text_msg + '\n' + str(message.id), reply_markup=btns())
            

            user = message.from_user

            sender_info = ('Tel ID: ' + str(user.id) + '\nName: ' + str(user.first_name) +
                ' ' + str(user.last_name) +
                '\nUsername: ' + str(user.username))

            bot.reply_to(m,sender_info) #sending user info as an replied message to admin

            #save message to a file to preventing data losing
            msg_list.append(message)
            with open(msg_list_fname,'wb') as f:
                pickle.dump(msg_list, f)


@bot.message_handler(commands=['Require','require'])
def r_book_info(message):
    
    m = bot.send_message(message.from_user.id, '📖لطفا نام کتاب یا جزوه درخواستی رو برام بفرست(بهتره از کلمات جزوه یا کتاب استفاده کنی که مشخص بشه چی میخوای)\n /Cancel')
    
    bot.register_next_step_handler(m,r_handle_book_name)
    
def r_handle_book_name(message):
    if str(message.text) == '/Cancel' or str(message.text) == '/cancel':
        bot.send_message(message.chat.id,'Canceled!')
    else:
        global r_book_name
        r_book_name = str(message.text)

        m = bot.send_message(message.from_user.id, '📄لطفا توضیحاتی راجع به کتاب یا جزوه ای که میخوای برام بفرست (مثلا چه ویرایشی، چه مترجمی و یا چیزای دیگه…)\n /Cancel')
    
        bot.register_next_step_handler(m, r_handle_book_description)

def r_handle_book_description(message):
    if str(message.text) == '/Cancel' or str(message.text) == '/cancel':
        bot.send_message(message.chat.id,'Canceled!')
    else:
        global r_book_description
        r_book_description = str(message.text)
        
        bot.send_message(message.from_user.id,'سفارش شما ثبت شد و بزودی در کانال قرار خواهد گرفت. ✅')

        if message.from_user.username != None:
           
            r_text_msg = '#درخواستی'+'\n\n'+f'📖{r_book_name}' + '\n' + f'📄{r_book_description}' + '\n🆔@'+ str(message.from_user.username)+'\n'+signid
        else:
            r_text_msg = r_book_name + '\n' + r_book_description 

        m = bot.send_message(admin_id, r_text_msg + '\n' + str(message.id), reply_markup=btns(3))#sending the order to admin for acceptance

        user = message.from_user

        r_sender_info = ('Tel ID: ' + str(user.id) + '\nName: ' + str(user.first_name) +
            ' ' + str(user.last_name) +
            '\nUsername: ' + str(user.username))

        bot.reply_to(m,r_sender_info)#Replying user info to the previous message which was sent to admin for Acceptance

        r_msg_list.append(message)
        with open(r_msg_list_fname,'wb') as ff:
            pickle.dump(r_msg_list, ff)


@bot.message_handler()
def all_handler(message):
    bot.send_message(message.from_user.id,'✅برای ثبت کتاب از دستور \n/Insert\n✅و برای ثبت درخواست یک کتاب یا جزوه، دستور\n/Require\nرو انتخاب کنید.')
    
#Button handler
@bot.callback_query_handler(func=lambda message: True)
def call_back_query(inlnbtn):
    if inlnbtn.from_user.id == admin_id:

        if inlnbtn.data == 'Accept':#If the admin accepts the order, the Bot will send the order to the channel and 
                                    #replies a message to the user with a button that says: your order has been published in the channel. 
                                    #The user can click the button whenever their order is done to remove it from the channel.

            t = str(inlnbtn.message.caption)
            msg_id = t.rsplit('\n', 1)[1]#getting the order ID.
            t = t.rsplit('\n', 1)[0]#removing the order ID from the message's text to send it to the channel.

            picture = open(f'{msg_id}', 'rb')
            
            l = bot.send_photo(channel_id, picture, t)

            crsr.execute('UPDATE books SET status = "Avalable" WHERE (photo) = (?);',(str(msg_id),))#updating the database
            connection.commit()
            

            for i in msg_list:
                if i.id == int(msg_id):
                    bot.reply_to(i, '✅کتاب در کانال:\n@ChannelID\nمنتشر شد.\nهرگاه کتاب را فروختید دکمه زیر را بزنید.'+'\n'+str(msg_id),reply_markup = btns(2))

                    posts_list.append([i.from_user.id,l,msg_id])
                    with open(posts_list_fname,'wb') as fh:
                        pickle.dump(posts_list, fh)
                    
                    msg_list.remove(i)
                    with open(msg_list_fname,'wb') as f:
                        pickle.dump(msg_list, f)
                    break

            bot.edit_message_reply_markup(inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id,reply_markup=None)#removing message buttons(Accept and Reject)
            bot.edit_message_caption(str(t + '\n' + 'Accepted!'),inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id)#Editing message

            if os.path.exists(f'{msg_id}'):#removing photo from our system (Server)
                os.remove(f'{msg_id}')

        elif inlnbtn.data == 'Reject':#The function is similar to the one mentioned before, but this time it's about the items that were rejected.
                                      #There are some variations in this task as compared to the previous one.

            t = str(inlnbtn.message.caption)
            msg_id = t.rsplit('\n', 1)[1]
            t = t.rsplit('\n', 1)[0]

            crsr.execute('UPDATE books SET status = "Rejected" WHERE (photo) = (?);',(str(msg_id),))
            connection.commit()

            bot.edit_message_reply_markup(inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id,reply_markup=None)
            bot.edit_message_caption(str(t + '\n' + 'Rejected!'),inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id)

            if os.path.exists(f'{msg_id}'):
                os.remove(f'{msg_id}')
            
            for i in msg_list:
                if i.id == int(msg_id):
                    
                    msg_list.remove(i)
                    with open(msg_list_fname,'wb') as f:
                        pickle.dump(msg_list, f)
                    break
        #Same as above, but here for the other type of the orders.
        if inlnbtn.data == 'rAccept':

            j = str(inlnbtn.message.text)
            msg_id = j.rsplit('\n', 1)[1]
            j = j.rsplit('\n', 1)[0]

            l = bot.send_message(channel_id,j)

            for i in r_msg_list:
                if i.id == int(msg_id):
                    bot.reply_to(i, '✅درخواست شما در کانال:\n@ChannelID\nمنتشر شد.\nهرگاه کتاب را خریدید یا جزوه را گرفتید، دکمه زیر را بزنید.'+'\n'+str(msg_id),reply_markup = btns(4))

                    posts_list.append([i.from_user.id,l,msg_id])
                    with open(posts_list_fname,'wb') as fh:
                        pickle.dump(posts_list, fh)
                    
                    r_msg_list.remove(i)
                    with open(r_msg_list_fname,'wb') as f:
                        pickle.dump(r_msg_list, f)
                    break

            bot.edit_message_reply_markup(inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id,reply_markup=None)
            bot.edit_message_text(str(j + '\n' + 'Accepted!'),inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id)
            
        elif inlnbtn.data == 'rReject':
            j = str(inlnbtn.message.text)
            msg_id = j.rsplit('\n', 1)[1]
            j = j.rsplit('\n', 1)[0]

            bot.edit_message_reply_markup(inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id,reply_markup=None)
            bot.edit_message_text(str(j + '\n' + 'Rejected!'),inlnbtn.from_user.id,inlnbtn.message.id,inlnbtn.id)

            for i in r_msg_list:
                if i.id == int(msg_id):
                    
                    r_msg_list.remove(i)
                    with open(r_msg_list_fname,'wb') as f:
                        pickle.dump(r_msg_list, f)
                    break


    if inlnbtn.data == 'Change':#Handling the button sent to the user that indicates their order has been completed.
        
        mID = str(inlnbtn.message.text).rsplit('\n',1)[1]
        
        for i in posts_list:
            
            if int(i[2]) == int(mID):
                
                new_caption = str(i[1].caption).rsplit('\n',3)[0]
                new_caption = new_caption + '\n' + '🛑این کتاب به فروش رفت!' + '\n' + signid
                bot.edit_message_caption(new_caption,i[1].chat.id,i[1].id,inlnbtn.id)
                bot.delete_message(inlnbtn.message.chat.id,inlnbtn.message.id)
                posts_list.remove(i)
                with open(posts_list_fname,'wb') as fh:
                        pickle.dump(posts_list, fh)
                crsr.execute('UPDATE books SET status = "Sold" WHERE (photo) = (?);',(str(mID),))
                connection.commit()
                break

    if inlnbtn.data == 'rChange':#Same as above, but here for the other type of the orders.
        mID = str(inlnbtn.message.text).rsplit('\n',1)[1]
        
        for i in posts_list:
            
            if int(i[2]) == int(mID):
                
                new_text = str(i[1].text).rsplit('\n',3)[0] 
                new_text = new_text + '\n' + '🛑این آگهی انجام شد!' + '\n'+ signid
                bot.edit_message_text(new_text,i[1].chat.id,i[1].id,inlnbtn.id)
                bot.delete_message(inlnbtn.message.chat.id,inlnbtn.message.id)
                posts_list.remove(i)
                with open(posts_list_fname,'wb') as fh:
                        pickle.dump(posts_list, fh)
                break
        

bot.infinity_polling()
