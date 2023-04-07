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


    async def dlttcmd(self, message: Message):
        """TikTok video downloader"""
        chat = "@ttdowsbot"
        reply = await message.get_reply_message()
        
        async with message.client.conversation(chat) as conv:
        
            text = utils.get_args_raw(message)
            
            if reply:
                text = await message.get_reply_message()
                
            await message.edit("<b>Downloading...</b>")
            
            try:
                await conv.send_message(text)
                
                await sleep(4)
                
                r = await message.client.get_messages(chat, limit=1)

                if r[0].media is not None:
                    await message.client.send_file(
                        message.to_id, r[0].media, reply_to=reply
                    )

                    await message.delete()

                else:

                    await message.edit("<b>Failed to download video.</b>")

                await message.client.delete_dialog(chat)
                
            except YouBlockedUserError:
            
                await message.edit("<code>Разблокируй @ttdowsbot</code>")
                return
            
            
