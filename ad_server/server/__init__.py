from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import timedelta
import config

db = SQLAlchemy()

migrate = Migrate()

def create_app():
    '''create app'''
    app = Flask(__name__)

    # Upload file size limit -> 500 MBytes
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1000 * 1000
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FILE_DIR

    app.config.from_object(config)

    # ORM DB setting
    db.init_app(app)
    migrate.init_app(app=app, db=db, render_as_batch=True)
    
    from server import models

    # View import
    from .views import (
        main_views,
    )

    # Register modules into app
    app.register_blueprint(main_views.bp)

    # Filters
    from .filters import (
        format_datetime_for_input_calendar,
        format_datetime_year_only,
        make_short_string_70chars,
        make_short_string_30chars,
        make_short_string_10chars,
        url_trim,
        comma_seperate,
        remove_phd_master,
    )
    app.jinja_env.filters['datetime_dash'] = format_datetime_for_input_calendar # 대쉬(-) 표현 날짜 (22-02-15)
    app.jinja_env.filters['datetime_year_only'] = format_datetime_year_only # 4자리 연도만 표시 (2024)
    app.jinja_env.filters['shorten_70chars'] = make_short_string_70chars # 70글자 축약
    app.jinja_env.filters['shorten_30chars'] = make_short_string_30chars # 30글자 축약
    app.jinja_env.filters['shorten_10chars'] = make_short_string_10chars # 10글자 축약
    app.jinja_env.filters['url_trim'] = url_trim # url 첨가 앱이름 문자열 제거:  'server' 제거
    app.jinja_env.filters['comma_seperate'] = comma_seperate # 숫자, 문자형 숫자 -> 세자리 콤마
    app.jinja_env.filters['remove_phd_master'] = remove_phd_master # 앞글자 제거:[박사학위 논문], [석사학위 논문]

    return app