import os
import json
import aiogram
import aiohttp
import mimetypes
from aiogram import types
from datetime import datetime
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# get keys from env
bot_token=os.getenv("BOT_TOKEN")
rest_token=os.getenv("REST_TOKEN")
base_url=os.getenv("ENDPOINT")
# Create a new bot instance
bot = aiogram.Bot(token=str(bot_token))
dp = aiogram.Dispatcher(bot)

messages_types={"AUDIO":"audio","VOICE":"voice","FOTO":"foto"}
file_types={"audio":["mp3","flac","wav"],"voice":["ogg"],"foto":["jpg","jpeg","png","bmp","webp"]}

json_data = {
        "user": {
    "id": "ID1234567890",
    "lng": "uk"
  },
  "empai": {
    "employees_id": "default",
    "path": "empai.actions.correctiona1"
  },
  "answers": [
    {
      "type": "text",
      "answer": "веселе"
    },
        {
      "type": "text",
      "answer": "веселе"
    }
  ],
  "prompt": {
    "type": "voice",
    "message": ""
  }
}


async def save_and_send(id,type):
    file_path=await save_file_message(id)
    await send_file_to_rest_api(file_path,type)

# Handler for /start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Create a custom keyboard with a "Start Conversation" button
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton('Start Conversation')
    keyboard.add(start_button)
    # Send a welcome message with the custom keyboard
    await message.answer("Welcome to the chat bot! Click the button below to start a conversation.", reply_markup=keyboard)

# Image handler
@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_image(message: types.Message):
    # Get the image file ID
    image_file_id = message.photo[-1].file_id
    # Process the image file or perform any desired actions
    await save_and_send(image_file_id,messages_types["FOTO"])
    # Send a response
    await message.answer("Image file received and processed!")

# Handler for audio messages
@dp.message_handler(content_types=types.ContentTypes.AUDIO)
async def handle_audio(message: types.Message):
    # Get the audio file ID
    audio_file_id = message.audio.file_id
    # Process the audio file or perform any desired actions
    await save_and_send(audio_file_id,messages_types["AUDIO"])
    # Send a response
    await message.answer("Audio file received and processed!")

async def save_file_message(file_id):
    # Get the voice message file by its ID
    file = await bot.get_file(file_id) 
    # Download the voice message file
    file_path = file.file_path
    type=mimetypes.guess_type(file_path)
    ext=str(type).split('/')[1].split("'")[0]
    downloaded_file = await bot.download_file(file_path)
    # Define the directory to save the voice messages
    save_directory = "files" 
    # Create the directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)
    file_content=downloaded_file.read()
    # Generate the file name for saving
    file_name = f"{datetime.now()}.{ext}"
    # Save the voice message file to the directory
    save_path = os.path.join(save_directory, file_name)
    with open(save_path, 'wb') as file:
        file.write(file_content)
    return save_path


# async def send_to_rest_api(downloaded_file):
#     url = "https://api.empai.store/ai/openai/chat_completions"  # Replace with the actual URL of your REST API
#     headers = {
#             "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFwaSIsInBhc3N3b3JkIjoidGN4VnhNb1Q2VE5oSnNlbVZ1RzYifQ.mT0rKEd6qsxQdBy3bQXDnHvEG9P83ygoNAq658Jxw2I",
#         }
#     # Create the JSON payload   
#     # multipart/mixed
#     async with aiohttp.ClientSession() as session:
#         form_data = [
#         ('json_data', json.dumps(json_data))
#     ]
#         if downloaded_file is not None:
#                 with open(downloaded_file["path"], 'rb') as file:
#                     # file.append(open(__file__, 'rb'))
#                     tmp=file.read()
#                     form_data.append(('file_data', tmp))
#         async with session.post(url, data=form_data, headers=headers) as response:
#                 if response.status == 200:
#                     print("message sent to REST API successfully")
#                 else:
#                     print("Failed to send message to REST API")

async def send_file_to_rest_api(file_path='files/AleJazz!.mp3',type=None):
     # Replace with the actual URL of your REST API
    headers = {
            "Authorization": f"Bearer {rest_token}",
        }
    json_data["prompt"]["type"]=type
    async with aiohttp.ClientSession() as session:
        form_data=[("json_data",json.dumps(json_data)),('file_data',open(file_path, 'rb'))]
        print("form_data",form_data)
        try:
            async with session.post(base_url, data=form_data, headers=headers) as response:
                if response.status == 200:
                    data=await response.json()
                    print(data)
                    print("File sent successfully")
                else:
                    print("Failed to send file. Response status:", response.status)
        except aiohttp.ClientError as e:
            print("An error occurred:", str(e))

# Handler for voice messages
@dp.message_handler(content_types=types.ContentTypes.VOICE)
async def handle_voice(message: types.Message):
    # Get the voice file ID
    voice_file_id = message.voice.file_id 
    print(f"handle_voice:<<<<< {voice_file_id} >>>\n[MESSAGE]:{message}",)
     # Process the voice message or perform any desired actions
    await save_and_send(voice_file_id,messages_types["VOICE"])
    # Send a response
    await message.answer("Voice message received and processed!")

# Handler for text messages
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_text(message: types.Message):
    print(message)
    # Get the user's Telegram ID
    user_id = message.from_user.id 
    # Send an audio file to the user
    with open('files/AleJazz!.mp3', 'rb') as audio_file:
        await bot.send_audio(user_id, audio_file)
    # Wait for a reply
    await bot.send_message(user_id, "Please reply with an audio file or a voice message.")

# # Handler for audio file replies
# @dp.message_handler(content_types=types.ContentTypes.AUDIO)
# async def handle_reply_audio(message: types.Message):
#     # Get the audio file ID
#     audio_file_id = message.audio.file_id
#     # Process the reply audio file or perform any desired actions
#     # ...
#     # Send a response
#     await message.answer("Reply audio file received and processed!")

# Handler for voice message replies
# @dp.message_handler(content_types=types.ContentTypes.VOICE)
# async def handle_reply_voice(message: types.Message):
#     # Get the voice file ID
#     voice_file_id = message.voice.file_id
#     print(f"handle_reply_voice:<<<<< {voice_file_id} >>>\n[MESSAGE]:{message}",)
#     # Process the reply voice message or perform any desired actions
#     # ...
#     # Send a response
#     await message.answer("Reply voice message received and processed!")

# Start the bot
if __name__ == '__main__':
    aiogram.executor.start_polling(dp)