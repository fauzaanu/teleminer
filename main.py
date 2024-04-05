import os
import time
from datetime import datetime

from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import User

load_dotenv()

api_id = os.getenv('TOKEN')
api_hash = os.getenv('API_HASH')

app = Client("teleminer", api_id, api_hash)


async def main():
    async with app:
        # Go through all the dialogs
        async for dialog in app.get_dialogs():
            print(f"Processing {dialog.chat.id}...")
            print(f"Chat type: {dialog.chat.type}")
            if dialog.chat.type != ChatType.PRIVATE:
                # For groups, supergroups, and channels, get members
                if dialog.chat.type in [ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP]:
                    print(f"Getting members for {dialog.chat.id}...")
                    async for member in dialog.chat.get_members():
                        user = member.user  # Correctly obtain the User object from ChatMember
                        if user:  # Ensure the user attribute is not None
                            await store_user_data(user)
                        else:
                            print(f"User is None in {dialog.chat.id}")
                else:
                    continue


async def store_user_data(user: User):
    # Define the base directory for storing user data
    base_dir = "user_data"

    # Create directories if they don't exist
    os.makedirs(base_dir, exist_ok=True)

    # Define the file paths
    avatar_path = os.path.join(base_dir, str(user.id), "avatars")
    log_file = os.path.join(base_dir, str(user.id), "log.txt")

    # Create the paths if they don't exist
    os.makedirs(os.path.dirname(avatar_path), exist_ok=True)

    # create the log file if it doesn't exist
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("")

    # Store the avatars
    async for photo in app.get_chat_photos(user.id):
        time.sleep(3)  # Sleep for a second to avoid rate limits
        avatar_file_name = avatar_path + f"/{photo.file_id}.jpg"
        await app.download_media(photo.file_id, avatar_file_name)
        print("saved avatar for", user.id)

    # Append user data to logs
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Timestamp: {timestamp}\n")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Username: {user.username}\n")
    with open(log_file, "a", encoding="utf-8") as f:
        chat = await app.get_chat(user.id)
        bio = chat.bio
        f.write(f"Bio: {bio}\n")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Phone: {user.phone_number}\n")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"Name: {user.first_name} {user.last_name}\n")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"=========================\n")


if __name__ == "__main__":
    app.run(main())
