from flask import jsonify, request, abort, url_for
from service import app
from service.models import Product, Category, db
from service.common import status
from flask import current_app

WAIT_SECONDS = 30

def check_content_type(content_type):
    if "Content-Type" not in request.headers:
        current_app.logger.error("No Content-Type specified.")
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}")
    if request.headers["Content-Type"] != content_type:
        current_app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {content_type}")

@app.route("/health")
def healthcheck():
    return jsonify(status=200, message="OK"), status.HTTP_200_OK

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/products", methods=["POST"])
def create_products():
    check_content_type("application/json")
    data = request.get_json()
    product = Product()
    product.deserialize(data)
    db.session.add(product)
    db.session.commit()
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return jsonify(product.serialize()), status.HTTP_201_CREATED, {"Location": location_url}

@app.route("/products", methods=["GET"])
def list_products():
    name = request.args.get("name")
    category_str = request.args.get("category")
    available_str = request.args.get("available")
    query = Product.query

    if name:
        query = query.filter_by(name=name)
    elif category_str:
        try:
            category = Category[category_str.upper()]
            query = query.filter_by(category=category)
        except KeyError:
            query = query.filter_by(category=None)
    elif available_str:
        available = available_str.lower() in ["true", "1", "yes"]
        query = query.filter_by(available=available)

    results = [p.serialize() for p in query.all()]
    return jsonify(results), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    return product.serialize(), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    check_content_type("application/json")
    product = Product.query.get(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
    data = request.get_json()
    product.deserialize(data)
    db.session.commit()
    return product.serialize(), status.HTTP_200_OK

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return "", status.HTTP_204_NO_CONTENT
