from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from app import app, db
from app.import_data import ImportData
# 实例化migrate
migrate = Migrate(app, db)
# 命令行解析
manager = Manager(app)
# 添加命令行参数
manager.add_command('db', MigrateCommand)
manager.add_command('Import_data', ImportData())


from app import routes

if __name__ == '__main__':
    # app.run()
    # db.create_all()
    manager.run()

