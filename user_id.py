# -*- coding: utf-8 -*-

# Module author: @alivergg
from .. import loader, utils


@loader.tds
class UserID(loader.Module):
    """Узнать TelegramID"""

    strings = {"name": "UserID Telegram"}

    async def useridcmd(self, message):
        """Команда .userid <@ или реплай> показывает ID выбранного пользователя."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        try:
            if args:
                user = await message.client.get_entity(
                    args if not args.isdigit() else int(args)
                )
            else:
                user = await message.client.get_entity(reply.sender_id)
        except ValueError:
            user = await message.client.get_entity(message.sender_id)

         keyboard = [
                {
                    "text": "🚫 Close",
                    "callback": self.inline__close,
                }
        ]

        await self.inline.form(
            text=f"<b>Имя:</b> <code>{user.first_name}</code>\n"
            f"<b>ID:</b> <code>{user.id}</code>",
            message=message,
            reply_markup=keyboard,
        )
