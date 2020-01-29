import os
import tempfile

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings


class UserService:
    @classmethod
    def generate_user_avatar(cls, name) -> str:
        """
        :param name: The intials to create icon from
        :return: filepath to icon created in temp folder.
        """

        ipath = os.path.join(tempfile.gettempdir(), f"{name}.png")

        # creating icon using pillow module
        W, H = 120, 120
        img = Image.new("RGB", (W, H), color="grey")
        d = ImageDraw.Draw(img)
        path = os.path.join(settings.STATIC_ROOT, "fonts", "PrimetimeRegular-vOL9.ttf")
        fnt = ImageFont.truetype(path, 70)
        w, h = d.textsize(name, font=fnt)
        d.text(
            ((W - w) / 2, ((H - h) / 2) - 5),
            name,
            align="center",
            font=fnt,
            fill=(255, 255, 255),
        )
        img.save(ipath)

        return ipath
