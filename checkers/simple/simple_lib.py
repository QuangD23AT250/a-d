from typing import NamedTuple, List, Optional

import requests
from checklib import *

PORT = 2112

class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{self.port}/api'

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.port = PORT

    def register(self, session: requests.Session, username: str, password: str, status: Status):
        resp = session.post(f"{self.url}/register", json={
            "username": username,
            "password": password,
            })

        resp = self.c.get_json(resp, "invalid response on register", status)
        self.c.assert_eq(type(resp), dict, "invalid response on register", status)
        if resp.get("status") != "success":
            self.c.cquit(status, f"could not register: {resp.get('message', '')}")
        self.c.assert_eq(type(resp.get("message")), dict, "invalid response on register", status)
        token = resp["message"].get("token")
        self.c.assert_eq(type(token), str, "invalid response on register", status)

        session.headers["Authorization"] = f"Bearer {token}"


    def login(self, session: requests.Session, username: str, password: str, status: Status):
        resp = session.post(f"{self.url}/login", json={
            "username": username,
            "password": password,
            })

        resp = self.c.get_json(resp, "invalid response on login", status)
        self.c.assert_eq(type(resp), dict, "invalid response on login", status)
        if resp.get("status") != "success":
            self.c.cquit(status, f"could not login: {resp.get('message', '')}")
        self.c.assert_eq(type(resp.get("message")), dict, "invalid response on login", status)
        token = resp["message"].get("token")
        self.c.assert_eq(type(token), str, "invalid response on login", status)

        session.headers["Authorization"] = f"Bearer {token}"

    def put_note(self, session: requests.Session, text: str, status: Status) -> str:
        resp = session.put(f"{self.url}/note", json={
            "text": text,
            })

        resp = self.c.get_json(resp, "invalid response on put note", status)
        self.c.assert_eq(type(resp), dict, "invalid response on put note", status)
        if resp.get("status") != "success":
            self.c.cquit(status, f"could not put note: {resp.get('message', '')}")
        self.c.assert_eq(type(resp.get("message")), dict, "invalid response on put note", status)
        uid = resp["message"].get("id")
        self.c.assert_eq(type(uid), str, "invalid response on put note", status)

        return uid


    def get_note(self, session: requests.Session, note_id: str, status: Status) -> str:
        resp = session.get(f"{self.url}/note/{note_id}")

        resp = self.c.get_json(resp, "invalid response on get note", status)
        self.c.assert_eq(type(resp), dict, "invalid response on get note", status)
        if resp.get("status") != "success":
            self.c.cquit(status, f"could not get note: {resp.get('message', '')}")
        self.c.assert_eq(type(resp.get("message")), dict, "invalid response on get note", status)
        text = resp["message"].get("text")
        self.c.assert_eq(type(text), str, "invalid response on get note", status)

        return text

    def list_notes(self, session: requests.Session, status: Status) -> List[str]:
        resp = session.get(f"{self.url}/notes")

        resp = self.c.get_json(resp, "invalid response on list notes", status)
        self.c.assert_eq(type(resp), dict, "invalid response on list notes", status)
        if resp.get("status") != "success":
            self.c.cquit(status, f"could not list notes: {resp.get('message', '')}")

        self.c.assert_eq(type(resp.get("message")), list, "invalid response on list notes", status)
        notes = resp["message"]
        for note_id in notes:
            self.c.assert_eq(type(note_id), str, "invalid response on list notes", status)

        return notes

