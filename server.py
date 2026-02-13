from fastmcp import FastMCP
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import os

mcp = FastMCP("mcp-data-auditor")

# Cosmos Database environmental variables
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
DATABASE_NAME = os.getenv("COSMOS_DATABASE_NAME")

# Use Azure Credential to access database
credential = DefaultAzureCredential()
client = CosmosClient(COSMOS_ENDPOINT, credential=credential)
database = client.get_database_client(DATABASE_NAME)


def execute_query(container_name: str, query: str) -> list[dict] | str:
    """
    Helper function for executing NoSQL queries.

    Args:
        container_name (str): Name of container to execute query in.
        query (str): NoSQL query to execute.

    Returns:
        list[dict] | str: List of objects returned from executing NoSQL query. Returns string in error case.
    """
    try:
        container = database.get_container_client(container_name)
        items = list(
            container.query_items(query=query, enable_cross_partition_query=True)
        )
        return items
    except Exception as e:
        return f"CosmosDB Error: {str(e)}"


# MCP Tools
@mcp.tool
def list_collections() -> list[str]:
    """
    Returns list available of CosmosDB containers.

    Returns:
        list[str]: List of all collections as strings.
    """
    containers = list(database.list_containers())
    return [c["id"] for c in containers]


@mcp.tool
def get_schema(container_name: str) -> dict:
    """
    Returns the field names and data types of a specific container by infering the most recent document.

    Args:
        container_name (str): Name of the container to get the schema of.

    Returns:
        dict: JSON object of field names and data type of the container.

    Example:
        get_schema(container_name="users")
    """
    try:
        container = database.get_container_client(container_name)
        # Get first document to get fields of
        query = "SELECT TOP 1 * FROM c"
        items = list(
            container.query_items(query=query, enable_cross_partition_query=True)
        )

        if not items:
            return {"message": "Container is empty; no schema found."}

        # Extract keys and types
        sample = items[0]
        schema = {
            key: type(value).__name__
            for key, value in sample.items()
            if not key.startswith("_")
        }
        return {"container": container_name, "fields": schema}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool
def query_data(container_name: str, query: str):
    """
    Executes a read-only SQL query.
    Only 'SELECT' queries are allowed.

    Args:
        container_name (str): Name of container to execute query in.
        query (str): NoSQL query to execute.

    Example:
        query_data(container_name="users", query="SELECT * FROM c WHERE c.active = true")
    """
    data = execute_query(container_name, query)
    return data


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
