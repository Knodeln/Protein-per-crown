import psycopg2


class Connection:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="protein")
        self.conn.autocommit = True
    
    def insert_product(self, product):
        insert_query = """
            INSERT INTO products (name, link, energy, protein, price) 
            VALUES (%s, %s, %s, %s, %s)
            """
            
        try:
            with self.conn.cursor() as cur:
                
                cur.execute(insert_query, (
                    product['name'],
                    product['link'],
                    product['energy'],
                    product['protein'],
                    product['price']
                ))
                print(f"Product '{product['name']}' inserted successfully.")
        except Exception as e:
            print("Insertion failed:", self.get_error(e))

    def close(self):
        if self.conn:
            self.conn.close()
            

    def get_error(self, e):
        message = repr(e)
        message = message.replace("\\n"," ")
        message = message.replace("\"","\\\"")
        return message


# db = Connection()
#
# product_data = {
#     "name": "Protein Bar",
#     "energy": 250,
#     "protein": 20,
#     "price": 2.99
# }
#
# db.insert_product(product_data)
# db.close()