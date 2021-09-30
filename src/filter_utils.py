from __future__ import annotations

from flask_sqlalchemy import Model
from sqlalchemy.orm.query import Query


def filter_by_contains(query: Query, model: Model, value: str, attr: str):
    res = query.filter(getattr(model, attr).contains(value))
    return res


def filter_by_equal(query: Query, model: Model, value: str, attr: str):
    attr_value = getattr(model, attr)

    res = query.filter(attr_value == value)
    return res


def filter_by_more(query: Query, model: Model, value: str, attr: str):
    attr_value = getattr(model, attr)

    if attr != 'date':
        value = int(value)

    res = query.filter(attr_value > value)
    return res


def filter_by_less(query: Query, model: Model, value: str, attr: str):
    attr_value = getattr(model, attr)

    if attr != 'date':
        value = int(value)

    res = query.filter(attr_value < value)
    return res


# Ассоциации фильтров и функций
FILTERS_ASSOC = {
    '0': filter_by_equal,
    '1': filter_by_contains,
    '2': filter_by_more,
    '3': filter_by_less,
}

# Ассоциации значений и атрибутов
ATTRS_ASSOC = {
    '0': 'date',
    '1': 'title',
    '2': 'count',
    '3': 'distance'
}


def filter_query(query: Query, model: Model, filter_column: str,
                 filter_condition: str, filter_value: str):
    return FILTERS_ASSOC[filter_condition](
        query, model, filter_value, ATTRS_ASSOC[filter_column])
