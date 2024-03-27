import sqlite3
import pymysql.cursors


connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             database='comrade',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()
# sql = "ALTER TABLE category CHANGE cat_id new_cat_id INT AUTO_INCREMENT PRIMARY KEY;"

# sql = "INSERT INTO sub_category (sub_category_name, cat_id) VALUES ('Fiction', 1), ('Non-Fiction', 1), ('Mystery/Thriller', 1), ('Romance', 1), ('Computers/Laptops', 2), ('Smartphones/Tablets', 2), ('Televisions', 2), ('Cameras/Photography', 2), ('Living Room Furniture', 3), ('Bedroom Furniture', 3), ('Dining Room Furniture', 3), ('Office Furniture', 3), ('Cleaning Services', 4), ('Repair Services', 4),  ('Maintenance Services', 4), ('Consultation Services', 4), ('Skincare', 5), ('Makeup', 5), ('Haircare', 5), ('Fragrances', 5),('Stationery and School Supplies', 6), ('Home Decor', 6), ('Kitchenware', 6), ('Sports and Fitness', 6), ('Travel and Luggage', 6), ('Entertainment', 6);"
# cursor.execute(sql)
