"""键值设置读写。"""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from ..models import Setting


def get_settings_map(db: Session) -> dict:
    """读取全部设置，value 存的是 JSON 字符串，按需反序列化。"""
    out: dict = {}
    for row in db.query(Setting).all():
        if row.value is None:
            out[row.key] = None
            continue
        try:
            out[row.key] = json.loads(row.value)
        except (json.JSONDecodeError, ValueError):
            out[row.key] = row.value
    return out


def set_settings(db: Session, values: dict) -> None:
    """批量覆盖写入设置。字符串原样存储，其余 JSON 序列化。"""
    for key, value in values.items():
        row = db.get(Setting, str(key))
        encoded = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        if row is None:
            db.add(Setting(key=str(key), value=encoded))
        else:
            row.value = encoded