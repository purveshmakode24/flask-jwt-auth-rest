## Flask-Rest

#### Some Important Commands:

1) ```flask run``` or ```python app.py``` to start the app.
> Flask-SQLAlchemy (ORM) based db commands
2) ```flask db init``` to initalize db for SQLalchemy db migrations [one time] (Module used flask-migrate) (don't require to delete db, this command to alter existing Model/db table)
3) ```flask db migrate -m "Initial Migration"``` to initialize the migration changes
4) ```flask db upgrade``` to push the migrated changes


Alternative to create db initally (note: requires to delete exisiting db if any before making any changes to model)

In Python interpreter

```
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
