"""
Script to view all users in the database
"""
import mysql.connector
from mysql.connector import Error

def view_users():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='AI_Speech'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Get all users
            cursor.execute("""
                SELECT 
                    user_id,
                    name,
                    email,
                    role,
                    is_active,
                    email_verified,
                    created_at,
                    last_login
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = cursor.fetchall()
            
            print("\n" + "="*100)
            print("ALL USERS IN DATABASE")
            print("="*100)
            
            if users:
                for user in users:
                    print(f"\nUser ID: {user['user_id']}")
                    print(f"Name: {user['name']}")
                    print(f"Email: {user['email']}")
                    print(f"Role: {user['role']}")
                    print(f"Active: {user['is_active']}")
                    print(f"Email Verified: {user['email_verified']}")
                    print(f"Created: {user['created_at']}")
                    print(f"Last Login: {user['last_login']}")
                    print("-" * 100)
                
                print(f"\nTotal Users: {len(users)}")
            else:
                print("\nNo users found in database!")
            
            # Get usage info for each user
            print("\n" + "="*100)
            print("USER USAGE INFORMATION")
            print("="*100)
            
            cursor.execute("""
                SELECT 
                    u.user_id,
                    u.name,
                    u.email,
                    ul.total_uses,
                    ul.remaining_uses,
                    ul.is_premium,
                    ul.last_reset_date
                FROM users u
                LEFT JOIN usage_limits ul ON u.user_id = ul.user_id
                ORDER BY u.created_at DESC
            """)
            
            usage_data = cursor.fetchall()
            
            for data in usage_data:
                print(f"\nUser: {data['name']} ({data['email']})")
                print(f"Total Uses: {data['total_uses']}")
                print(f"Remaining Uses: {data['remaining_uses']}")
                print(f"Premium: {data['is_premium']}")
                print(f"Last Reset: {data['last_reset_date']}")
                print("-" * 100)
            
            # Get subscription info
            print("\n" + "="*100)
            print("ACTIVE SUBSCRIPTIONS")
            print("="*100)
            
            cursor.execute("""
                SELECT 
                    s.subscription_id,
                    u.name,
                    u.email,
                    s.plan_type,
                    s.start_date,
                    s.end_date,
                    s.is_active,
                    s.amount,
                    s.currency
                FROM subscriptions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.is_active = TRUE
                ORDER BY s.start_date DESC
            """)
            
            subscriptions = cursor.fetchall()
            
            if subscriptions:
                for sub in subscriptions:
                    print(f"\nUser: {sub['name']} ({sub['email']})")
                    print(f"Plan: {sub['plan_type']}")
                    print(f"Amount: {sub['amount']} {sub['currency']}")
                    print(f"Start Date: {sub['start_date']}")
                    print(f"End Date: {sub['end_date']}")
                    print("-" * 100)
            else:
                print("\nNo active subscriptions found!")
            
            print("\n" + "="*100)
            print("DEFAULT LOGIN CREDENTIALS")
            print("="*100)
            print("\nAdmin Account:")
            print("  Email: admin@speechclarity.com")
            print("  Password: admin123")
            print("\nNote: Passwords are hashed in the database using bcrypt")
            print("="*100 + "\n")
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    view_users()
