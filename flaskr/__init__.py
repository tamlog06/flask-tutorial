import os
from flask import Flask

def create_app(test_config=None):
    # create and configure app

    # バージョン管理をしたくないものをインスタンスフォルダに格納するが、通常はこれをinstanceディレクトリに入れる
    # instance_relative_config=Trueとすると、instanceディレクトリをインスタンスディレクトリと認識し、かつそこからの相対パスで指定することができるようになる
    app = Flask(__name__, instance_relative_config=True)

    # appの使用する標準設定
    # SECRET_KEYはパスワードのようなもの？
    # DATABASEはSQLiteデータベースのパス
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # もしインスタンスフォルダにconfig.pyファイルがあれば、値をそこから取り出して、標準設定を上書きします。例えば、デプロイの時には、本当のSECRET_KEYを設定するために使用できます。
        # silent=Trueで、ファイルが見つからなかった時のエラーを抑制
        app.config.from_pyfile("config.py", silent=True)    
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page test say hello
    @app.route("/hello")
    def hello():
        return "Hello World"
    
    from . import db
    db.init_app(app)
    
    return app

