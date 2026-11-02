from setup import setup

MONGO_URL = "mongodb://admin:admin123@localhost:27017/BasicPyRestaurant?authSource=admin"
DATABASE_NAME="BasicPyRestaurant"
APP_URL="localhost:8080"
streamlit=setup(mongo_url=MONGO_URL,database_name=DATABASE_NAME,app_url=APP_URL)
streamlit.run()
