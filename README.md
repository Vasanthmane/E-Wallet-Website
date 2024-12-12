# E-Wallet-Website
A digital wallet system designed to simulate functionalities similar to Venmo or Zelle, allowing users to manage accounts, send/receive money, request payments, and generate transaction statements. This project provides a comprehensive solution for managing financial transactions, user details, and bank accounts within a simple, menu-driven application.
# Features:

    User Account Management: Allows users to create and modify accounts, including adding phone numbers, email addresses, and bank account details.
    Money Transfer: Users can send and request money via email or phone number, with real-time balance validation and transaction recording.
    Transaction Management: Each transaction (send/request) is recorded and linked to the user's account for transparency and tracking.
    Monthly Statements: Users can view monthly statements showing sent and received transactions, with aggregated statistics for financial analysis.
    Advanced Search: Search transactions by SSN, email, phone number, type, or date range.
    Optimized Database: The backend uses relational tables to maintain data integrity, with optimized queries for performance.

# Technologies Used:

    Backend: Python with SQLite for data storage.
    Database: SQL commands to create and manage tables such as users, bank accounts, transactions, and monthly statements.
    Transaction Management: Stored procedures for real-time balance checks and validations.
    Database Integrity: Cascading updates/deletes and foreign key constraints for referential integrity.

# Setup and Installation:

# Clone the repository:

git clone https://github.com/Vasanthmane/E-Wallet-Website.git

# Install necessary dependencies:

pip install -r requirements.txt

# Run the application:

    python app.py

# Challenges and Solutions:

    Data Integrity: Ensured referential integrity using cascading updates/deletes.
    Concurrent Access: Managed simultaneous operations with database transaction isolation levels to prevent deadlock.
    Complex Queries: Optimized queries using GROUP BY and ORDER BY for monthly summaries and top user identification.

# Future Improvements:

    Real-time transaction notifications.
    Multi-factor authentication for secure access.
    Enhanced transaction validation to include fraud detection mechanisms.

