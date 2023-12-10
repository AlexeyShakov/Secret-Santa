if [ "$DB_HOST" = "secret_santa_db" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi


alembic upgrade head
python main.py