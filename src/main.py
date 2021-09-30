from __future__ import annotations

import os
from datetime import date, datetime

from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from loguru import logger

from funcs import filter_process, page_update_process, sort_process

import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config[
    'SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

# Инициализируем БД
db = SQLAlchemy(app)


class Row(db.Model):
    """ Класс строки для таблицы """
    __tablename__ = 'Rows'

    uid = db.Column(db.Integer(), primary_key=True)

    date = db.Column(db.Date(), default=date.today())
    title = db.Column(db.String(255), nullable=False)
    count = db.Column(db.Integer(), nullable=False)
    distance = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return "<{}:{}>".format(self.uid,  self.title)


# Создаём таблицу Row
db.create_all()


@app.route('/')
@app.route('/index/')
def index():
    """ Главная страница """
    return render_template('index.j2')


@app.route('/render_content/', methods=['POST', 'GET'])
def render_content():
    req_data: dict = request.get_json()

    try:
        page_index = int(req_data.get(
            'page_index', session.get('page_index', 0)))
    except TypeError:
        page_index = 0

    # Получаем все строки из бд для таблицы
    query = db.session.query(Row)

    # Пробуем отфильтровать строки
    filter_result = filter_process(session, req_data, query, Row, page_index)
    filter_enabled, bad_filter, query, page_index = filter_result

    # Пробуем отсортировать строки
    sort_enabled, rows = sort_process(session, req_data, query, Row)

    # Преобразуем Query в list[Row]
    if not sort_enabled and not filter_enabled:
        rows = db.session.query(Row).all()
    else:
        if not sort_enabled:
            rows = query.all()

    # Выбранная страница
    if page_index != 0 and not bool(page_index):
        page_index = session['page_index']
    page_index = page_index if page_index >= 0 else 0

    # Посты, которые нужно отобразить
    need_render_rows = page_update_process(session, page_index, rows)

    logger.debug('Данные для рендера таблицы получены:')
    logger.debug(f' - Сессия: {session}')
    logger.debug(f' - Индекс страницы: {page_index}')
    logger.debug(f' - Фильтр активен: {filter_enabled}')
    logger.debug(f' - Сортировка активна: {sort_enabled}')

    return render_template(
        'table_gen.j2',
        page_index=page_index,
        rows=need_render_rows,
        bad_filter=bad_filter
    )


@app.route('/render_pagination/')
def render_pagination():
    """ Добавляет на страницу список кнопок для навигации """
    return render_template(
        'pagination_gen.j2',
        page_index=session['page_index'],
        page_numbers=session['page_numbers'],
        is_last_page=len(session['page_numbers']) <= 1,
    )


if __name__ == '__main__':
    if config.DEBUG:
        # Для удаления папки с логами,
        # чтобы не засорять лишний раз
        import shutil
        try:
            shutil.rmtree(config.LOG_DIR)
        except PermissionError as e:
            logger.error(e)

    if not os.path.exists(config.LOG_DIR):
        os.mkdir(config.LOG_DIR)

    # Указываем путь для сохранения лога
    logger.add(f'{config.LOG_DIR}/'
               f'{datetime.now().strftime("%Y-%m-%d %Hh %Mm")}.log',
               encoding='utf-8')

    # Запускаем приложение
    app.run(debug=config.DEBUG)
