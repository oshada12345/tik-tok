import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pytube import YouTube


# Define your Telegram bot token
TOKEN = '6162835664:AAF82yhi5W7jJe8VJxeLTk10xKGCLWBn6Fk'

# Define the command handler for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the TikTok downloader bot!")

# Define the function to handle text messages
def handle_message(update, context):
    message_text = update.message.text
    
    # Check if the message text is a valid TikTok video URL
    if 'vt.tiktok.com' in message_text:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading TikTok video...")
        
        # Extract the TikTok video ID
        video_id = extract_video_id(message_text)
        
        if video_id:
            # Generate the direct download URL for the TikTok video
            video_url = generate_direct_download_url(video_id)
            
            # Download the TikTok video using requests library
            response = requests.get(video_url, stream=True)
            
            # Get the filename from the URL
            filename = f"{video_id}.mp4"
            
            # Save the video to a file
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            
            # Send the downloaded video file
            context.bot.send_video(chat_id=update.effective_chat.id, video=open(filename, 'rb'))
            
            # Remove the downloaded video file
            os.remove(filename)
            
            # Generate the direct download URL for the TikTok audio
            audio_url = generate_direct_audio_url(video_id)
            
            if audio_url:
                # Download the TikTok audio using pytube library
                audio_filename = f"{video_id}.mp3"
                YouTube(audio_url).streams.first().download(filename='audio', filename_prefix='')
                os.rename(audio_filename, audio_filename + '.mp3')
                
                # Send the downloaded audio file
                context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(audio_filename + '.mp3', 'rb'))
                
                # Remove the downloaded audio file
                os.remove(audio_filename + '.mp3')
            
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


# Define a helper function to generate the direct download URL for the TikTok video
def generate_direct_download_url(video_id):
    return f"https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={video_id}&vr_type=0&is_play_url=1&source=PackSourceEnum_PUBLISH"

# Define a helper function to generate the direct download URL for the TikTok audio
def generate_direct_audio_url(video_id):
    return f"https://api2-16-h2.musical.ly/aweme/v1/play/?video_id={video_id}&vr_type=0&is_play_url=1&source=PackSourceEnum_PUBLISH&download_type=3"

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
