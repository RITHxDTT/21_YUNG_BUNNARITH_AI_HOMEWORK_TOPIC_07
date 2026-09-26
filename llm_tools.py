from langchain_core.tools import tool

from tools import (
    search_products,
    check_stock,
    delete_product,
)


@tool
def search_products_tool(query: str):
    """
    Search for products by product name or category.

    Args:
        query: Product name or category to search for.
    """
    return search_products(query)


@tool
def check_stock_tool(product_id: int):
    """
    Check the current stock of a product.

    Args:
        product_id: ID of the product to check.
    """
    return check_stock(product_id)


@tool
def delete_product_tool(product_id: int):
    """
    Delete a product from the system.

    This is a destructive action.

    Args:
        product_id: ID of the product to delete.
    """
    return delete_product(product_id)


TOOLS = [
    search_products_tool,
    check_stock_tool,
    delete_product_tool,
]