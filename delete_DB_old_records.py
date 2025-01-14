import psycopg2
from datetime import datetime, timedelta

# Database credentials
DB_HOST = "fileshare.cds4iww2su3w.eu-north-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "fileshare"
DB_USER = "mysuperuser"
DB_PASSWORD = "mysuperuser"

# Table and column configuration
TABLE_NAME = "files_fileupload"  # Replace with your table name
TIMESTAMP_COLUMN = "uploaded_at"  # Replace with the timestamp column name

def delete_old_entries():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = connection.cursor()

        # Calculate the cutoff timestamp (72 hours ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=72)

        # Delete entries older than 24 hours
        delete_query = f"""
        DELETE FROM {TABLE_NAME}
        WHERE {TIMESTAMP_COLUMN} < %s;
        """
        cursor.execute(delete_query, (cutoff_time,))
        connection.commit()

        print(f"Deleted rows older than {cutoff_time} from table {TABLE_NAME}.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Trigger the function
if __name__ == "__main__":
    delete_old_entries()



# Open the Crontab File:
# crontab -e


# Add a Cron Job: Add the following line at the bottom of the file to schedule the script to run every 6 hours:
# 0 */6 * * * /usr/bin/python3 /home/ubuntu/filesharing/delete_DB_old_records.py >> /home/ec2-user/delete_old_entries.log 2>&1


# Verify the Cron Job: List scheduled cron jobs to confirm:
# crontab -l


# for analytics
# <!-- https://analytics.google.com/analytics/web/#/a324778647p453750898/admin/streams/table/ -->