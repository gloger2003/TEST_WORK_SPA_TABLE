"""
!!!
Можно было и через переменные окружения задать, но т.к.
это просто тестовое задание, я решил сделать через кфг,
чтобы их можно было быстрее редактировать
!!!
"""

# =====================================================
# < Настройки приложения > ============================

# Включает режим дебага для Flask-приложения
DEBUG = True

# Директория для хранения логов
# (У тестового задания я их не развивал,
#  там всего пару строчек логгинга)
LOG_DIR = './logs'

# Вид: 'mysql+pymysql://{login}:{pass}@{host}/{structure}'
# Пример:
#   'mysql+pymysql://root:1234@localhost/TE_Tables'
# app.config['SQLALCHEMY_DATABASE_URI']: str
SQLALCHEMY_DATABASE_URI = ('mysql+pymysql://')


# app.config['SECRET_KEY']: str
SECRET_KEY = ''

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']: bool
SQLALCHEMY_TRACK_MODIFICATIONS = False

# =====================================================
# =====================================================


# =====================================================
# < Настройки отображения страницы > ==================
# =====================================================

# Максимальное кол-во строк в таблице
# на одной странице
MAX_ROWS_IN_TABLE = 10

# Желаемое кол-во кнопок для навигации на странице
PAGE_NUM_BTN_COUNT = 10
# =====================================================
# =====================================================
