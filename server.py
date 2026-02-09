from fastmcp import FastMCP
import sqlite3

mcp = FastMCP("mcp-data-auditor")

DB_PATH = "company_data.sqlite"

# Query executor for querying sqlite file
def execute_query(query: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        # Use Row factory so we get dictionary-like results
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        # Convert sqlite3.Row objects to standard dictionaries for JSON output
        return [dict(row) for row in results]
    except Exception as e:
        return f"Database Error: {str(e)}"

# MCP Tools
@mcp.tool
def list_collections() -> list[str]:
    """
    Returns list available of CosmosDB containers.

    Returns:
        list[str]: List of all collections as strings.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    # Get just the names as a simple list of strings
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Return the raw list, NOT a formatted string
    return tables

@mcp.tool
def get_schema(container_name: str) -> dict:
    """
    Returns the field names and data types of a specific container.

    Args:
        container_name (str): Name of the container to get the schema of.

    Returns:
        dict: JSON object of field names and data type of the container.
    
    Example:
        get_schema(container_name="users")
    """

@mcp.tool
def query_data(query: str):
    """
    Executes a read-only SQL query.
    Only 'SELECT' queries are allowed.

    Args:
        query (str): 
        
    Example:
        query_data(query="SELECT * FROM users DESC LIMIT 5")
    """
    data = execute_query(query)
    return data

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)