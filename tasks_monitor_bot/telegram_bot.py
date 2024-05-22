import subprocess
import asyncio
import os
import sys
import time
from telegram import Bot
from telegram.constants import ParseMode

# Read bot token and chat id from environment variables
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

# Ensure environment variables are set
if not bot_token or not chat_id:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")

# Initialize Bot
bot = Bot(token=bot_token)

async def send_telegram_message(message):
    """
    Sends a message to the specified Telegram chat.

    Args:
        message (str): The message to send.
    """
    await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)

async def main(script_type, command, task_name):
    """
    Executes a command as a subprocess and sends Telegram messages about its status.

    Args:
        script_type (str): The type of script to run ('shell' or 'python').
        command (str): The command to execute.
        task_name (str): The name of the task for messaging purposes.
    """
    # Record start time
    start_time = time.time()
    
    # Start subprocess
    if script_type == 'shell':
        process = subprocess.Popen(command, shell=True)
    else:
        process = subprocess.Popen([script_type, command])

    pid = process.pid
    await send_telegram_message(f"🚀 Started *{task_name}* task with PID `{pid}`")

    # Wait for subprocess to complete
    while process.poll() is None:
        await asyncio.sleep(1)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Check subprocess exit status
    if process.returncode == 0:
        await send_telegram_message(f"✅ *{task_name}* completed in {elapsed_time:.2f} seconds.")
    else:
        await send_telegram_message(f"⚠️ *{task_name}* was interrupted. Exit code: {process.returncode}")

def cli():
    """
    Command line interface entry point.
    Parses command line arguments and runs the main function.

    Usage:
        python telegram_bot.py <script_type> <task_name> <command>

    The <script_type> argument should be 'shell' or 'python'.
    The <task_name> argument is a descriptive name for the task.
    The <command> argument is the command to execute.
    """
    if len(sys.argv) != 4:
        print("Usage: python telegram_bot.py <script_type> <task_name> <command>")
        sys.exit(1)
    
    script_type = sys.argv[1]  # 'shell' or 'python'
    task_name = sys.argv[2]
    command = sys.argv[3]

    asyncio.run(main(script_type, command, task_name))

if __name__ == "__main__":
    cli()

