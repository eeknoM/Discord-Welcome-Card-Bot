import discord
from discord.ext import commands
import requests
from PIL import Image, ImageDraw, ImageFont
import glob
from io import BytesIO
import os
import logging
import json

# load JSON
with open('config.json') as config_file:
    config = json.load(config_file)

logging.basicConfig(level=logging.INFO)

# setup vars
resize_size = (124, 124)
border_size = 3
frame_duration = 53
output_gif = 'imagedraw.gif'
target_width, target_height = 1000, 430
fallback_channel_id = config['fallback_channel_id']
font_path = os.path.join(os.path.dirname(__file__), config['welcome_font'])
font_size = 40
role_id = config['role_id']


# get the users avatar
def fetch_and_prepare_avatar(url, resize_size):
    try:
        response = requests.get(url)
        response.raise_for_status()
        user_img = Image.open(BytesIO(response.content)).convert('RGBA')
        user_img = user_img.resize(resize_size)
        return user_img
    except Exception as e:
        logging.error(f"Error fetching avatar: {e}")
        return None

# create a circular mask for the avatar
def create_circular_image(image, border_size):
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.width, image.height), fill=255)
    
    circular_img = Image.new('RGBA', image.size)
    circular_img.paste(image, (0, 0), mask=mask)
    
    bordered_size = (image.width + 2 * border_size, image.height + 2 * border_size)
    bordered_img = Image.new('RGBA', bordered_size, (255, 255, 255, 0))
    border_mask = Image.new('L', bordered_size, 0)
    border_draw = ImageDraw.Draw(border_mask)
    border_draw.ellipse((border_size, border_size, image.width + border_size, image.height + border_size), fill=255)
    border_draw.ellipse((0, 0, bordered_size[0], bordered_size[1]), outline=255, width=border_size)
    bordered_img.paste(circular_img, (border_size, border_size), mask=mask)
    bordered_img.putalpha(border_mask)
    
    return bordered_img

# draw the welcome text over the image frames
def draw_text_on_image(image, text, font_path, font_size, position):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = (position[0] - text_width // 2, position[1] - text_height // 2)
    draw.text(text_position, text, font=font, fill=(255, 255, 255, 255))

# prepare the gif
def process_gif_frames(dir_path, target_width, target_height, bordered_img, frame_duration, output_gif, welcome_text):
    images = []
    for item in glob.glob(os.path.join(dir_path, "ImageFrames", "*.gif")):
        im = Image.open(item).convert('RGBA')
        im = im.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        x_center = im.width // 2
        y_center = im.height // 2
        x_user_center = bordered_img.width // 2
        y_user_center = bordered_img.height // 2
        im.paste(bordered_img, (x_center - x_user_center, y_center - y_user_center - 70), bordered_img)
        
        draw_text_on_image(im, welcome_text, font_path, font_size, (x_center, y_center + 50))
        
        images.append(im)

    if images:
        images[0].save(output_gif, save_all=True, append_images=images[1:], optimize=False, duration=frame_duration, loop=0)
        logging.info(f"Animated GIF saved as '{output_gif}'.")
    else:
        logging.warning("No images to save.")

async def handle_member_join(member, bot):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    user_img = fetch_and_prepare_avatar(avatar_url, resize_size)
    if user_img:
        bordered_img = create_circular_image(user_img, border_size)
        welcome_text = f"Welcome to {member.guild.name} @{member.name}"
        process_gif_frames(dir_path, target_width, target_height, bordered_img, frame_duration, output_gif, welcome_text)

        with open(output_gif, 'rb') as f:
            gif = discord.File(f)
            welcome_message = f"Welcome to the server, {member.mention}!"

            if member.guild.system_channel is not None:
                await member.guild.system_channel.send(welcome_message, file=gif)
            else:
                fallback_channel = member.guild.get_channel(fallback_channel_id)
                if fallback_channel is not None:
                    await fallback_channel.send(welcome_message, file=gif)
                else:
                    logging.error("No suitable channel found to send the welcome message.")

        try:
            os.remove(output_gif)
            logging.info(f"Deleted temporary file '{output_gif}'.")
        except OSError as e:
            logging.error(f"Error deleting file {output_gif}: {e}")

    role = member.guild.get_role(role_id)
    if role is not None:
        await member.add_roles(role)
    else:
        logging.error(f"Role with ID {role_id} not found.")

def setup_welcomer(bot):
    @bot.event
    async def on_member_join(member):
        await handle_member_join(member, bot)
