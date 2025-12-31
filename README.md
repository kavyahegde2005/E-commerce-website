**🛒 E‑Commerce Website**
**📌 Overview**

This project is a simple e‑commerce web application built with Flask (Python) and MySQL.
It allows users to register, log in, browse products, add items to their cart/wishlist, and place orders.

**⚙️ Prerequisites**
Python 3.x
Flask framework
MySQL Workbench
Basic knowledge of HTML, CSS, and Python

**📌 Database Setup (MySQL Workbench)**

First, open MySQL Workbench and create a new schema called e_commerce.
Then, inside this database, create tables such as users (to store account details), products (to store items for sale), orders (to track purchases), and order_items (to list products inside each order).
Each table should have a primary key, and you can link them with foreign keys (for example, orders are linked to users, and order_items are linked to both orders and products).
After creating the tables, refresh the schema to see them listed, and you can start inserting sample data to test your e‑commerce app.
