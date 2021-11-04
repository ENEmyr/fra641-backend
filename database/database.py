from configs import DB_CONF
from databases import Database

DATABASE_URL = "{dialect}://{username}:{password}@{host}/{database}".format(**DB_CONF)
db = Database(DATABASE_URL)
