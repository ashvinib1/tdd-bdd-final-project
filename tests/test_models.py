# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, DataValidationError, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_product(self, count=1):
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            product = ProductFactory()
            product.create()
            products.append(product)
        return products

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_a_product(self):
        """It should Read a product"""
        product = self._create_product()[0]
        found_product = Product.find(product.id)
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a product"""
        product = self._create_product()[0]
        logging.debug(product)
        product_id = product.id
        # Update the product
        product.description = "New description"
        product.update()
        
        # Fetch it back
        found_product = Product.find(product_id)
        self.assertEqual(found_product.description, "New description")

    def test_delete_a_product(self):
        """It should Delete a product"""
        product = self._create_product()[0]
        product_id = product.id
        self.assertEqual(len(Product.all()), 1)
        # Delete the product
        product.delete()
        self.assertEqual(len(Product.all()), 0)
        # Try to find it again
        found_product = Product.find(product_id)
        self.assertIsNone(found_product)

    def test_list_all_products(self):
        """It should List all products"""
        self._create_product(count=5)
        self.assertEqual(len(Product.all()), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = self._create_product(count=5)
        first_product_name = products[0].name
        count = len([product for product in products if product.name == first_product_name])
        
        found_products = Product.find_by_name(first_product_name)
        self.assertEqual(found_products.count(), count)
        for product in found_products:
            self.assertEqual(product.name, first_product_name)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = self._create_product(count=10)
        category = products[0].category
        count = len([product for product in products if product.category == category])
        
        found_products = Product.find_by_category(category)
        self.assertEqual(found_products.count(), count)
        for product in found_products:
            self.assertEqual(product.category, category)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = self._create_product(count=10)
        # Make some unavailable
        products[0].available = False
        products[0].update()
        products[1].available = False
        products[1].update()

        available_products = Product.find_by_availability(True)
        self.assertEqual(available_products.count(), 8)
        
        unavailable_products = Product.find_by_availability(False)
        self.assertEqual(unavailable_products.count(), 2)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("price", data)
        self.assertEqual(Decimal(data["price"]), product.price)
        self.assertIn("available", data)
        self.assertEqual(data["available"], product.available)
        self.assertIn("category", data)
        self.assertEqual(data["category"], product.category.name)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        new_product = Product()
        new_product.deserialize(data)
        
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_deserialize_with_key_error(self):
        """It should raise DataValidationError with a KeyError"""
        product = Product()
        with self.assertRaises(DataValidationError) as context:
            product.deserialize({"id": 1, "description": "missing name"})
        self.assertIn("Invalid product: missing name", str(context.exception))
        
    def test_deserialize_with_type_error(self):
        """It should raise DataValidationError with a TypeError"""
        product = Product()
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(123) # Passing an int instead of dict
        self.assertIn("Invalid product: body of request is not a dictionary", str(context.exception))
