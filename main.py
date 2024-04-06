import os
import shutil
import time
from datetime import datetime

from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import User

load_dotenv()

api_id = os.getenv('TOKEN')
api_hash = os.getenv('API_HASH')

app = Client("teleminer", api_id, api_hash)


async def main(skip_existing=True):
    try:
        async with app:
            # Go through all the dialogs
            async for dialog in app.get_dialogs():
                print(f"Processing {dialog.chat.id}...")
                print(f"Chat type: {dialog.chat.type}")
                if dialog.chat.type != ChatType.PRIVATE:

                    # For groups, supergroups, and channels, get members
                    if dialog.chat.type in [ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP]:
                        print(f"Getting members for {dialog.chat.id}...")

                        try:
                            async for member in dialog.chat.get_members():
                                user = member.user
                                if user:

                                    # Skip user data if it already exists (default) - Overwrite by setting
                                    # skip_existing=False
                                    if os.path.exists(f"user_data/{user.id}") and skip_existing:
                                        print(f"Skipping {user.id} as data already exists...")
                                        continue

                                    await store_user_data(user)
                                else:
                                    print(f"User is None in {dialog.chat.id}")
                        except Exception as e:
                            print(f"Error: {e}")
                            # todo: Exceptions should be explicitly handled : currently monitoring all errors that
                            #  happen 1. pyrogram.errors.exceptions.bad_request_400.ChatAdminRequired:
                            continue

                    else:
                        continue
    except FloodWait as e:
        error_text = str(e)
        # pyrogram.errors.exceptions.flood_420.FloodWait: Telegram says: [420 FLOOD_WAIT_X] - A wait of 2546 seconds
        # is required (caused by "auth.ExportAuthorization")
        wait_time = error_text.find("seconds") - 1
        wait_time = int(error_text[error_text.find("of") + 3:wait_time])
        print(f"Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        await app.stop()
        app.run(main())


async def store_user_data(user: User):
    has_avatar = False

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
        has_avatar = True
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

    if has_avatar:
        # users who have avatars are additionally stored in a separate folder called user_data_avatars
        os.makedirs("user_data_avatars", exist_ok=True)

        # copy the entire user directory to user_data_avatars
        shutil.copytree(os.path.join(base_dir, str(user.id)), os.path.join("user_data_avatars", str(user.id)))

    if user.phone_number:
        # users with phone numbers are stored in a separate file called phone_numbers.txt with a ref to the user id
        print(f"User {user.id} has a phone number: {user.phone_number}")
        with open("phone_numbers.txt", "a", encoding="utf-8") as f:
            f.write(f"{user.id}: {user.phone_number} : {user.first_name} : {user.last_name}\n")


if __name__ == "__main__":
    app.run(main())
