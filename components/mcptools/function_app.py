import azure.functions as func
import logging
import datetime
import os
import json
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

#app = func.FunctionApp()

# The main function is the entry point for the Azure Function App. It initializes the necessary clients and resources, and then yields control to the function handlers.

# The function handlers are defined using the @app.mcp_tool() decorator, which registers them as tools that can be invoked by the MCP . Each handler takes a context parameter, which contains information about the invocation and allows access to the app state.


# The get_blob_service_client function is a helper function that creates and returns a BlobServiceClient using the AzureWebJobsStorage connection string from the environment variables.
def get_blob_service_client():
    """Helper function to get BlobServiceClient using identity-based auth or connection string."""
    blob_service_uri = os.getenv("AzureWebJobsStorage__blobServiceUri")
    if blob_service_uri:
        logging.info("Using identity-based authentication")
        return BlobServiceClient(account_url=blob_service_uri, credential=DefaultAzureCredential())

    connection_string = os.getenv("AzureWebJobsStorage")
    if connection_string and not connection_string.startswith("https://"):
        logging.info("Using connection string authentication")
        return BlobServiceClient.from_connection_string(connection_string)

    raise ValueError("Storage connection not configured. Set AzureWebJobsStorage__blobServiceUri or AzureWebJobsStorage.")

@app.mcp_tool()
def list_vbd() -> str:
    """List VBDs and price from Azure Blob Storage."""
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client("vbd-data")
        
        # check if container exists
        if not container_client.exists():
            logging.error("Container 'vbd-data' does not exist.")
            return json.dumps({
                "error": "Container 'vbd-data' does not exist.",
                "vbd_list": []
            })
        
        # list all blobs in the container
        blob_list = container_client.list_blobs()
        vbds = []

        for blob in blob_list:
            if blob.name.endswith(".json"):
                # download the blob content and parse it as JSON
                blob_client = container_client.get_blob_client(blob.name)
                blob_data = blob_client.download_blob().readall().decode("utf-8")
                vbd = json.loads(blob_data)
                vbds.append(vbd)
        logging.info(f"Found {len(vbds)} VBDs in the container.")
        return json.dumps({
            "count": len(vbds),
            "vbds": vbds
        }, indent=2)
    except Exception as e:
        logging.error(f"Error listing VBDs: {e}")
        return json.dumps({
            "error": f"Failed to list VBDs: {str(e)}",
            "vbds": []
        })


@app.mcp_tool()
def dispatch_vbd(name: str, item: str, quantity: str) -> str:
    """Place a VBD dispatch order.
    
    Args:
        name: Account name for the order.
        item: Product item to order.
        quantity: Quantity of the item to order.
    """
    try:
        # Convert quantity to integer
        try:
            quantity_int = int(quantity)
            if quantity_int <= 0:
                return json.dumps({"error": "Quantity must be a positive number"})
        except ValueError:
            return json.dumps({"error": "Quantity must be a valid number"})
        
        blob_service_client = get_blob_service_client()
        
        # Get VBD price from VBD container
        vbd_container = blob_service_client.get_container_client("vbd-data")
        
        if not vbd_container.exists():
            return json.dumps({"error": "VBD container not found"})
        
        # Find the VBD
        vbd_found = False
        vbd_price = 0
        vbd_info = None
        
        blobs = vbd_container.list_blobs()
        for blob in blobs:
            if blob.name.endswith(".json"):
                blob_client = vbd_container.get_blob_client(blob.name)
                vbd_data = json.loads(blob_client.download_blob().readall().decode("utf-8"))
                
                # Check if this is the product we're looking for (case-insensitive match)
                vbd_name = vbd_data.get("name", "").lower()
                if vbd_name == item.lower() or blob.name.replace(".json", "").lower() == item.lower():
                    vbd_found = True
                    vbd_price = float(vbd_data.get("price", 0))
                    vbd_info = vbd_data
                    break
        
        if not vbd_found:
            return json.dumps({"error": f"VBD '{item}' not found"})
        
        # Calculate total price
        total_price = vbd_price * quantity_int
        
        # Create order data
        order_data = {
            "customer_name": name,
            "item": vbd_info.get("name", item),
            "quantity": quantity_int,
            "unit_price": vbd_price,
            "total_price": total_price,
            "order_date": datetime.datetime.utcnow().isoformat() + "Z"
        }
        
        # Save order to Orders container
        orders_container = blob_service_client.get_container_client("orders")
        
        # Create container if it doesn't exist
        if not orders_container.exists():
            orders_container.create_container()
            logging.info("Created Orders container")
        
        # Generate unique filename with timestamp
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        order_filename = f"order_{timestamp}.json"
        
        # Upload order to blob storage
        blob_client = orders_container.get_blob_client(order_filename)
        blob_client.upload_blob(json.dumps(order_data, indent=2), overwrite=True)
        
        logging.info(f"Order placed: {order_filename}")
        
        return json.dumps({
            "success": True,
            "message": f"Order placed successfully for {name}",
            "order": order_data,
            "order_id": order_filename
        }, indent=2)
        
    except Exception as e:
        logging.error(f"Error placing order: {e}")
        return json.dumps({
            "error": f"Failed to place order: {str(e)}"
        })


@app.mcp_tool()
def list_dispatch() -> str:
    """List all VBD orders"""
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client("orders")
        
        # Check if container exists
        if not container_client.exists():
            logging.info("VBD orders container does not exist yet - no orders placed")
            return json.dumps({
                "count": 0,
                "orders": [],
                "message": "No VBD orders have been placed yet"
            })
        
        # List all blobs in the VBD Orders container
        blobs = container_client.list_blobs()
        
        orders = []
        for blob in blobs:
            if blob.name.endswith(".json"):
                # Download and parse each order JSON file
                blob_client = container_client.get_blob_client(blob.name)
                order_data = json.loads(blob_client.download_blob().readall().decode("utf-8"))
                order_data["order_id"] = blob.name  # Add the filename as order_id
                orders.append(order_data)
        
        # Sort orders by date (most recent first)
        orders.sort(key=lambda x: x.get("order_date", ""), reverse=True)
        
        logging.info(f"Found {len(orders)} orders")
        
        return json.dumps({
            "count": len(orders),
            "orders": orders
        }, indent=2)
        
    except Exception as e:
        logging.error(f"Error listing orders: {e}")
        return json.dumps({
            "error": f"Failed to list orders: {str(e)}",
            "orders": []
        })