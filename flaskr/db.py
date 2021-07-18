import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

'''
gは特別なオブジェクトで、リクエストごとに個別なものになります。それは、リクエストの（処理）期間中は複数の関数によってアクセスされるようなデータを格納するために使われます。
connectionは（gオブジェクトに）格納されて、もしも同じリクエストの中でget_dbが2回呼び出された場合、新しいconnectionを作成する代わりに、再利用されます。

current_appはもうひとつの特別なオブジェクトで、リクエストを処理中のFlaskアプリケーションを指し示します。
application factoryを利用しているため、残りのコードを書いているときは、Flaskアプリケーションのオブジェクトは存在しません
（訳注: application factoryを作成・使用する場合、ソースコードでどこからでもアクセスできる場所・モジュール変数に「app = Flask(__name__)」のようなコードを普通は書かなくなるため、
factory関数以外の場所からアクセスできるFlaskインスタンス（を格納する変数）が基本的には存在しないという意味合いだと思います）。
get_dbが呼び出されるのは、アプリケーションが作成されてリクエストを処理しているときであるため、current_appが使用できます。

sqlite3.connect()は、設定の（訳注: current_app.configの）キーDATABASEで示されるファイルへのconnectionを確立します。このファイルはまだ存在せず、後程データベースを初期化するまで存在しないままです。
sqlite3.Rowは、dictのように振る舞う行を返すようにconnectionへ伝えます。これは列名による列へのアクセスを可能にします。
close_dbは、g.dbが設定されているか調べることでconnectionが作成済みであるかを調べます。もしconnectionが存在した場合は、それを閉じます。（この文書の）後の方では、各リクエストの後でclose_dbが呼び出されるように、application factoryの中でclose_db関数についてアプリケーションに伝えます。
'''

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # flaskrから相対位置のファイルを読み取る
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''clear the existing data and create new tables.'''
    init_db()
    click.echo("Initialized the database")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

