# project-connect-api

1. Install pre-requisites
=========================

Virtualenv
----------
Standard installation with virtualevnwrapper.

PostgreSQL
----------
Standard installation.



# Standard project initialization
## 1. Create virtual environment


1. Clone repository: ``git clone https://github.com/razortheory/project-connect-api.git``
2. Create virtual environment: ``mkvirtualenv proco -p python3``
3. Install requirements ``pip install -r requirements/dev.txt``
4. Edit ``$VIRTUAL_ENV/bin/postactivate`` to contain the following lines:

        export DATABASE_URL=postgres://username:password@localhost/dbname
        export DEV_ADMIN_EMAIL=your@email.com

5. Deactivate and re-activate virtualenv:

        deactivate
        workon proco


## 2. Database

1. Create database table:

        psql -U your_psql_user
        CREATE DATABASE proco;

2. Migrations: ``./manage.py migrate``
3. Create admin: ``./manage.py createsuperuser``
4. Run the server ``./manage.py runserver``


# Alternative project initialization

1. Clone repository: ``git clone https://github.com/razortheory/project-connect-api.git``
2. Create project database
3. Execute the following command to setup database credentials:

        echo DATABASE_URL=postgres://username:password@localhost/dbname >> env.config

4. **Make sure that you are not in any of existing virtual envs**
5. run ``./initproject.bash`` - will run all commands listed in standard initialization, including edition of postactivate
6. activate virtualenv ``workon proco``
7. run ``./manage.py runserver``

