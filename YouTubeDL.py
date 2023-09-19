import os
import glob
import subprocess

from telethon.tl.types import Message
from pytube import YouTube
from moviepy.editor import *
import logging
import ssl

from .. import loader, utils


ssl._create_default_https_context = ssl._create_stdlib_context
VIDEO_SAVE_DIRECTORY = "./videos"
AUDIO_SAVE_DIRECTORY = "./audio"


@loader.tds
class YouTubeMod(loader.Module):
    """Download YouTube video and music"""

    strings = {
        "name": "YouTube",
        "args": "🎞 <b>You need to specify a link</b>",
        "downloading": "🎞 <b>Downloading...</b>",
        "not_found": "🎞 <b>Video not found...</b>",
    }

    strings_ru = {
        "args": "🎞 <b>Укажите ссылку на видео</b>",
        "downloading": "🎞 <b>Скачиваю...</b>",
        "not_found": "🎞 <b>Видео не найдено...</b>",
        "_cmd_doc_yt": "[mp3] <ссылка> - Скачать видео YouTube",
        "_cls_doc": "Скачать YouTube видео",
    }

    @staticmethod
    def _mp4_to_mp3(mp4, mp3):
        fileconv = AudioFileClip(mp4)
        fileconv.write_audiofile(mp3)
        fileconv.close()

    @loader.unrestricted
    async def ytcmd(self, message: Message):
        """[mp3] <ссылка> - Скачать видео с YouTube"""
        args = utils.get_args_raw(message)
        message = await utils.answer(message, self.strings["downloading"])

        ext = False
        if len(args.split()) > 1:
            ext, args = args.split(maxsplit=1)

        if not args:
            return await utils.answer(message, self.strings["args"])

        video = YouTube(args, use_oauth=True)
        try:
            if ext == "mp3":
                path = (video.streams.filter(only_audio=True).first().download(AUDIO_SAVE_DIRECTORY))

                audio_path = AUDIO_SAVE_DIRECTORY + '/' + video.title + '.mp3'
                self._mp4_to_mp3(path, audio_path)

                await self._client.send_file(message.peer_id, audio_path)
                os.remove(path)
                os.remove(audio_path)
            else:
                path = (video.streams.filter(progressive=True, file_extension='mp4').
                        order_by('resolution').desc().first().download(VIDEO_SAVE_DIRECTORY))

                await self._client.send_file(message.peer_id, path, supports_streaming=True)
                os.remove(path)

        except Exception as ex:
            logging.error(ex)
            await utils.answer(message, self.strings["not_found"])
            return

        if message.out:
            await message.delete()
