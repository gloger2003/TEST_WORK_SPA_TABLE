from __future__ import annotations

from flask_sqlalchemy import Model
from sqlalchemy.orm.query import Query


def sort_query(query: Query, Model: Model, sort_string: str):
    try:
        attr, direction = sort_string.split('-')
        model_attr = getattr(Model, attr)
        res = query.order_by(model_attr.desc()).all()

        if direction == 'down':
            res.reverse()
    except Exception as e:
        print(e)
        res = []
    return res
