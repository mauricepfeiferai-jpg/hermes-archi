"""MQC Mac-native app connectors (read-only by default)."""
from .mail_connector import read_mail
from .calendar_connector import read_calendar
from .messages_connector import read_messages

__all__ = ["read_mail", "read_calendar", "read_messages"]
