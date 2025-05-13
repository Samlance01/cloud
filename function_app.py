import azure.functions as func 
from azure.data.tables import TableServiceClient
from datetime import datetime
import uuid
import os

app = func.FunctionApp()

@app.function_name(name="SubmitFeedback")
@app.route(route="SubmitFeedback", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON format.", status_code=400)

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return func.HttpResponse(
            "All fields (name, email, message) are required.",
            status_code=400
        )

    try:
        # Connect to Azure Table Storage
        conn_str = os.environ["CUSTOM_STORAGE_CONN"]
        table_service = TableServiceClient.from_connection_string(conn_str)
        table_client = table_service.get_table_client("Feedbacks")

        entry = {
            "PartitionKey": "feedback",
            "RowKey": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }

        table_client.create_entity(entry)

        return func.HttpResponse("Feedback received successfully!", status_code=200)

    except Exception as e:
        return func.HttpResponse(
            f"Error saving feedback: {str(e)}",
            status_code=500
        )
