import mysql.connector
from mysql.connector import Error
import csv
from datetime import datetime, timedelta
import argparse

# Database connection configuration
db_config = {
    'host': 'localhost',
    'database': 'mydb',
    'user': 'root',
    'password': 'root'  # add your password if needed
}

def create_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_daily_stats(connection, start_date, end_date):
    """Get daily statistics for the specified period"""
    cursor = connection.cursor(dictionary=True,buffered=True)
    stats = {}
    
    try:
        # Get thread counts per day for percentage calculation
        thread_counts = {}
        cursor.execute("""
            SELECT DATE(action_time) as day, COUNT(DISTINCT threads_id) as count
            FROM actions
            WHERE actions_type_id = 5 AND response_type_id = 1
            AND action_time BETWEEN %s AND %s
            GROUP BY DATE(action_time)
            ORDER BY day
        """, (start_date, end_date))
        thread_counts = {row['day']: row['count'] for row in cursor.fetchall()}
        
        # Get initial thread count before start date
        cursor.execute("""
            SELECT COUNT(DISTINCT threads_id) as count
            FROM actions
            WHERE actions_type_id = 5 
            AND response_type_id = 1
            AND action_time < %s
        """, (start_date,))
        prev_thread_count = cursor.fetchone()['count'] if cursor.rowcount > 0 else 0
        
        current_date = start_date
        while current_date <= end_date:
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = day_start + timedelta(days=1)
            
            # Get new accounts created
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM actions
                WHERE actions_type_id = 2 AND response_type_id = 1
                AND action_time BETWEEN %s AND %s
            """, (day_start, day_end))
            new_accounts = cursor.fetchone()['count']
            
            # Get message statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_messages,
                    SUM(CASE WHEN users_id IS NULL THEN 1 ELSE 0 END) as anonymous_messages
                FROM actions
                WHERE actions_type_id = 8
                AND action_time BETWEEN %s AND %s
            """, (day_start, day_end))
            messages = cursor.fetchone()
            total_messages = messages['total_messages'] or 0
            anonymous_percent = (messages['anonymous_messages'] / total_messages * 100) if total_messages > 0 else 0
            
            # Calculate thread count change
            current_thread_count = thread_counts.get(current_date, 0)
            thread_change_percent = 0
            if prev_thread_count > 0:
                thread_change_percent = ((current_thread_count - prev_thread_count) / prev_thread_count) * 100
            
            # Store stats
            stats[current_date] = {
                'new_accounts': new_accounts,
                'anonymous_messages_percent': round(anonymous_percent, 2),
                'total_messages': total_messages,
                'thread_change_percent': round(thread_change_percent, 2)
            }
            
            prev_thread_count += (current_thread_count - prev_thread_count)
            current_date += timedelta(days=1)
            
    finally:
        cursor.close()
    
    return stats

def save_to_csv(stats, filename):
    """Save statistics to CSV file"""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['day', 'new_accounts', 'anonymous_messages_percent', 
                     'total_messages', 'thread_change_percent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for day, data in sorted(stats.items()):
            row = {'day': day.strftime('%Y-%m-%d')}
            row.update(data)
            writer.writerow(row)
    
    print(f"Statistics saved to {filename}")

def parse_date(date_str):
    """Parse date from string in YYYY-MM-DD format"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def main():
    """Main function to process command line arguments and generate report"""
    parser = argparse.ArgumentParser(description='Generate forum statistics report')
    parser.add_argument('--start', type=parse_date, required=True,
                       help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end', type=parse_date, required=True,
                       help='End date in YYYY-MM-DD format')
    parser.add_argument('--output', type=str, default='forum_stats.csv',
                       help='Output CSV filename (default: forum_stats.csv)')
    
    args = parser.parse_args()
    
    if args.start > args.end:
        print("Error: Start date must be before end date")
        return
    
    connection = create_db_connection()
    if not connection:
        return
    
    try:
        stats = get_daily_stats(connection, args.start, args.end)
        save_to_csv(stats, args.output)
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main()