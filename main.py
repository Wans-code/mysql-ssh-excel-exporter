import os
import json
import time
import pymysql
import openpyxl
from datetime import datetime
from sshtunnel import SSHTunnelForwarder

def load_connections():
    config_file = 'connections.json'
    if not os.path.exists(config_file):
        print(f"Error: {config_file} tidak ditemukan.")
        print("Silakan buat file connections.json terlebih dahulu (Anda bisa copy dari connections.json.example)")
        return None
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error membaca {config_file}: {e}")
        return None

def main():
    connections = load_connections()
    if not connections:
        return

    print("=== MySQL to Excel Export via SSH ===")
    print("Daftar koneksi yang tersedia:")
    for key in connections.keys():
        print(f" - {key}")
    print("=====================================")
    
    selected_key = input("Ketik nama koneksi yang ingin digunakan (misal: pbb_kab_cianjur): ").strip()
    
    if selected_key not in connections:
        print(f"Error: Koneksi '{selected_key}' tidak ditemukan di connections.json!")
        return

    config = connections[selected_key]
    
    print(f"\nMenggunakan koneksi: {selected_key}")

    # Record start time
    start_time = time.time()
    
    # Configuration
    SSH_HOST = config.get("SSH_HOST")
    SSH_PORT = int(config.get("SSH_PORT", 22))
    SSH_USER = config.get("SSH_USER")
    SSH_PASSWORD = config.get("SSH_PASSWORD")
    SSH_KEY_PATH = config.get("SSH_KEY_PATH")

    DB_HOST = config.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(config.get("DB_PORT", 3306))
    DB_USER = config.get("DB_USER")
    DB_PASSWORD = config.get("DB_PASSWORD")
    
    CHUNK_SIZE = int(config.get("CHUNK_SIZE", 10000))

    # Read Query
    try:
        with open('query.sql', 'r') as f:
            query = f.read().strip()
    except Exception as e:
        print(f"Error reading query.sql: {e}")
        return

    if not query:
        print("query.sql is empty. Please provide a query in the file.")
        return

    print("Opening SSH Tunnel...")
    server = None
    conn = None
    
    try:
        # Setup SSH Tunnel
        tunnel_args = {
            'ssh_address_or_host': (SSH_HOST, SSH_PORT),
            'ssh_username': SSH_USER,
            'remote_bind_address': (DB_HOST, DB_PORT)
        }
        
        if SSH_KEY_PATH:
            tunnel_args['ssh_pkey'] = SSH_KEY_PATH
        elif SSH_PASSWORD:
            tunnel_args['ssh_password'] = SSH_PASSWORD
        else:
            raise ValueError("Either SSH_PASSWORD or SSH_KEY_PATH must be set in connections.json")

        server = SSHTunnelForwarder(**tunnel_args)
        server.start()
        print(f"SSH Tunnel opened on local port {server.local_bind_port}")

        # Setup MySQL Connection
        print("Connecting to MySQL Database...")
        conn = pymysql.connect(
            host='127.0.0.1',
            port=server.local_bind_port,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.SSCursor # Important for streaming large results
        )

        print("Executing Query...")
        with conn.cursor() as cursor:
            cursor.execute(query)
            
            # Setup Excel Workbook in write-only mode (memory efficient)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Automatically prefix the output file with the connection name
            excel_filename = f"export_{selected_key}_{timestamp}.xlsx"
            wb = openpyxl.Workbook(write_only=True)
            ws = wb.create_sheet("Data")
            
            # Write Header
            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
                ws.append(column_names)
            else:
                print("Warning: Query did not return any column descriptions.")
            
            print(f"Fetching data in chunks of {CHUNK_SIZE} and writing to {excel_filename}...")
            total_rows = 0
            
            while True:
                results = cursor.fetchmany(CHUNK_SIZE)
                if not results:
                    break
                
                for row in results:
                    ws.append(row)
                
                total_rows += len(results)
                print(f"  Processed {total_rows} rows...")
            
            wb.save(excel_filename)
            print(f"Export successful! Total rows exported: {total_rows}")
            print(f"File saved as: {excel_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn and conn.open:
            conn.close()
            print("MySQL connection closed.")
        if server and server.is_active:
            server.stop()
            print("SSH Tunnel closed.")
            
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"\nTotal Execution Time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()
