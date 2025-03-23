import paramiko
import io
from telethon.tl.custom import Button
from telethon import TelegramClient, events

class JSONr:
    def __init__(self, file_path="settings.json"):
        import json
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                settings = json.load(file)
                self.API_ID = settings["API_ID"]
                self.API_HASH = settings["API_HASH"]
                self.BOT_TOKEN = settings["BOT_TOKEN"]
        except:
            pass

    def reset(self):
        if self.__init__() : return True

settings = JSONr()

class RSA:
    @staticmethod
    def parse_key(pkey):
        try : 
            return io.StringIO(pkey)
        except :
            return False
    
class SSH(RSA):
    def __init__(self, ip, username, password=False, port=22, pkey=False):
        self.ip = ip
        self.username = username
        if pkey != False : 
            self.password = pkey
            self.pkey = pkey
        else : 
            self.pkey = pkey
            self.password = password

        self.port = port

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.pkey != False : 
            self.pkey = paramiko.RSAKey(file_obj=self.parse_key(self.pkey))
            self.client.connect(self.ip, self.port, self.username, pkey = self.pkey)
            return True
        else : 
            self.client.connect(self.ip, self.port, self.username, self.password)
            return True
        return False
    
    def command(self,command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return [stdin, stdout.read().decode(), stderr.read().decode()]
    
    def reset(self, *args, **kwargs):
        return self.__init__(args,kwargs)


token = settings.BOT_TOKEN
api_id = settings.API_ID
api_hash = settings.API_HASH
bot = TelegramClient('STS', api_id, api_hash).start(bot_token=token)
data = {}

@bot.on(events.NewMessage(pattern=r"^/connect\s+(\S+)\s+(\S+)\s+([\s\S]+)"))
async def connect_command(event):
    ip_port, username, password = event.pattern_match.groups()
    try : 
        ip = ip_port.split(':')[0]
        port = ip_port.split(":")[1]
    except IndexError:
        ip = ip_port ; port = 22
    if "-----END RSA PRIVATE KEY-----" in password : 
        ssh = SSH(ip = ip, port=port, username=username, pkey = password)
        if ssh.connect():
            data[event.sender_id] = ssh
            await event.reply(f"<$> Now your account is at session {username}@{ip}")
        else : 
            await event.reply("<!> Probably wrong password or login info <!>")
    else : 
        ssh = SSH(ip = ip, port=port, username=username, password = password)
        if ssh.connect():
            data[event.sender_id] = ssh
            await event.reply(f"<$> Now your account is at session {username}@{ip}")
        else : 
            await event.reply("<!> Probably wrong password or login info <!>")

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(
    "Welcome",
    buttons=[[Button.url("Developer's usesrname", url="https://t.me/RadiatedSmith")]])

@bot.on(events.NewMessage(pattern="(?i)^/help$"))
async def help_command(event):
    help_text = """
**Bot Commands:**

/start - Start the bot
/help - Show this help message
/connect - ip:port username password(or pkey)
/disconnect - to disconnect the shell

@RadiatedSmith
"""
    await event.reply(help_text)

@bot.on(events.NewMessage)
async def handle_commands(event):
    user_id = event.sender_id
    message = event.text.strip()
    if message == "/disconnect" : 
        del data[user_id]
        await event.reply("<!> Just disconnected from the current session <!>")
        return
    try : 
        await event.reply(data[user_id].command(message)[1])
    except :
        return



bot.run_until_disconnected()
