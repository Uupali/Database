import os
import pymysql
from sshtunnel import SSHTunnelForwarder
import getpass
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Read credentials from environment with fallback to interactive prompts
# Environment variable names used: SSH_USERNAME, SSH_PASSWORD, DB_USER, DB_PASSWORD
ssh_username = os.getenv('SSH_USERNAME') or input("Enter your SSH username: ")
ssh_password = os.getenv('SSH_PASSWORD') or getpass.getpass("Enter your SSH password: ")

db_user = os.getenv('DB_USER') or input("Enter your group name: ")
db_password = os.getenv('DB_PASSWORD') or getpass.getpass("Enter your group password: ")

# Set SSH tunnel
tunnel = SSHTunnelForwarder(
    ('fries.it.uu.se', 22),  #port = 22
    ssh_username=ssh_username,
    ssh_password=ssh_password,
    remote_bind_address=('127.0.0.1', 3306)
)

# Start SSH tunnel
tunnel.start()

# Connect to MySQL database
mydb = pymysql.connect(
    host='127.0.0.1',
    user=db_user,
    password=db_password,
    port=tunnel.local_bind_port,
    database=db_user
)


create_tables_command = """
CREATE TABLE IF NOT EXISTS Users
(
    person_number VARCHAR(13) PRIMARY KEY,
    first_name VARCHAR(40),
    last_name VARCHAR(40),
    address VARCHAR(150),
    phone_number VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    newsletter_permission BOOL
);

CREATE TABLE IF NOT EXISTS Departments
(
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(25),
    description VARCHAR(200),
    link VARCHAR(120),
    parent_department_id INT,

    CONSTRAINT fk_parent 
        FOREIGN KEY (parent_department_id)
        REFERENCES Departments(department_id)
);

CREATE TABLE IF NOT EXISTS Orders
(
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_reference VARCHAR(25),
    order_date DATE,
    date_last_change DATE,
    status CHAR(15),
    tracking_number VARCHAR(15),
    person_number VARCHAR(13),

    CONSTRAINT fk_orders_person
        FOREIGN KEY (person_number)
        REFERENCES Users(person_number)
    
);

CREATE TABLE IF NOT EXISTS Products
(
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(30),
    description VARCHAR(700),
    short_description VARCHAR(70),
    quant_in_stock INT,
    discount_percent INT,
    retail_no_vat FLOAT,
    vat_percent FLOAT,
    link VARCHAR(120),
    is_featured BOOL,
    department_id INT,

    CONSTRAINT fk_products_department
        FOREIGN KEY (department_id)
        REFERENCES Departments(department_id)
);


CREATE TABLE IF NOT EXISTS Reviews
(
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    star_rating TINYINT,
    text VARCHAR(500),
    product_id INT,
    person_number VARCHAR(13),

    CONSTRAINT fk_reviews_person 
        FOREIGN KEY (person_number)
        REFERENCES Users(person_number),
    CONSTRAINT fk_reviews_product 
        FOREIGN KEY (product_id)
        REFERENCES Products(product_id),
    CONSTRAINT max_star
        CHECK (star_rating <= 5),
    CONSTRAINT min_star
        CHECK (star_rating >= 1)
);
CREATE TABLE IF NOT EXISTS ProductsInOrder
(
    order_id INT,
    product_id INT,
    quantity INT,

    PRIMARY KEY(order_id, product_id),

    CONSTRAINT fk_PIO_order 
        FOREIGN KEY (order_id)
        REFERENCES Orders(order_id),

    CONSTRAINT fk_PIO_product 
        FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
);
CREATE TABLE IF NOT EXISTS KeywordOf
(
    product_id INT,
    keyword VARCHAR(20),

    PRIMARY KEY(product_id, keyword),

    CONSTRAINT fk_keyword_of_product 
        FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
);

"""

create_electronics_depts = """
INSERT INTO Departments
(department_id, title, description, link, parent_department_id)
VALUES
(1, 'Home', 'Welcome to AltOnline', '/home', NULL),
(2, 'Electronics', 'Electronic devices', '/electronics', 1),
(3, 'Laptops', 'All kinds of laptops', '/electronics/laptops', 2),
(4, 'Phones', 'Smartphones and mobile phones', '/electronics/phones', 2)
"""

create_book_dept = """
INSERT INTO Departments (title, description, link, parent_department_id)
VALUES ('Books','Our store offers tons of awesome books.','/home/books', 1);
"""

create_products_test = """
INSERT INTO Products (title, description, short_description, quant_in_stock, discount_percent, retail_no_vat, vat_percent, link, is_featured, department_id)
VALUES ('iPhone 7', 'epic iphone super cool helps you work and helps with school', 'cool phone', '2000','5','12000','25','www.altonline.com/iphone7',TRUE, 4),
    ('iPhone 6', 'sorta cool iphone helps you work(kinda) and helps with school(kinda)', 'less cool phone', '1000','5','8000','25','www.altonline.com/iphone6',FALSE, 4),
    ('Pippi Långstrump', 'Astrid Lindgren''s classic children''s book', 'pippi är bäst', '10','0','200','0','www.altonline.com/pippilangstrump',FALSE, 6)
"""

