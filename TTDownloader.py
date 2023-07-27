# -*- coding: utf-8 -*-

# Module author: @alivergg

import logging
from asyncio import sleep
import aiohttp
from bs4 import BeautifulSoup

from telethon.tl.patched import Message

from telethon import events, functions
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl

from .. import loader, utils


logger = logging.getLogger(__name__)

@loader.tds
class DownloadeTTMod(loader.Module):
    """
    Module for downdoad tik-tok videos.
    
    .dltt {url} OR (reply to message)
    """

    strings = {"name": "TTDownloader"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "rapidapikey",
                "",
                "X-RapidAPI-Key",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "caption",
                "",
                "Video caption",
                validator=loader.validators.String(),
            )
        )

    async def download(self, link):
        soup = BeautifulSoup(link, 'html.parser')
        link = soup.get_text()

        url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"

        headers = {
            "X-RapidAPI-Key": self.config["rapidapikey"],
            "X-RapidAPI-Host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
        }

        querystring = {"url": link}
        
        async with aiohttp.ClientSession() as client:
            async with client.request('GET', url, headers=headers, params=querystring) as r:
                video_json = await r.json()
                
                try:

                    if isinstance(video_json, list):
                        video_json = video_json[0]
                
                    return video_json['video'][0]
                
                except:

                    return video_json


    async def dlttcmd(self, message: Message):
        """TikTok video downloader"""
        reply = await message.get_reply_message()
        text = utils.get_args_raw(message)
        
        if reply:
            text = await message.get_reply_message()

        if self.config["rapidapikey"] == '':
            return await message.edit("<b>RapidAPI-Key not found! Get it on https://rapidapi.com/maatootz/api/tiktok-downloader-download-tiktok-videos-without-watermark</b>")
            
        await message.edit("<b>Downloading...</b>")
            
        try:
            video = await self.download(text)
            
            if video:

                await message.client.send_file(
                    message.to_id, 
                    video, 
                    reply_to=reply,
                    supports_streaming=True,
                    caption=self.config["caption"]
                )
                
                await message.delete()

            else:

                if not video.startswith('http'):
                    await message.edit(video)
                else:
                    await message.edit("<b>Failed to download video.</b>")
            
        except Exception as ex:
                
            logging.info(ex)
            await message.edit("<code>Р</code>")
            return
                
                
    async def watcher(self, message):
        try:
            me_id = (await message.client.get_me()).id
            if message.sender_id != me_id:
                return
                
            if len(message.text) < 5:
                return
        except:
            return
            
        if message.text.startswith('<a href="https://vm.tiktok.com/'):
            if self.config["rapidapikey"] == '':
                return await message.edit("<b>RapidAPI-Key not found! Get it on https://rapidapi.com/maatootz/api/tiktok-downloader-download-tiktok-videos-without-watermark</b>")
        
            reply = await message.get_reply_message()
            await message.edit("<b>Downloading...</b>")
            
            try:
                video = await self.download(message.text)
                
                if video:
                    
                    await message.client.send_file(
                        message.to_id, 
                        video, 
                        reply_to=reply,
                        supports_streaming=True,
                        caption=self.config["caption"]
                    )
                    
                    await message.delete()

                else:

                    if not video.startswith('http'):
                        await message.edit(video)
                    else:
                        await message.edit("<b>Failed to download video.</b>")
            except:
                await message.edit("<b>Failed to download video.</b>")
                    
  
