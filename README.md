# Student eCommerce Platform
This Flask-based eCommerce platform allows students to buy and sell goods to each other in a user-friendly environment. The platform features Google sign-up/sign-in functionality, making it easy for students to get started.

## Features
User Authentication: Students can sign up and sign in using their Google accounts.

Buyer Dashboard: View available products, add items to the cart, and proceed to checkout using M-Pesa.

Seller Dashboard: Manage products, view orders, and track sales (currently under development).

M-Pesa Integration: A seamless payment process through M-Pesa for quick and secure transactions.

### Incomplete Features
The seller's dashboard does not display correctly.

The cart functionality has issues.

Contact information handling is incomplete.

The checkout process, including the transfer of funds to sellers, is not fully implemented.

### Installation
Clone the repository: <https://github.com/Asthnesis/comrade-emarketplace>

Set up a virtual environment.

Install dependencies using pip install -r requirements.txt.

Set up the database using the provided SQL scripts. 

Configure your web server (e.g., Apache or Nginx) to point to the project directory. 

Update the database connection settings in the config.php file.

Set up the Google OAuth credentials <https://developers.google.com/identity/protocols/oauth2>

Set up the M-pesa API using the Daraja API <https://developer.safaricom.co.ke/APIs>

Run the Flask app using flask run.

### Contribution
Feel free to fork the project, submit issues, or contribute to the development of missing features!

