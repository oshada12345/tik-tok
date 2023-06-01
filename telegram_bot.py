import os
import re
import requests
from telegram import InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pytube import YouTube
from pytube.exceptions import PytubeError
from moviepy.editor import VideoFileClip


# Define your Telegram bot token
TOKEN = '6162835664:AAF82yhi5W7jJe8VJxeLTk10xKGCLWBn6Fk'


# Define the command handler for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the TikTok downloader bot! Send me a TikTok video URL to download.")


# Define the function to handle text messages
def handle_message(update, context):
    message_text = update.message.text

    # Check if the message text is a valid TikTok video URL
    if 'vt.tiktok.com' in message_text:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading TikTok video...")

        # Extract the TikTok video ID
        video_id = extract_video_id(message_text)

        if video_id:
            try:
                # Create a YouTube object using the TikTok video URL
                tiktok_url = f"https://www.tiktok.com/@_/{video_id}"
                youtube = YouTube(tiktok_url)

                # Get the highest resolution video stream
                video_stream = youtube.streams.get_highest_resolution()

                # Download the video
                video_filename = f"{video_id}.mp4"
                video_stream.download(output_path=".", filename=video_filename)

                # Get the video duration using moviepy
                video = VideoFileClip(video_filename)
                video_duration = video.duration
                video.close()

                # Send the downloaded video file
                context.bot.send_chat_action(chat_id=update.effective_chat.id, action="UPLOAD_VIDEO")
                context.bot.send_video(chat_id=update.effective_chat.id, video=InputFile(video_filename), duration=int(video_duration), supports_streaming=True)

                # Remove the downloaded video file
                os.remove(video_filename)

            except PytubeError:
                # Send an error message if there's an issue with downloading the video
                context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to download TikTok video.")

        else:
            # Send an error message if the video ID cannot be extracted
            context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to extract TikTok video ID.")

    else:
        # Send an error message if the message is not a valid TikTok URL
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid TikTok video URL.")


# Define a helper function to extract the TikTok video ID from the URL
def extract_video_id(url):
    match = re.search(r'vt\.tiktok\.com\/(.+?)\/', url)
    if match:
        return match.group(1)
    return None


# Create an instance of the Updater class and pass it the Telegram bot token
updater = Updater(token=TOKEN, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Register the command handlers
dispatcher.add_handler(CommandHandler("start", start))

# Register the message handler
dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

# Start the bot
updater.start_polling()
