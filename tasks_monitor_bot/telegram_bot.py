import subprocess
import asyncio
import os
import sys
import time
import argparse
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

async def main(script_type, task_name, command):
    """
    Executes a command as a subprocess and sends Telegram messages about its status.

    Args:
        script_type (str): The type of script to run ('shell' or 'python').
        task_name (str): The name of the task for messaging purposes.
        command (list): The command to execute as a list of arguments.
    """
    # Record start time
    start_time = time.time()
    
    # Start subprocess
    if script_type == 'shell':
        process = subprocess.Popen(command, shell=True)
    else:
        process = subprocess.Popen(['python'] + command)

    pid = process.pid
    await send_telegram_message(f"🚀 Started *{task_name}* task with PID `{pid}`")

    # Wait for subprocess to complete
    while process.poll() is None:
        await asyncio.sleep(1)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Convert elapsed time to hh:mm:ss format
    elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

    # Check subprocess exit status
    if process.returncode == 0:
        await send_telegram_message(f"✅ *{task_name}* completed in {elapsed_time_str}.")
    else:
        await send_telegram_message(f"⚠️ *{task_name}* was interrupted. Exit code: {process.returncode}")

def cli():
    """
    Command line interface entry point.
    Parses command line arguments and runs the main function.

    Usage:
        task-monitor -p <task_name> <python_script> [<args>...]
        task-monitor -s <task_name> <shell_command> [<args>...]

    The -p argument is for running a Python script.
    The -s argument is for running a shell command.
    The <task_name> argument is a descriptive name for the task.
    The <command> argument is the command to execute, followed by any arguments.
    """
    parser = argparse.ArgumentParser(description="Run tasks and send status messages to Telegram.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p', '--python', nargs='+', metavar=('task_name', 'python_script'), help='Run a Python script')
    group.add_argument('-s', '--shell', nargs='+', metavar=('task_name', 'shell_command'), help='Run a shell command')

    args = parser.parse_args()

    if args.python:
        script_type = 'python'
        task_name = args.python[0]
        command = args.python[1:]
    elif args.shell:
        script_type = 'shell'
        task_name = args.shell[0]
        command = ' '.join(args.shell[1:])

    asyncio.run(main(script_type, task_name, command))

if __name__ == "__main__":
    cli()
