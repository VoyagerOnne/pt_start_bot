import os
from dotenv import load_dotenv
load_dotenv()
import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import psycopg2
from psycopg2 import sql

import re
import paramiko


TOKEN = os.getenv('TOKEN')
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')


def client_connect_and_execute(command, host=host, username=username, password=password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)

    stdin, stdout, stderr = client.exec_command(f'{command}')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data


logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def helpCommand(update: Update, context):
    help_text = """
        /help - for help\n
        /find_phone_number\n
        /find_email\n
        /verify_password\n
        /get_release\n
        /get_uname\n
        /get_uptime\n
        /get_df\n
        /get_free\n
        /get_mpstat\n
        /get_w\n
        /get_auths\n
        /get_critical\n
        /get_ps\n
        /get_ss\n
        /get_apt_list\n
        /get_services\n
        /get_repl_logs\n
        /get_emails\n
        /get_phone_numbers\n
    """
    update.message.reply_text(help_text)


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END


def findPhoneNumbersCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findPhoneNumbers (update: Update, context: CallbackContext):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'((\+7|8)[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})')
    phoneNumberL = phoneNumRegex.findall(user_input)

    if not phoneNumberL:
        update.message.reply_text('Телефонные номера не найдены')
        return

    phoneNumbers = ''
    for i in range(len(phoneNumberL)):
        phoneNumbers += f'{i+1}. {phoneNumberL[i][0]}\n'

    context.user_data['phones'] = phoneNumberL
    update.message.reply_text(phoneNumbers)
    update.message.reply_text('Даете ли вы согласие на сохранение найденных номеров? (введите "y"): ')
    return 'confirmSavePassword'


def confirmSavePassword(update: Update, context: CallbackContext):
    user_input = update.message.text
    phoneNumberL = context.user_data.get('phones', [])

    if user_input.lower() == 'y':
        try:
            for phone in phoneNumberL:
                try:
                    connection = psycopg2.connect(
                        host=DB_HOST,
                        database=DB_DATABASE,
                        user=DB_USER,
                        password=DB_PASSWORD
                    )
                    cursor = connection.cursor()
                    cursor.execute(f"INSERT INTO phone_numbers (phone) VALUES (\'{phone[0]}\');")
                    update.message.reply_text('Все номера успешно сохранены')
                except Exception as e:
                    update.message.reply_text(f'Извините, произошла ошибка при подключении к серверу :(\n{e}')
                finally:
                    if connection:
                        cursor.close()
                        connection.close()
        except Exception as e:
            update.message.reply_text(f'Во время сохранения произошла ошибка: {e}')
    else:
        update.message.reply_text('Сохранение отменено.')
    return ConversationHandler.END


def findEmailCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите текст для поиска электронной почты: ')
    return 'findEmail'

def findEmail(update: Update, context: CallbackContext):
    user_input = update.message.text
    EmailRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    EmailL = EmailRegex.findall(user_input)

    if not EmailL:
        update.message.reply_text('Электронная почта не найдены')
        return

    Emails = ''
    for i in range(len(EmailL)):
        Emails += f'{i+1}. {EmailL[i]}\n'

    context.user_data['emails'] = EmailL
    update.message.reply_text(Emails)
    update.message.reply_text('Даете ли вы согласие на сохранение найденных почт? (введите "y"): ')

    return 'confirmSaveEmail'


def confirmSaveEmail(update: Update, context: CallbackContext):
    user_input = update.message.text
    EmailL = context.user_data.get('emails', [])

    if user_input.lower() == 'y':
        try:
            for email in EmailL:
                try:
                    connection = psycopg2.connect(
                        host=DB_HOST,
                        database=DB_DATABASE,
                        user=DB_USER,
                        password=DB_PASSWORD
                    )
                    cursor = connection.cursor()
                    cursor.execute(f"INSERT INTO emails (email) VALUES (\'{email}\');")
                    update.message.reply_text('Все почты успешно сохранены')
                except Exception as e:
                    update.message.reply_text(f'Извините, произошла ошибка при подключении к серверу :(\n{e}')
                finally:
                    if connection:
                        cursor.close()
                        connection.close()

        except Exception as e:
            update.message.reply_text(f'Во время сохранения произошла ошибка: {e}')
    else:
        update.message.reply_text('Сохранение отменено.')
    return ConversationHandler.END


