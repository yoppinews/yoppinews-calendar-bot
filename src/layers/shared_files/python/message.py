# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional


class TweetMessage:
    def __init__(self, status: str):
        self._status = status

    @staticmethod
    def of(d: dict) -> Optional[TweetMessage]:
        try:
            return TweetMessage(d['status'])
        except KeyError:
            return None

    @property
    def status(self):
        return self._status

    @property
    def dictionary(self) -> dict:
        return {
            'status': self._status,
        }
