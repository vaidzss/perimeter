import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

def generate_openapi():
    # Fetch FastAPI's generated OpenAPI schema
    schema = app.openapi()
    
    # Filter paths down strictly to the documented public API surface
    documented_prefixes = ["/api/v2/auth/login", "/api/v2/auth/me", "/api/v2/accounts/{account_id}/statement", "/api/v2/upi/merchants", "/api/v2/payments/upi-transfer"]
    
    filtered_paths = {}
    for path, path_item in schema.get("paths", {}).items():
        if path in documented_prefixes:
            filtered_paths[path] = path_item
            
    schema["paths"] = filtered_paths
    schema["info"]["title"] = "BharatPay Public Banking API"
    schema["info"]["description"] = "Documented production API surface for BharatPay neobank services."
    schema["info"]["version"] = "2.0.0"

    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../spec/openapi.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"[OpenAPI Export] Successfully wrote curated spec ({len(filtered_paths)} paths) to {output_path}")

if __name__ == "__main__":
    generate_openapi()
