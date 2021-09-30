from __future__ import annotations
from flask_sqlalchemy import Model

from sqlalchemy.orm.query import Query
from flask import config, session

from filter_utils import filter_query
from sort_utils import sort_query

import config


def filter_process(session: session, req_data: dict,
                   query: Query, model: Model, page_index: int):
    """ Фильтрация Query и обработка фильтрационных параметров сессии
        ------------------------------------------
        RETURN:
            * `filter_enabled`: bool
            * `bad_filter`: bool
            * `query`: Query
            * `page_index`: int
        """
    filter_enabled = req_data.get(
        'filter_enabled', session.get('filter_enabled', None))
    filter_column = req_data.get(
        'filter_column', session.get('filter_column', None))
    filter_condition = req_data.get(
        'filter_condition', session.get('filter_condition', None))
    filter_value = req_data.get(
        'filter_value', session.get('filter_value', None))

    # Если параметры фильтра изменились
    # то устанавливаем самую первую страницу
    if (filter_column != session['filter_column']
            or filter_condition != session['filter_condition']
            or filter_value != session['filter_value']):
        page_index, session['page_index'] = 0, 0

    # Указывает, являются ли параметры фильтрации неверными
    bad_filter = False

    if filter_enabled:
        session['filter_enabled'] = filter_enabled
        session['filter_column'] = filter_column
        session['filter_condition'] = filter_condition
        session['filter_value'] = filter_value

        if filter_enabled:
            # Простенькая защита от неверных параметров фильтра
            # или ошибок сервера при фильтрации
            # с помощью проверки исключений
            try:
                query = filter_query(query, model, filter_column,
                                     filter_condition, filter_value)
            except Exception as e:
                query = Query([])
                bad_filter = True
    return filter_enabled, bad_filter, query, page_index


def sort_process(session: session, req_data: dict, query: Query, model: Model):
    """ Сортирировка Query и обработка зависимых данных
        -----------------------------------------------

        RETURN:
            * `sort_enabled`: bool
            * `rows`: list[Row]
    """

    sort_string = None

    # Если вы второй раз нажали на ту же кнопку сортировки,
    # то сортировка будет отключена
    if req_data.get('sort_string', None) == session.get('sort_string', None):
        sort_string = None
        session['sort_string'] = None
    else:
        sort_string = req_data.get(
            'sort_string', session.get('sort_string', None))

    if sort_string:
        session['sort_string'] = sort_string
        rows = sort_query(query, model, sort_string)
    else:
        rows = []

    return bool(sort_string), rows


def page_update_process(session: session, page_index: int, rows: list[Model]):
    """ Получает срез нужных для рендера строк и
        срез номеров страниц для рендера и
        поддержки пагинации на странице

        RETURN:
            * `need_render_rows`: list[Row]
            * `page_numbers`: list[int]
    """

    # Максимальное кол-во строк в таблице
    # на одной странице
    max_rows_in_table = config.MAX_ROWS_IN_TABLE

    # Желаемое кол-во кнопок для навигации на странице
    page_num_btn_count = config.PAGE_NUM_BTN_COUNT

    # Посты для рендера на выбранной странице
    need_render_rows = rows[(page_index * max_rows_in_table):
                            (page_index * max_rows_in_table) +
                            max_rows_in_table]

    # Список всех номеров страниц, которые доступны
    all_page_nums = [k + 1 for k in range(len(rows) // max_rows_in_table)]

    # Если после инт-деления есть остаток,
    # то добавляем еще одну страницу в конец списка
    if all_page_nums:
        if len(rows) - (all_page_nums[-1] * max_rows_in_table) > 0:
            all_page_nums.append(all_page_nums[-1] + 1)

    # Стартовая страница в пагинации
    # Отрезок
    #  - Включает в себя страницы:
    #  - [N - 1, N, <...>, N + page_num_btn_count, N + 1]
    start_page_index = ((page_index // page_num_btn_count)
                        * page_num_btn_count + 1)

    # Нужно оставить страницу,
    # чтобы переключался отрезок назад
    if start_page_index - 2 >= 0:
        # Если это не самый первый отрезок
        start_page_index -= 2
    else:
        start_page_index -= 1

    # Первичный индекс последней страницы
    end_page_index = start_page_index + page_num_btn_count + 1

    # Прибавляем еще одну страницу,
    # чтобы переходило на следующий отрезок
    end_page_index = end_page_index + 1 \
        if start_page_index > 0 else end_page_index

    # Делаем первичный срез и
    # получаем список индексов страниц,
    # которые нужно показать на странице
    page_numbers = all_page_nums[start_page_index:end_page_index]

    # Если длина отрезка меньше нужной,
    # то добавляем в него страницы из предыдущего отрезка
    if len(page_numbers) < page_num_btn_count + 1:
        page_numbers = all_page_nums[-page_num_btn_count - 2:]

    # Записываем новые данные в сессию
    # для рендера таблицы и кнопок для пагинации
    session['page_index'] = page_index
    session['page_numbers'] = page_numbers
    return need_render_rows
