import os
from copy import deepcopy
from email.mime.image import MIMEImage

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template.context import make_context
from django.template.loader import get_template


class BaseEmailMessage(mail.EmailMultiAlternatives):
    _node_map = {"subject": "subject", "text_body": "body", "html_body": "html"}
    template_name = None

    def __init__(
            self,
            request=None,
            context=None,
            template_name=None,
            images=None,
            mime_images=None,
            files=None,
            *args,
            **kwargs
    ):
        super(BaseEmailMessage, self).__init__(*args, **kwargs)

        self.request = request
        self.context = {} if context is None else context
        self.html = None

        if template_name is not None:
            self.template_name = template_name
        self.images = images
        self.mime_images = mime_images
        self.files = files

    def get_context_data(self):
        context = deepcopy(self.context)
        if self.request:
            site = get_current_site(self.request)
            domain = context.get("domain") or (
                    getattr(settings, "DOMAIN", "") or site.domain
            )
            protocol = context.get("protocol") or (
                "https" if self.request.is_secure() else "http"
            )
            site_name = context.get("site_name") or (
                    getattr(settings, "SITE_NAME", "") or site.name
            )
            user = context.get("user") or self.request.user
        else:
            domain = context.get("domain") or getattr(settings, "DOMAIN", "")
            protocol = context.get("protocol") or "http"
            site_name = context.get("site_name") or getattr(settings, "SITE_NAME", "")
            user = context.get("user")

        context.update(
            {
                "domain": domain,
                "protocol": protocol,
                "site_name": site_name,
                "user": user,
            }
        )
        return context

    def render(self):
        context = make_context(self.get_context_data(), request=self.request)
        template = get_template(self.template_name)
        with context.bind_template(template.template):
            for node in template.template.nodelist:
                self._process_node(node, context)
        self._attach_body()
        self._add_images()
        self._attach_files()

    def send(self, to, cc=None, bcc=None, *args, **kwargs):
        self.render()
        self.to = to
        if cc:
            self.cc = cc
        if bcc:
            self.bcc = bcc
        super(BaseEmailMessage, self).send(*args, **kwargs)

    def _process_node(self, node, context):
        attr = self._node_map.get(getattr(node, "name", ""))
        if attr is not None:
            setattr(self, attr, node.render(context).strip())

    def _attach_body(self):
        if self.body and self.html:
            self.attach_alternative(self.html, "text/html")
        elif self.html:
            self.body = self.html
            self.content_subtype = "html"

    def _add_images(self):
        static_root = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        )
        if self.images:
            for filename, file_id in self.images:
                image_path = os.path.join(
                    static_root, settings.EMAIL_IMAGE_DIR, filename
                )
                image_file = open(image_path, "rb")
                msg_image = MIMEImage(image_file.read())
                image_file.close()
                msg_image.add_header("Content-ID", "<%s>" % file_id)
                self.attach(msg_image)

        if self.mime_images:
            for image in self.mime_images:
                self.attach(image)

    def _attach_files(self):
        if self.files:
            for file_name, file_path in self.files:
                with open(file_path, "rb") as attachment:
                    self.attach(file_name, content=attachment.read())
