import os

base_path = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Parent configuration class."""

    DEBUG = False
    LOGIN_DISABLED = False

    SECRET_KEY = os.urandom(24)
    BASE_DIR = base_path
    STATIC = os.path.join(BASE_DIR, "static")
    UPLOADED_PATH_IMAGE = os.path.join(STATIC, "uploads", "images")
    UPLOADED_PATH_THUM = os.path.join(STATIC, "uploads", "thumbs")

    UPLOADED_PRODUCTPHOTOS_DEST = os.path.join(STATIC, "uploads", "products")
    UPLOADED_CATEGORYPHOTOS_DEST = os.path.join(STATIC, "uploads", "category")
    UPLOADED_SUBCATEGORYPHOTOS_DEST = os.path.join(
        STATIC, "uploads", "subcategory"
    )
    UPLOADED_IDCARDPHOTOS_DEST = os.path.join(
        STATIC, "uploads", "idcard"
    )
    UPLOADED_BRNPHOTOS_DEST = os.path.join(
        STATIC, "uploads", "brn"
    )
    UPLOADED_ADDRESSPHOTOS_DEST = os.path.join(
        STATIC, "uploads", "address"
    )
    UPLOADED_STORELOGOPHOTOS_DEST = os.path.join(
        STATIC, "uploads", "store_logo_photos"
    )
    UPLOADED_STOREBANNERPHOTOS_DEST = os.path.join(
        STATIC, "uploads", "store_banner_photos"
    )

    PASSWORD_SALT = "abcdefghi"

    # either
    # SQLALCHEMY_DATABASE_URI = "sqlite:///shopyo.db"

    # or
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{server_name}/{db_name}".format(
        username='shopyo_user',
        password='pass',
        server_name='localhost',
        db_name='shopyodb'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configurations for development"""

    ENV = "development"
    DEBUG = True
    # EXPLAIN_TEMPLATE_LOADING = True
    LOGIN_DISABLED = True
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{server_name}/{db_name}".format(
    #         username='',
    #         password='',
    #         server_name='localhost',
    #         db_name=''
    #     )


class TestingConfig(Config):
    """Configurations for testsing"""

    SQLALCHEMY_DATABASE_URI = "sqlite:///testing.db"
    DEBUG = True
    LIVESERVER_PORT = 8943
    LIVESERVER_TIMEOUT = 10
    SERVER_NAME = "localhost.com"
    BCRYPT_LOG_ROUNDS = 4
    TESTING = True
    WTF_CSRF_ENABLED = False


app_config = {
    "development": DevelopmentConfig,
    "production": Config,
    "testing": TestingConfig,
}
