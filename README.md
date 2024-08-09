*******Shopping Platform*******
Overview
The Simple Shopping Platform is a web application designed to manage users and products efficiently.
Built using Flask, this application includes robust features such as user authentication, product management, and email notifications.
It uses MySQL as the database and leverages JWT for secure authentication.

**Features**
User Authentication:

 --> Registration and login functionality with JWT-based session management.
 --> Password hashing and validation for security.
 
Product Management:

 --> Add, view, and manage products.
 --> Pagination for product listings.
 
Email Notifications:

 --> Send welcome emails upon user registration.
 --> Notify users via email when a new product is added.
 
*Tech Stack*

 * Backend: Flask
 * Database: MySQL with SQLAlchemy ORM
 * Authentication: JWT (JSON Web Tokens)
 * Email: Flask-Mail
 * Environment Management: python-dotenv
 * Frontend: HTML/CSS (Bootstrap optional)

Installation:
Prerequisites
 --> Python 3.x
 --> MySQL server


*****API Endpoints*****

*User Registration*

 --> Endpoint: /users
 --> Method: POST
 --> Body: { "firstName": "John", "lastName": "Doe", "username": "johndoe", "email": "your@example.com", "password": "Password123!", "confirm_password": "Password123!" }
 --> Response: { "message": "User account created" }
 
*User Login*

 --> Endpoint: /login
 --> Method: POST
 --> Body: { "username": "johndoe", "password": "Password123!" }
 --> Response: { "status": true, "message": "Login successful.", "access_token": "your_jwt_token" }
 
*Add Product*

 --> Endpoint: /products
 --> Method: POST
 --> Headers: Authorization: Bearer <your_jwt_token>
 --> Body: { "product_name": "Product Name", "description": "Product Description", "price": 29.99 }
 --> Response: { "message": "Product added" }
 
*Display Products*

 --> Endpoint: /products
 --> Method: GET
 --> Query Parameters: page, per_page
 --> Response: { "status": true, "data": [ { "product_id": 1, "product_name": "Product Name", "description": "Product Description", "price": 29.99 } ], "total": 10, "pages": 1, "current_page": 1, "per_page": 10 }
 
*Contributing*
 * Fork the repository.
 * Create a feature branch (git checkout -b feature/your-feature).
 * Commit your changes (git commit -am 'Add some feature').
 * Push to the branch (git push origin feature/your-feature).
 * Open a pull request.

**Contact**

For any questions or feedback, please contact neevarp02082003@gmail.com.