create_more_products = """

INSERT INTO Products (title, description, short_description, quant_in_stock, discount_percent, retail_no_vat, vat_percent, link, is_featured, department_id)
VALUES ('Macbook Pro', 'epic laptop super cool helps you work and helps with school', 'cool laptop', '2000','5','30000','25','www.altonline.com/macbookpro',TRUE, 4),
    ('Macbook Slow', 'it''s a macbook but it runs helllla slow', 'slow laptop', '100','5','10000','25','www.altonline.com/macbookslow',FALSE, 4),
    ('Of Mice and Men', 'Steinbeck was the gooaat', 'is it about mice? or men? or both???', '120','0','100','0','www.altonline.com/ofmiceandmen',FALSE, 6),
    ('Of Rice and Men', 'A practical guide for rice cookery the worldwide', 'is it about rice? or men? or both???', '120','0','100','0','www.altonline.com/ofriceandmen',FALSE, 6),
    ('Elementary Swedish', 'Swedish for absolute beginners. This course will get you fluent in no time', 'A basic swedish book', '120','0','150','0','www.altonline.com/elementaryswedish',FALSE, 6),
    ('Clown Class', 'Have you ever been interested in clownery? This book will teach you all you need to know', 'A basic clown book', '120','0','600','0','www.altonline.com/clownclass',TRUE, 6),
    ('Advanced Clowning Principles', 'ONLY FOR EXPERTS: DO NOT BUY THIS BOOK IF YOU HAVEN''T COMPLETED BASIC CLOWNERY!!', 'An advanced clown book', '120','0','800','0','www.altonline.com/advancedclowning',TRUE, 6)

"""

create_keywords = """
INSERT INTO KeywordOf (product_id, keyword)
VALUES (11, 'Macbook'),
    (12, 'Macbook'),
    (13, 'Men'),
    (14,'Men')
"""

create_users = """
INSERT INTO Users(person_number, first_name, last_name, address, phone_number, email, password, newsletter_permission) 
VALUES ('199901170327', 'Goran', 'Johansson', 'Sveasvängen 3, Norrköping', '696969696', 'svea2345@svea.com', 'Johansson_är_rolig', 1),
    ('200301170327', 'Alfons', 'Foks', 'Gubbegatan 3, Norrköping', '420420420', 'alfons5@svea.com', 'tyckerinteomfisk', 0)
"""

create_order = """
INSERT INTO Orders(payment_reference, order_date, date_last_change, status, tracking_number, person_number)
VALUES ('13524524','20251201','20251202','In transit', NULL,'199901170327')
"""

add_product_to_order = """
INSERT INTO ProductsInOrder(order_id, product_id, quantity)
VALUES (1,17,2)
"""


query_to_get_welcome_text = """
SELECT description, department_id  FROM Departments WHERE department_id = 1
"""

query_to_get_toplevel_depts = """
SELECT * FROM Departments WHERE parent_department_id = 1
"""

query_to_get_featured_prods = """
SELECT * FROM Products WHERE is_featured
"""
query_to_get_keyword_relateds = """
SELECT * FROM Products 
WHERE product_id IN(
    SELECT product_id FROM KeywordOf
    WHERE keyword IN (
        SELECT keyword FROM KeywordOf
        WHERE product_id = 11
    )
)
"""

query_to_get_all_prods_from_leaf_dept = """

WITH CURRENT_PRICES AS(
SELECT product_id, ((retail_no_vat - discount_percent/100)*(1 + vat_percent/100))AS current_price FROM Products
),

AVERAGE_RATINGS AS(
SELECT product_id, AVG(star_rating) AS avg_rating FROM Reviews
GROUP BY product_id)

SELECT Products.title, Products.short_description, CURRENT_PRICES.current_price, AVERAGE_RATINGS.avg_rating
FROM Products
LEFT JOIN CURRENT_PRICES ON (Products.product_id = CURRENT_PRICES.product_id)
LEFT JOIN AVERAGE_RATINGS ON (Products.product_id = AVERAGE_RATINGS.product_id)
WHERE Products.department_id = 4
"""

query_to_get_products_on_sale_sorted = """
SELECT * FROM Products WHERE discount_percent > 0 ORDER BY discount_percent DESC
"""

add_sort_idx = """
CREATE INDEX discount_idx ON Products(discount_percent)
"""

add_feat_idx = """
CREATE INDEX feat_idx ON Products(is_featured)
"""

# Excute MySQL statements
mycursor = mydb.cursor()
'''
for command in create_tables_command.split(";"):
    print(command)
    mycursor.execute(command)
    mydb.commit()
'''
mycursor.execute(add_feat_idx)
mydb.commit()


my_queries = {"welcome text": query_to_get_welcome_text,"toplevel depts": query_to_get_toplevel_depts,"prods of leaf":query_to_get_all_prods_from_leaf_dept,"prods on sale sort":query_to_get_products_on_sale_sorted,"featured":query_to_get_featured_prods,"keyword relateds":query_to_get_keyword_relateds}

for name,query in my_queries.items(): #for each of the queries get the number of rows queried
    explained_q = "EXPLAIN " + query
    value = mycursor.execute(explained_q)
    
    print(name)
    counter = 0
    for x in mycursor:
        if x[9]: # add up all the estimated rows scanned by each subquery, if estimated rows exists
            counter += x[9]
    print(counter)

# Close MySQL and SSH connections
mydb.close()
tunnel.stop()
