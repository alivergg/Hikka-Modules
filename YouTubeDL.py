import os
import glob
import subprocess

from telethon.tl.types import Message
from yt_dlp import YoutubeDL
import logging

from .. import loader, utils


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

    @loader.unrestricted
    async def ytcmd(self, message: Message):
        """[mp3] <ссылка> - Скачать видео с YouTube"""
        args = utils.get_args_raw(message)
        message = await utils.answer(message, self.strings("downloading"))

        ext = False
        if len(args.split()) > 1:
            ext, args = args.split(maxsplit=1)

        if not args:
            return await utils.answer(message, self.strings("args"))

        ydl_opts = {
            "outtmpl": "/tmp/%(title)s.%(ext)s",
            "writethumbnail": True,
        }

        if ext == "mp3":
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(args, download=True)
            except Exception:
                await utils.answer(message, self.strings("not_found"))
                return

            path = ydl.prepare_filename(info)

            if ext == "mp3":
                filename, ext = os.path.splitext(path)
                out = f"{filename}.mp3"
                subprocess.call(
                    ["ffmpeg", "-y", "-i", path, out],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )
                
                await self._client.send_file(message.peer_id, out)

            else:
                await self._client.send_file(message.peer_id, path)

            try:
                file_pattern = os.path.join("/tmp", filename + '.*')
                file_list = glob.glob(file_pattern)
                for file_path in file_list:
                    os.remove(file_path)
            except:
                pass

        if message.out:
            await message.delete()
