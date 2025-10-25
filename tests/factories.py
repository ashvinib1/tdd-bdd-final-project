# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
# (License text omitted for brevity)

"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import Product, Category


class ProductFactory(factory.Factory):
    """Creates fake products for testing"""

    class Meta:
        """Maps factory to data model"""
        model = Product

    id = factory.Sequence(lambda n: n)

    # Corrected attributes for fake data (using Category Enums)
    name = FuzzyChoice(choices=[
        "Hat", "Pants", "Shirt", "Apple", "Banana",
        "Pots", "Towels", "Ford", "Chevy", "Hammer", "Wrench"
    ])
    description = factory.Faker("text")
    price = FuzzyDecimal(low=0.5, high=2000.0, precision=2)
    available = FuzzyChoice(choices=[True, False])
    # Use Category Enum members, not strings
    category = FuzzyChoice(choices=[
        Category.UNKNOWN,
        Category.CLOTHS,
        Category.FOOD,
        Category.HOUSEWARES,
        Category.AUTOMOTIVE,
        Category.TOOLS
    ])