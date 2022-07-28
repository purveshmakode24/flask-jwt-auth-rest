## Flask-JWT-Auth-Rest

### Some Important Commands:

STEP 1:  ```flask run``` or ```python app.py``` to start the app.

STEP 2 (OPTION 1): Using Flask-Migrate db commands [RECOMMENDED]
> Existing manually created (without ORM) tables is affected (DELETED) BY below commands, Migrate command simply checks the updated Models.py file and replace exisiting tables with brand new or updated ORM tables or models from models.py. So existance of Tables totally depends on the Models.py file which is taken care by Flask-Migrate Alembic.

(A) ```flask db init``` to initalize db for SQLalchemy db migrations [one time] (Module used flask-migrate) (don't require to delete db, this command to alter existing Model/db table).

(B) ```flask db migrate -m "Initial Migration"``` to initialize the migration changes.

(C) ```flask db upgrade``` to push the migrated changes in db.

STEP 2 (OPTION 2): Using SQLALchemy db command 

> Alternative to create db or all db tables initally (note: requires to delete exisiting db if any before making any changes to model) 

> Existing manually created (without ORM) tables won't affect by executing this command. It will keep exsiting tables and add other ORM tables

(A) In Python interpreter, or just by calling create_all() method of SQLALchemy db object.

```
here, db = SQLAlchemy(app)

>> from app import db
>> db.create_all()
```

For more details refer Flask-MySQLAlchemy official docs.
URL: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#a-minimal-application

#### Note ([REF](https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application)):

If you want to use another database engine such as PostgreSQL or MySQL, you’ll need to use the proper URI.

For PostgreSQL, use the following format:

```
postgresql://username:password@host:port/database_name
```
For MySQL:
```
mysql://username:password@host:port/database_name
```
For more, see the [SQLAlchemy documentation for engine configuration](https://docs.sqlalchemy.org/en/14/core/engines.html).


#### Other Important References:
1) https://www.section.io/engineering-education/flask-crud-api/
2) https://geekflare.com/securing-flask-api-with-jwt/
