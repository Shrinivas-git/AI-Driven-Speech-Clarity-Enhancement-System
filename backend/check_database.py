"""
Check database structure and view users
"""
import mysql.connector
from mysql.connector import Error

def check_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='AI_Speech'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("\n" + "="*100)
            print("DATABASE STRUCTURE")
            print("="*100)
            
            # Show all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\nTables in AI_Speech database:")
            for table in tables:
                table_name = list(table.values())[0]
                print(f"\n  Table: {table_name}")
                
                # Show columns
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                print("  Columns:")
                for col in columns:
                    print(f"    - {col['Field']} ({col['Type']}) {col['Key']} {col['Null']} {col['Default']}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                print(f"  Total Rows: {count}")
            
            # Now get users with correct columns
            print("\n" + "="*100)
            print("USERS IN DATABASE")
            print("="*100)
            
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            users = cursor.fetchall()
            
            if users:
                for i, user in enumerate(users, 1):
                    print(f"\n{'='*100}")
                    print(f"USER #{i}")
                    print(f"{'='*100}")
                    for key, value in user.items():
                        if key == 'password_hash':
                            print(f"{key:20s}: {str(value)[:50]}... (bcrypt hashed)")
                        else:
                            print(f"{key:20s}: {value}")
                
                print(f"\n{'='*100}")
                print(f"TOTAL USERS: {len(users)}")
                print(f"{'='*100}")
            
            # Show login info
            print("\n" + "="*100)
            print("LOGIN CREDENTIALS")
            print("="*100)
            print("\nAdmin Account:")
            print("  Email:    admin@speechclarity.com")
            print("  Password: admin123")
            print("\nNote: Passwords are hashed with bcrypt in the database")
            print("="*100 + "\n")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_database()
