from langgraph_sdk import Auth

auth = Auth()

@auth.authenticate
async def authenticate(headers: dict) -> dict:
    user_info = json.loads(hearders.get("X-User-Info", "{}"))
    if not user_info.get("id"):
        raise Exception("Authentication required")

    return {
        "identity": user_info["id"],
        "display_name": user_info.get("name", ""),
        "is_authenticated": True
    }