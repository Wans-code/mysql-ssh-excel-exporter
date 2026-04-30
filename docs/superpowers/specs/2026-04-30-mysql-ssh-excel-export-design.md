# MySQL to Excel Exporter via SSH Design

## Overview
A command-line Python script designed to execute custom SQL queries against a MySQL database over an SSH tunnel and stream the results directly into an Excel file. This tool is optimized for memory efficiency and speed, mirroring the export functionality of database GUI tools like Navicat, but operating in a headless manner.

## Key Features
1.  **SSH Tunneling**: Securely connects to the remote MySQL database using SSH.
2.  **Custom Query Execution**: Reads raw SQL queries from an external `query.sql` file, supporting complex queries including cross-database joins (provided both databases reside on the same server instance).
3.  **Memory-Efficient Exporting**: Uses the chunking technique (streaming data in batches, e.g., 10,000 rows at a time) and `openpyxl`'s `write_only` mode to generate massive Excel files without exhausting system RAM.
4.  **Environment Configuration**: Manages sensitive credentials and connection parameters via a `.env` file.
5.  **Execution Timer**: Measures and logs the total duration of the data extraction and export process.

## Architecture & Data Flow
1.  **Initialization**: Script reads configuration parameters from `.env`.
2.  **Connection Establishment**:
    *   Creates an SSH tunnel using `sshtunnel.SSHTunnelForwarder`.
    *   Establishes a MySQL connection through the tunnel using `pymysql`.
3.  **Query Execution**:
    *   Reads the query string from `query.sql`.
    *   Executes the query using a server-side cursor (`SSCursor`) to stream results from the server instead of buffering everything on the client.
4.  **Excel Generation**:
    *   Initializes an Excel workbook in `openpyxl` using `write_only=True`.
    *   Writes headers based on the cursor description.
    *   Iterates through the data stream, appending rows directly to the disk-backed Excel file.
5.  **Cleanup & Reporting**: Closes the MySQL connection, SSH tunnel, saves the Excel file to the local disk, and outputs the total execution time to the console.

## Components
*   **`.env`**: Stores SSH host, port, username, password/key, MySQL host, port, username, password. (No default DB is required to allow cross-db queries).
*   **`query.sql`**: A text file containing the SQL `SELECT` statement.
*   **`main.py`**: The core execution script.

## Error Handling
*   Validates the existence of `.env` and `query.sql`.
*   Handles SSH connection failures (e.g., timeout, bad credentials).
*   Handles MySQL execution errors (e.g., syntax errors in `query.sql`, permission denied).
*   Gracefully closes all connections even if an exception occurs during the export process.

## Trade-offs & Decisions
*   **Python + Chunking vs. Go**: Chosen Python for ease of maintenance and modification. Mitigated Python's higher memory footprint by strictly utilizing `openpyxl`'s `write-only` mode and cursor chunking.
*   **File-based Query vs. Env Variable**: Chose `query.sql` to support multi-line, complex queries natively without quoting/escaping issues common in `.env` files.
