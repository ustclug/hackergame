from django.conf import settings

import requests

from server.context import Context
from .models import Challenge
from server.user.interface import User

import secrets
from typing import Optional


# Spec: https://github.com/iBug/podzol#api-reference
# ContainerInfo:
# type ContainerInfo struct {
#     // Container name, ID, reverse proxy hostname
#     Name     string    `json:"name"`
#     ID       string    `json:"id"`
#     Hostname string    `json:"hostname"`

#     // When the container will expire, in Unix timestamp
#     Deadline time.Time `json:"deadline"`
# }
class PodZol:
    def __init__(self):
        self.podzol_manager = settings.PODZOL_MANAGER
        self.podzol_revproxy = settings.PODZOL_REVPROXY

    # POST /create -> ContainerInfo
    def create(self, context: Context, challenge: Challenge) -> dict:
        user = context.user
        token = User.get(context, user.pk).token
        challenge_name = challenge.name
        hostname = secrets.token_urlsafe(16)
        lifetime = challenge.podzol_lifetime
        if lifetime is None:
            lifetime = 3600  # Set 1hr by default
        r = requests.post(
            f"{self.podzol_manager}/create",
            json={
                "user": user.pk,
                "token": token,
                "appname": challenge_name,
                "hostname": hostname,
                "image": challenge.podzol_image_name,
                "lifetime": lifetime,
            },
            timeout=15,
        )
        return r.json()

    # GET /list?opts= -> ContainerInfo[]
    def get(self, context: Context, challenge: Challenge) -> Optional[dict]:
        user = context.user
        challenge_name = challenge.name
        r = requests.get(
            f"{self.podzol_manager}/list",
            params={
                "user": user.pk,
                "app": challenge_name,
            },
            timeout=15,
        )
        r = r.json()
        if not r:
            return None
        assert len(r) <= 1
        return r[0]

    # POST /remove -> None
    def remove(self, context: Context, challenge: Challenge) -> None:
        user = context.user
        challenge_name = challenge.name
        r = requests.post(
            f"{self.podzol_manager}/remove",
            json={
                "user": user.pk,
                "app": challenge_name,
            },
            timeout=15,
        )
