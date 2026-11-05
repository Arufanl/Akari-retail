"""Quote a DM only when several unanswered messages make its target ambiguous."""
from collections import OrderedDict


class AdaptiveReplyQuotes:
    def __init__(self):
        self.pending = OrderedDict()

    def note(self, chat_id, message_id, *, is_group=False):
        if is_group or not message_id:
            return
        messages = self.pending.setdefault(chat_id, [])
        if message_id not in messages:
            messages.append(message_id)
            del messages[:-64]
        self.pending.move_to_end(chat_id)
        while len(self.pending) > 256:
            self.pending.popitem(last=False)

    def anchor(self, chat_id, reply_to):
        messages = self.pending.get(chat_id, [])
        return None if messages == [reply_to] else reply_to

    def delivered(self, chat_id, reply_to):
        messages = self.pending.get(chat_id, [])
        if reply_to in messages:
            # Keep arrivals newer than the message this response actually answered.
            del messages[:messages.index(reply_to) + 1]
        if not messages:
            self.pending.pop(chat_id, None)
