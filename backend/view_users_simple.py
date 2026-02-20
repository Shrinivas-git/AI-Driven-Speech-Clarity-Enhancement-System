"""
Simple script to view all users in the database
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
            
            print("\n" + "="*100)
            print("ALL USERS IN DATABASE")
            print("="*100)
            
            # Get all users
            cursor.execute("""
                SELECT 
                    user_id,
                    name,
                    email,
                    password_hash,
                    role,
                    is_active,
                    email_verified,
                    is_premium,
                    total_uses,
                    remaining_uses,
                    created_at,
                    last_login
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = cursor.fetchall()
            
            if users:
                for i, user in enumerate(users, 1):
                    print(f"\n{'='*100}")
                    print(f"USER #{i}")
                    print(f"{'='*100}")
                    print(f"User ID:         {user['user_id']}")
                    print(f"Name:            {user['name']}")
                    print(f"Email:           {user['email']}")
                    print(f"Password Hash:   {user['password_hash'][:50]}... (hashed with bcrypt)")
                    print(f"Role:            {user['role']}")
                    print(f"Active:          {'Yes' if user['is_active'] else 'No'}")
                    print(f"Email Verified:  {'Yes' if user['email_verified'] else 'No'}")
                    print(f"Premium:         {'Yes' if user['is_premium'] else 'No'}")
                    print(f"Total Uses:      {user['total_uses']}")
                    print(f"Remaining Uses:  {user['remaining_uses']}")
                    print(f"Created:         {user['created_at']}")
                    print(f"Last Login:      {user['last_login'] if user['last_login'] else 'Never'}")
                
                print(f"\n{'='*100}")
                print(f"TOTAL USERS: {len(users)}")
                print(f"{'='*100}")
            else:
                print("\nNo users found in database!")
            
            # Show login credentials
            print("\n" + "="*100)
            print("LOGIN CREDENTIALS")
            print("="*100)
            print("\n1. Admin Account:")
            print("   Email:    admin@speechclarity.com")
            print("   Password: admin123")
            print("   Role:     ADMIN")
            print("   Uses:     Unlimited (999999)")
            
            if len(users) > 1:
                print("\n2. Other Registered Users:")
                for user in users:
                    if user['email'] != 'admin@speechclarity.com':
                        print(f"\n   Email:    {user['email']}")
                        print(f"   Name:     {user['name']}")
                        print(f"   Role:     {user['role']}")
                        print(f"   Premium:  {'Yes' if user['is_premium'] else 'No'}")
                        print(f"   Uses:     {user['remaining_uses']}/{user['total_uses']}")
            
            print("\n" + "="*100)
            print("NOTE: All passwords are securely hashed using bcrypt")
            print("      You cannot see the plain text passwords in the database")
            print("="*100 + "\n")
            
            # Show table structure
            print("\n" + "="*100)
            print("DATABASE TABLES")
            print("="*100)
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\nTables in AI_Speech database:")
            for table in tables:
                table_name = list(table.values())[0]
                print(f"  - {table_name}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                print(f"    Rows: {count}")
            
            print("\n" + "="*100 + "\n")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    view_users()
