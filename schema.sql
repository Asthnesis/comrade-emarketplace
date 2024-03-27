create table user(
user_id varchar(25),
primary key (user_id)
);
create table User_Account(
email varchar(50),
user_id varchar(25) not null,
first_name varchar(50) not null,
last_name varchar(50) not null,
primary key (email)
);
create table Buyer(
buyer_id varchar(25),
primary key (buyer_id)
);
create table Seller(
seller_id varchar(25),
description varchar(1000) not null,
items_sold integer not null,
primary key (seller_id)
);
create table Product(
product_id varchar(20),
prod_name varchar(100) not null,
condition varchar(10),
description varchar(500),
available_units integer not null,
seller_id varchar(25) not null,
sub_cat_id integer not null,
primary key (product_id)
);
create table Product_Images(
product_id varchar(20),
product_image varchar(500) not null,
primary key (product_id)
);
create table Buyer_Reviews_Product(
buyer_id varchar(25),
product_id varchar(20),
rating char(1),
buyer_comment varchar(500),
primary key (buyer_id, product_id)
);
create table Buyer_Reviews_Seller(
buyer_id varchar(25),
seller_id varchar(25),
rating char(1) not null,
buyer_comment varchar(500),
primary key (buyer_id, seller_id)
);
create table Cart(
buyer_id varchar(20),
quantity integer not null,
total_price integer not null,
primary key (buyer_id)
);
create table Cart_Contains_Product(
product_id varchar(20),
buyer_id varchar(20),
primary key (buyer_id, product_id)
);
create table Watches(
product_id varchar(20),
buyer_id varchar(20),
primary key (buyer_id, product_id)
);
create table Category(
cat_id integer,
category_name varchar(20) not null,
primary key (cat_id)
);
create table Sub_Category(
sub_cat_id integer,
sub_category_name varchar(20) not null,
product_id varchar(20) not null,
primary key (sub_cat_id)
);
create table Category_Has_Sub_Category(
sub_cat_id integer,
cat_id integer,
primary key (sub_cat_id, cat_id)
);
create table Buyer_Order(
order_id varchar(20),
order_status varchar(20) default 'created',
order_date date default sysdate,
buyer_id varchar(25) not null,
contact_id integer not null,
primary key (order_id)
);
create table Order_Has_Product(
product_id varchar(20),
order_id varchar(20),
selling_price integer not null,
quantity integer not null,
primary key (product_id, order_id)
;)
ALTER TABLE User_Account ADD CONSTRAINT fk_user_account_user_id FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE;

ALTER TABLE Product ADD CONSTRAINT fk_product_seller_id FOREIGN KEY (seller_id) REFERENCES Seller(seller_id);

ALTER TABLE Product ADD CONSTRAINT fk_product_sub_cat_id FOREIGN KEY (sub_cat_id) REFERENCES Sub_Category(sub_cat_id);

ALTER TABLE Product_Images ADD CONSTRAINT fk_product_images_product_id FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Buyer_Reviews_Product ADD CONSTRAINT fk_buyer_reviews_product_buyer_id FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id);

ALTER TABLE Buyer_Reviews_Product ADD CONSTRAINT fk_buyer_reviews_product_product_id FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Buyer_Reviews_Seller ADD CONSTRAINT fk_buyer_reviews_seller_seller_id FOREIGN KEY (seller_id) REFERENCES Seller(seller_id);

ALTER TABLE Buyer_Reviews_Seller ADD CONSTRAINT fk_buyer_reviews_seller_buyer_id FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id);

ALTER TABLE Cart ADD CONSTRAINT fk_cart_buyer_id FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id);

ALTER TABLE Cart_Contains_Product ADD CONSTRAINT fk_cart_contains_product_buyer_id FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id);

ALTER TABLE Cart_Contains_Product ADD CONSTRAINT fk_cart_contains_product_product_id FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Watches ADD CONSTRAINT fk_watches_product_id FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Watches ADD CONSTRAINT fk_watches_buyer_id FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id);

ALTER TABLE Sub_Category ADD CONSTRAINT fk_sub_category_product_id FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Category_Has_Sub_Category ADD CONSTRAINT fk_category_has_sub_category_sub_cat_id FOREIGN KEY (sub_cat_id) REFERENCES Sub_Category(sub_cat_id);

ALTER TABLE Category_Has_Sub_Category ADD CONSTRAINT fk_category_has_sub_category_cat_id FOREIGN KEY (cat_id) REFERENCES Category(cat_id);

ALTER TABLE Buyer_Order ADD CONSTRAINT fk_buyer_order_buyer_id FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id);

ALTER TABLE Order_Has_Product ADD CONSTRAINT fk_order_has_product_product_id FOREIGN KEY (product_id) REFERENCES Product(product_id);

ALTER TABLE Order_Has_Product ADD CONSTRAINT fk_order_has_product_order_id FOREIGN KEY (order_id) REFERENCES Buyer_Order(order_id);

CREATE TABLE Payment (
    payment_id INT PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP,
    payer_id VARCHAR(25),  -- ID of the payer (buyer)
    receiver_id VARCHAR(25),  -- ID of the receiver (seller)
    payment_method VARCHAR(50),  -- Payment method (e.g., M-pesa)
    status VARCHAR(20),  -- Payment status (e.g., pending, completed)
    FOREIGN KEY (payer_id) REFERENCES Buyer(buyer_id),
    FOREIGN KEY (receiver_id) REFERENCES Seller(seller_id)
);

CREATE TABLE Wishlist (
    wishlist_id INTEGER PRIMARY KEY,
    user_id VARCHAR(25) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    added_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);
