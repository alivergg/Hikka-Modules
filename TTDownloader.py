# -*- coding: utf-8 -*-

# Module author: @alivergg

import io
import logging
import os
from asyncio import sleep

from telethon.tl.patched import Message

from telethon import events, functions
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl

from .. import loader, utils


@loader.tds
class DownloadeTTMod(loader.Module):
    """
    Module for downdoad tik-tok videos.
    
    .dltt {url} OR (reply to message)
    """

    strings = {"name": "TTDownloader"}
    
    async def get_video(self, url: str, message):
        chat = "@ttk_downloader_bot"
        async with message.client.conversation(chat) as conv:
            await conv.send_message(url)
            r = await conv.get_response()
            
            if r.media is not None:
                return r.media
                
            return


    async def dlttcmd(self, message: Message):
        """TikTok video downloader"""
        reply = await message.get_reply_message()
        text = utils.get_args_raw(message)
        
        if reply:
            text = await message.get_reply_message()
            
        await message.edit("<b>Downloading...</b>")
            
        try:
            video = await self.get_video(text, message)
            
            if video:
                await message.client.send_file(
                    message.to_id, video, reply_to=reply
                )
                await message.delete()

            else:

                await message.edit("<b>Failed to download video.</b>")

            await message.client.delete_dialog(chat)
            
        except YouBlockedUserError:
        
            await message.edit("<code>Разблокируй @ttk_downloader_bot</code>")
            return
                
                
    async def watcher(self, message):
        try:
            me_id = (await message.client.get_me()).id
            if message.sender_id != me_id:
                return
                
            chat = await message.client.get_entity(message.to_id)
            if chat.id == 5401383549:
                return
                
            if len(message.text) < 3:
                return
        except:
            return
            
        if message.text.startswith('<a href="https://vm.tiktok.com/'):
            reply = await message.get_reply_message()
            await message.edit("<b>Downloading...</b>")
            
            try:
                video = await self.get_video(message.text, message)
                
                if video:
                    await message.client.send_file(
                        message.to_id, video, reply_to=reply
                    )
                    await message.delete()

                else:

                    await message.edit("<b>Failed to download video.</b>")

                await message.client.delete_dialog(chat)
                
            except YouBlockedUserError:
            
                await message.edit("<code>Разблокируй @ttk_downloader_bot</code>")
                return
