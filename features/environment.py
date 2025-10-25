# features/environment.py

"""
Environment for Behave Testing
"""
from os import getenv
from selenium import webdriver
# ADD THESE IMPORTS:
from service import app # Import the Flask app object
from service.models import db, Product # Import db and Product model

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '30'))
# Use the correct port (8081 if you changed it)
BASE_URL = getenv('BASE_URL', 'http://localhost:8081')
DRIVER = getenv('DRIVER', 'firefox').lower()


def before_all(context):
    """ Executed once before all tests """
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS

    # -- INTIALIZE THE DATABASE AND APP CONTEXT --
    context.app = app.test_client()
    app.app_context().push()
    db.init_app(app)
    db.create_all() # Make sure tables are created

    # Select browser
    if 'firefox' in DRIVER:
        context.driver = get_firefox()
    else:
        context.driver = get_chrome()
    context.driver.implicitly_wait(context.wait_seconds)
    context.config.setup_logging()


def after_all(context):
    """ Executed after all tests """
    # --- FIX: Explicitly drop dependent tables first ---
    engine = db.get_engine()
    inspector = db.inspect(engine)
    if inspector.has_table(Product.__tablename__):
         Product.__table__.drop(engine) # Drop the product table first

    db.drop_all() # Now drop the rest
    # --- End Fix ---
    context.driver.quit()


def after_scenario(context, scenario):
    """ Runs after each scenario to clear the database """
    db.session.query(Product).delete()
    db.session.commit()

######################################################################
# Utility functions to create web drivers
######################################################################

def get_chrome():
    """Creates a headless Chrome driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)


def get_firefox():
    """Creates a headless Firefox driver"""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)