def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите ваш пароль: ')
    return 'verifyPassword'

def verifyPassword(update: Update, context):
    user_input = update.message.text
    PassRegex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+{}\[\]:;"\'<>,.?/~`\\|]).{8,}$')
    PassM = PassRegex.match(user_input)

    if PassM:
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END


def get_release(update: Update, context):
    update.message.reply_text('информации о релизе: ')
    try:
        update.message.reply_text(client_connect_and_execute('cat /etc/os-release'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_uname(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('uname -a'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_uptime(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('uptime'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_df(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('df -h'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_free(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('free -h'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_mpstat(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('mpstat'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_w(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('w'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_auths(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('last -n 10'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_critical(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('journalctl -p crit -n 5'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_ps(update: Update, context):
    try:
        text = client_connect_and_execute('ps aux')
        n = 3000
        parts = [text[i:i+n] for i in range(0, len(text), n)]
        for i in parts:
            update.message.reply_text(i)
    except Exception as e:
        update.message.reply_text(f'Извините, произошла ошибка при подключении к серверу :(\n{e}')
    return ConversationHandler.END


def get_ss(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('ss -tuln'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END



def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите имя пакета или all, чтобы найти все: ')
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text
    try:
        if user_input != 'all':
            update.message.reply_text(client_connect_and_execute(f'apt list --installed | grep {user_input}'))
        else:
            update.message.reply_text(client_connect_and_execute('apt list --installed'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_services(update: Update, context):
    try:
        update.message.reply_text(client_connect_and_execute('systemctl list-units --type=service --state=running'))
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_repl_logs(update: Update, context):
    try:
        log = client_connect_and_execute('cat /var/log/postgresql/postgresql-16-main.log').split('\n')
        update.message.reply_text('Последние 20 логов')
        for i in log[-20:]:
            update.message.reply_text(i)
    except Exception as e:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(', e)
    return ConversationHandler.END


def get_emails(update: Update, context):
    try:
        try:
            connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_DATABASE,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = connection.cursor()
            cursor.execute("select * from emails;")
            result = cursor.fetchall()
            update.message.reply_text(f'{result}')
        except Exception as e:
            update.message.reply_text(f'Извините, произошла ошибка при подключении к серверу :(\n{e}')
        finally:
            if connection:
                cursor.close()
                connection.close()
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def get_phone_numbers(update: Update, context):
    try:
        try:
            connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_DATABASE,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = connection.cursor()
            cursor.execute("select * from phone_numbers;")
            result = cursor.fetchall()
            update.message.reply_text(f'{result}')
        except Exception as e:
            update.message.reply_text(f'Извините, произошла ошибка при подключении к серверу :(\n{e}')
        finally:
            if connection:
                cursor.close()
                connection.close()
    except:
        update.message.reply_text('Извините, произошла ошибка при подключении к серверу :(')
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'confirmSavePassword': [MessageHandler(Filters.text, confirmSavePassword)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'confirmSaveEmail': [MessageHandler(Filters.text & ~Filters.command, confirmSaveEmail)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )
    convHandlerGetRelease= ConversationHandler(
        entry_points=[CommandHandler('get_release', get_release)],
        states={
            'get_release': [MessageHandler(Filters.text & ~Filters.command, get_release)],
        },
        fallbacks=[]
    )
    convHandlerGetUname = ConversationHandler(
        entry_points=[CommandHandler('get_uname', get_uname)],
        states={
            'get_uname': [MessageHandler(Filters.text & ~Filters.command, get_uname)],
        },
        fallbacks=[]
    )
    convHandlerGetUptime= ConversationHandler(
        entry_points=[CommandHandler('get_uptime', get_uptime)],
        states={
            'get_uptime': [MessageHandler(Filters.text & ~Filters.command, get_uptime)],
        },
        fallbacks=[]
    )
    convHandlerGetDf= ConversationHandler(
        entry_points=[CommandHandler('get_df', get_df)],
        states={
            'get_df': [MessageHandler(Filters.text & ~Filters.command, get_df)],
        },
        fallbacks=[]
    )
    convHandlerGetFree= ConversationHandler(
        entry_points=[CommandHandler('get_free', get_free)],
        states={
            'get_free': [MessageHandler(Filters.text & ~Filters.command, get_free)],
        },
        fallbacks=[]
    )
    convHandlerGetMpStat= ConversationHandler(
        entry_points=[CommandHandler('get_mpstat', get_mpstat)],
        states={
            'get_mpstat': [MessageHandler(Filters.text & ~Filters.command, get_mpstat)],
        },
        fallbacks=[]
    )
    convHandlerGetW= ConversationHandler(
        entry_points=[CommandHandler('get_w', get_w)],
        states={
            'get_w': [MessageHandler(Filters.text & ~Filters.command, get_w)],
        },
        fallbacks=[]
    )
    convHandlerGetAuth= ConversationHandler(
        entry_points=[CommandHandler('get_auths', get_auths)],
        states={
            'get_auths': [MessageHandler(Filters.text & ~Filters.command, get_auths)],
        },
        fallbacks=[]
    )
    convHandlerGetCritical = ConversationHandler(
        entry_points=[CommandHandler('get_critical', get_critical)],
        states={
            'get_critical': [MessageHandler(Filters.text & ~Filters.command, get_critical)],
        },
        fallbacks=[]
    )
    convHandlerGetPs= ConversationHandler(
        entry_points=[CommandHandler('get_ps', get_ps)],
        states={
            'get_ps': [MessageHandler(Filters.text & ~Filters.command, get_ps)],
        },
        fallbacks=[]
    )
    convHandlerGetSs= ConversationHandler(
        entry_points=[CommandHandler('get_ss', get_ss)],
        states={
            'get_ss': [MessageHandler(Filters.text & ~Filters.command, get_ss)],
        },
        fallbacks=[]
    )
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
    convHandlerGetService= ConversationHandler(
        entry_points=[CommandHandler('get_services', get_services)],
        states={
            'get_services': [MessageHandler(Filters.text & ~Filters.command, get_services)],
        },
        fallbacks=[]
    )
    convHandlerGetReplLog= ConversationHandler(
        entry_points=[CommandHandler('get_repl_logs', get_repl_logs)],
        states={
            'get_repl_logs': [MessageHandler(Filters.text & ~Filters.command, get_repl_logs)],
        },
        fallbacks=[]
    )
    convHandlerGetEmails = ConversationHandler(
        entry_points=[CommandHandler('get_emails', get_emails)],
        states={
            'get_emails': [MessageHandler(Filters.text & ~Filters.command, get_emails)],
        },
        fallbacks=[]
    )
    convHandlerGetPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('get_phone_numbers', get_phone_numbers)],
        states={
            'get_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, get_phone_numbers)],
        },
        fallbacks=[]
    )


    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerGetRelease)
    dp.add_handler(convHandlerGetUptime)
    dp.add_handler(convHandlerGetUname)
    dp.add_handler(convHandlerGetDf)
    dp.add_handler(convHandlerGetFree)
    dp.add_handler(convHandlerGetMpStat)
    dp.add_handler(convHandlerGetW)
    dp.add_handler(convHandlerGetAuth)
    dp.add_handler(convHandlerGetCritical)
    dp.add_handler(convHandlerGetPs)
    dp.add_handler(convHandlerGetSs)
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(convHandlerGetService)
    dp.add_handler(convHandlerGetReplLog)
    dp.add_handler(convHandlerGetEmails)
    dp.add_handler(convHandlerGetPhoneNumbers)


    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()