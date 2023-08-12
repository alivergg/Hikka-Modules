# -*- coding: utf-8 -*-

# Module author: @alivergg

import io
import logging
import os
import uuid
import aiohttp
from bs4 import BeautifulSoup
import requests
from moviepy.editor import *

from telethon.tl.patched import Message

from telethon import events, functions
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class DownloaderTTMod(loader.Module):
    """
    Module for download tik-tok videos.
    
    .dltt {url} OR (reply to message)

    https://rapidapi.com/yi005/api/tiktok-download-without-watermark
    """

    strings = {"name": "TTDownloader"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "rapid-apikey",
                "",
                "X-RapidAPI-Key",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "caption",
                "",
                "Video caption",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "cut-sound",
                False,
                "Flag that indicates whether to cut the sound for the pictures count (only for tiktok with pictures)",
                validator=loader.validators.Boolean(),
            )
        )

    async def download(self, link: str):
        if link.startswith('<a'):
            soup = BeautifulSoup(link, 'html.parser')
            link = soup.get_text()

        url = "https://tiktok-download-without-watermark.p.rapidapi.com/analysis"

        headers = {
            "X-RapidAPI-Key": self.config["rapid-apikey"],
            'X-RapidAPI-Host': "tiktok-download-without-watermark.p.rapidapi.com"
        }

        querystring = {"url": link}

        async with aiohttp.ClientSession() as client:
            async with client.request('GET', url, headers=headers, params=querystring) as r:
                video_json = await r.json()

                return video_json
            

    async def send_video(self, message: Message, link: str, reply = None):
        video = await self.download(link)
        
        if video.get('msg', None) is None:
            return await message.edit(video['message'])
        
        if video['msg'] != 'success':
            return await message.edit(video['msg'])

        if video['data']['duration'] == 0:

            image_clips = []
            clips = []

            for image_url in video['data']['images']:
                response = requests.get(image_url)
                image_data = response.content

                image_path = f"image_{str(uuid.uuid4())}.jpg"
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                clips.append(ImageClip(image_path, duration=2))
                image_clips.append(image_path)


            response = requests.get(video['data']['play'])
            sound_data = response.content

            sound_path = f"sound_{str(uuid.uuid4())}.mp3"
            with open(sound_path, 'wb') as f:
                f.write(sound_data)

            audioclip = AudioFileClip(sound_path)

            final_clip = concatenate_videoclips(clips, method='compose')
            if self.config["cut-sound"] and audioclip.duration > final_clip.duration:
                audioclip.set_duration(final_clip.duration)

            final_clip = final_clip.set_audio(audioclip)
            output_file_path = f"video_{str(uuid.uuid4())}.mp4"
            final_clip.write_videofile(output_file_path, fps=24)

            await message.client.send_file(
                message.to_id,
                output_file_path,
                reply_to=reply,
                caption=self.config["caption"]
            )

            for i in image_clips:
                os.remove(i)
            os.remove(sound_path)
            os.remove(output_file_path)

        else:
            await message.client.send_file(
                message.to_id,
                video['data']['play'],
                reply_to=reply,
                supports_streaming=True,
                caption=self.config["caption"]
            )

        await message.delete()


    async def dlttcmd(self, message: Message):
        """TikTok video downloader"""
        reply = await message.get_reply_message()
        text = utils.get_args_raw(message)

        if reply:
            text = await message.get_reply_message()

        await message.edit("<b>Downloading...</b>")

        await self.send_video(message, text, reply)

        

    async def watcher(self, message: Message):
        try:
            me_id = (await message.client.get_me()).id
            if message.sender_id != me_id:
                return

            if len(message.text) < 10:
                return
        except:
            return

        if message.text.startswith('<a href="https://vm.tiktok.com/'):

            reply = await message.get_reply_message()
            await message.edit("<b>Downloading...</b>")
            await self.send_video(message, message.text, reply)
