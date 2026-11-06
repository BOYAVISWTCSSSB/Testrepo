import logging, os, time
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware
from starlette.responses import PlainTextResponse
from api_app import app as banking_api
load_dotenv(Path(__file__).resolve().parent / ".env")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("mcp")


class ToolLogger(Middleware):
    """Logs each tool call so you can watch the agent hitting the server."""
    async def on_call_tool(self, context, call_next):
        name, args = context.message.name, context.message.arguments
        start = time.perf_counter()
        log.info("CALL  %s args=%s", name, args)
        try:
            result = await call_next(context)
            log.info("OK    %s (%.0f ms)", name, (time.perf_counter() - start) * 1000)
            return result
        except Exception as e:
            log.error("FAIL  %s: %s", name, e)
            raise


mcp = FastMCP.from_fastapi(app=banking_api, name="SSB Bank MCP Server")
mcp.add_middleware(ToolLogger())


@mcp.tool()
def list_test_statement_files(container_name: str = "test-statements") -> list[str]:
    """Return the blob file names in the Azure Blob Storage container.

    This is a sample MCP tool that reads files from the configured Azure storage account
    and returns the names of all blobs currently present in the requested container.
    """
    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    if not account_url:
        raise ValueError(
            "AZURE_STORAGE_ACCOUNT_URL is not set. Example: https://<account>.blob.core.windows.net"
        )

    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
    credential = account_key if account_key else DefaultAzureCredential()
    blob_service = BlobServiceClient(account_url=account_url, credential=credential)

    candidate_containers = [container_name]
    if container_name == "test-statments":
        candidate_containers.append("test-statements")
    elif container_name == "test-statements":
        candidate_containers.append("test-statments")

    for candidate in candidate_containers:
        container_client = blob_service.get_container_client(candidate)
        if container_client.exists():
            blob_names = [blob.name for blob in container_client.list_blobs()]
            return blob_names

    available = [c.name for c in blob_service.list_containers()]
    raise ValueError(
        f"Container '{container_name}' does not exist. "
        f"Available containers: {available if available else 'none'}"
    )


@mcp.tool()
def read_test_statement_file(file_name: str, container_name: str = "test-statements") -> str:
    """Read a .txt blob file from the Azure Storage container and return its content as text."""
    if not file_name or not file_name.strip():
        raise ValueError("file_name must be provided and cannot be empty.")

    if not file_name.lower().endswith(".txt"):
        raise ValueError("file_name must point to a .txt file.")

    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    if not account_url:
        raise ValueError(
            "AZURE_STORAGE_ACCOUNT_URL is not set. Example: https://<account>.blob.core.windows.net"
        )

    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
    credential = account_key if account_key else DefaultAzureCredential()
    blob_service = BlobServiceClient(account_url=account_url, credential=credential)

    container_client = blob_service.get_container_client(container_name)
    if not container_client.exists():
        raise ValueError(f"Container '{container_name}' does not exist.")

    blob_client = container_client.get_blob_client(file_name)
    if not blob_client.exists():
        raise ValueError(f"Blob '{file_name}' does not exist in container '{container_name}'.")

    blob_bytes = blob_client.download_blob().readall()
    return blob_bytes.decode("utf-8", errors="replace")


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return PlainTextResponse("mcp is working")


if __name__ == "__main__":
    #mcp.run(transport="http", host="127.0.0.1", port=8000)
    port = int(os.getenv("PORT",os.getenv("WEBSITES_PORT","8000")))
    mcp.run(transport="http",host="0.0.0.0",port = port,path="/mcp")
