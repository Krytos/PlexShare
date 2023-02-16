import logging
import os
from dataclasses import dataclass

from plexapi import exceptions
from plexapi.server import PlexServer

logger = logging.getLogger("uvicorn")

PLEX_TOKEN = os.getenv("PLEX_TOKEN")
PLEX_URL = "http://amber-direct.usbx.me:13675"

plex = PlexServer(PLEX_URL, PLEX_TOKEN)
users = plex.myPlexAccount().users()


async def update_plex_user(user: dataclass) -> dataclass:
	library_access = ["anime", "filme", "tv shows"]
	if user.email in [u.email for u in plex.myPlexAccount().users()]:
		user.plex_id = [u.id for u in plex.myPlexAccount().users() if u.email == user.email][0]
		if user.status == "active" or user.status == "trialing":
			plex.myPlexAccount().updateFriend(user.email, server=plex, allowSync=True, sections=library_access)
			logger.info(f"User {user.email} has been updated. Access to {library_access} granted.")
			return user
		else:
			try:
				plex.myPlexAccount().updateFriend(user.email, server=plex, sections=library_access, removeSections=True)
			except Exception as e:
				logger.info(e)
			logger.info(f"User {user.email} has been updated. Access to all libraries revoked.")
			try:
				plex.myPlexAccount().cancelInvite(user.email)
				logger.info(f"User {user.email} has been removed from pending invites.")
			except Exception as e:
				logger.info(e)
			return user
	elif user.email not in [u.email for u in plex.myPlexAccount().pendingInvites()]:
		if user.status == "active" or user.status == "trialing":
			try:
				plex.myPlexAccount().inviteFriend(user.email, server=plex, allowSync=True, sections=library_access)
				logger.info(f"User {user.email} has been invited. Access to {library_access} granted.")
			except exceptions.BadRequest:
				logger.info(f"User {user.email} has already been invited.")
			return user
		else:
			return user
	else:
		return user
