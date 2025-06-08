from flask_migrate import Migrate
from app import app, db
from settings import RUN_SEEDERS

# from endpoints.users.model import User, UserType, Gender, Client, Customer
# from endpoints.address.model import Address
# from endpoints.products.model import Product
# from endpoints.jastip.model import OrderStatus, JastipTransactionDetail, JastipTransactionHeader, JastipSession, JastipSessionProducts
# from endpoints.anjem.model import AnjemOrder, AnjemArea

# migrate = Migrate(app, db)

# from endpoints.anjem.seeders import SeedAnjemAreas
# if RUN_SEEDERS:
#     SeedAnjemAreas()