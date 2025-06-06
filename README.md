git clone
cd fitness-api
pip install -r requirements.txt


python manage.py migrate

python create_classes.py


python manage.py runserver



Get Upcoming Classes:
curl --location 'http://127.0.0.1:8000/apiV1/classes/' \
--header 'Accept: application/json'



Create a Booking:
curl --location 'http://127.0.0.1:8000/apiV1/bookings/' \
--header 'Content-Type: application/json' \
--data-raw '{
  "class_id": 1,
  "client_name": "test name",
  "client_email": "test@gmail.com"
}'



Get Bookings for a User:
curl --location 'http://127.0.0.1:8000/apiV1/bookings/?email=test%40gmail.com&tstatus=CONFIRMED' \
--header 'Accept: application/json'


















