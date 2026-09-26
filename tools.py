from database.db import get_connection


def search_products(query: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, category, price, stock
                FROM products
                WHERE name ILIKE %s
                   OR category ILIKE %s
                ORDER BY id;
                """,
                (f"%{query}%", f"%{query}%"),
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price": float(row[3]),
            "stock": row[4],
        }
        for row in rows
    ]


def check_stock(product_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, stock
                FROM products
                WHERE id = %s;
                """,
                (product_id,),
            )

            row = cursor.fetchone()

    if row is None:
        return {
            "success": False,
            "error": "Product not found",
        }

    return {
        "success": True,
        "product_id": row[0],
        "name": row[1],
        "stock": row[2],
        "in_stock": row[2] > 0,
    }


def delete_product(product_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM products
                WHERE id = %s
                RETURNING id, name;
                """,
                (product_id,),
            )

            row = cursor.fetchone()

    if row is None:
        return {
            "success": False,
            "error": "Product not found",
        }

    return {
        "success": True,
        "message": "Product deleted successfully",
        "product_id": row[0],
        "name": row[1],
    }