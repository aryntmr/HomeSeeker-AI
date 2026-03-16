import asyncio
import re
import boto3
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.session_store import session_store
from backend.tools.property_search import search_properties

SYSTEM_PROMPT = """You are Alex, a friendly NYC real estate agent helping buyers find homes from a database of 217 NYC listings.
Gather requirements conversationally and call search_properties as soon as you have at least one criterion.

CRITICAL FORMATTING RULES:
- Plain text only. Zero markdown. No asterisks, no bold (**), no bullets, no numbered lists, no headers, no backticks.
- Never list or describe individual properties in your reply text. The UI displays property cards automatically.
- After a search, write ONE short sentence summarizing what you found (e.g. "I found 4 condos in Brooklyn under $600k — take a look!"), then stop.
- Keep every reply under 3 sentences.

Tool: search_properties — searches the property database; all filters are optional, combine any subset.
- min_price (int): minimum listing price in dollars
- max_price (int): maximum listing price in dollars
- min_beds (int): minimum number of bedrooms required
- max_beds (int): maximum number of bedrooms allowed
- min_baths (float): minimum number of bathrooms (e.g. 1.5)
- location (str): matches against city or neighborhood name using partial case-insensitive search
- property_type (str): type of property — common values: "Single Family Residential", "Condo/Co-op", "Townhouse", "Multi-Family (2-4 Unit)"
- min_sqft (int): minimum interior square footage
- max_sqft (int): maximum interior square footage
- min_year_built (int): only return properties built in this year or later
- listing_status (str): current listing status — most listings are "Active"
- max_results (int): number of results to return, default 10

Database schema (properties table):
- id: unique integer primary key for each listing
- property_type: category of the property (e.g. Single Family Residential, Condo/Co-op)
- address: full street address of the property
- city: city the property is located in (e.g. Brooklyn, Bronx, Staten Island)
- state: US state abbreviation (all listings are NY)
- zip_code: 5-digit postal code
- price: listing price in dollars (integer)
- beds: number of bedrooms (integer)
- baths: number of bathrooms (decimal, e.g. 1.5)
- neighborhood: sub-area within the city (e.g. "Park Slope", "Dongan Hills")
- sqft: interior living area in square feet
- lot_size: total lot area in square feet (may be null for condos)
- year_built: year the structure was originally constructed
- days_on_market: number of days the listing has been active
- hoa_month: monthly HOA fee in dollars (null if no HOA)
- listing_status: current status of the listing (typically "Active")
- latitude: GPS latitude coordinate
- longitude: GPS longitude coordinate
- url: direct Redfin listing URL for the property"""

TOOL_SPEC = {
    "name": "search_properties",
    "description": "Search NYC property listings with optional filters. Call this when you have at least one search criterion.",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "min_price": {
                    "type": "integer",
                    "description": "Minimum price in dollars"
                },
                "max_price": {
                    "type": "integer",
                    "description": "Maximum price in dollars"
                },
                "min_beds": {
                    "type": "integer",
                    "description": "Minimum number of bedrooms"
                },
                "max_beds": {
                    "type": "integer",
                    "description": "Maximum number of bedrooms"
                },
                "min_baths": {
                    "type": "number",
                    "description": "Minimum number of bathrooms"
                },
                "location": {
                    "type": "string",
                    "description": "City or neighborhood name (e.g. 'Brooklyn', 'Astoria')"
                },
                "property_type": {
                    "type": "string",
                    "description": "Property type (e.g. 'Single Family Residential', 'Condo/Co-op', 'Townhouse')"
                },
                "min_sqft": {
                    "type": "integer",
                    "description": "Minimum square footage"
                },
                "max_sqft": {
                    "type": "integer",
                    "description": "Maximum square footage"
                },
                "min_year_built": {
                    "type": "integer",
                    "description": "Minimum year the property was built"
                },
                "listing_status": {
                    "type": "string",
                    "description": "Listing status (e.g. 'Active')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 10)"
                }
            },
            "required": []
        }
    }
}

INT_PARAMS = {"min_price", "max_price", "min_beds", "max_beds", "min_sqft", "max_sqft", "min_year_built", "max_results"}
FLOAT_PARAMS = {"min_baths"}


def _strip_thinking(text: str) -> str:
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL)
    text = re.sub(r"</?response>", "", text)
    return text.strip()


def _coerce_tool_input(raw: dict) -> dict:
    coerced = {}
    for k, v in raw.items():
        if k in INT_PARAMS and v is not None:
            coerced[k] = int(v)
        elif k in FLOAT_PARAMS and v is not None:
            coerced[k] = float(v)
        else:
            coerced[k] = v
    return coerced


def _trim_tool_result(result: dict) -> dict:
    """Keep only total_found + top 5 properties to avoid context bloat in history."""
    return {
        "total_found": result["total_found"],
        "search_criteria": result.get("search_criteria", {}),
        "properties": result["properties"][:5],
    }


class ChatAgent:
    def __init__(self):
        self._bedrock = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )

    async def chat(self, session_id: str, user_message: str, db: AsyncSession, verbose: bool = False) -> tuple[str, list]:
        def _log(*args):
            if verbose:
                print(*args)

        session_store.append_message(session_id, "user", [{"text": user_message}])
        history = session_store.get_history(session_id)

        full_properties: list = []
        loop = asyncio.get_event_loop()
        iteration = 0

        while True:
            iteration += 1
            _log(f"\n[agent] loop iteration {iteration} — calling converse() with {len(history)} history turns")

            def _converse():
                return self._bedrock.converse(
                    modelId=settings.nova_lite_model_id,
                    system=[{"text": SYSTEM_PROMPT}],
                    messages=history,
                    toolConfig={"tools": [{"toolSpec": TOOL_SPEC}]},
                )

            response = await loop.run_in_executor(None, _converse)
            stop_reason = response["stopReason"]
            output_message = response["output"]["message"]
            _log(f"[agent] stopReason = {stop_reason}")

            if stop_reason == "end_turn":
                reply_text = ""
                for block in output_message["content"]:
                    if "text" in block:
                        reply_text = _strip_thinking(block["text"])
                        break
                _log(f"[agent] end_turn — returning reply ({len(reply_text)} chars), {len(full_properties)} properties")
                session_store.append_message(session_id, "assistant", output_message["content"])
                return reply_text, full_properties

            if stop_reason == "tool_use":
                session_store.append_message(session_id, "assistant", output_message["content"])

                tool_results = []
                for block in output_message["content"]:
                    if "toolUse" not in block:
                        continue

                    tool_use = block["toolUse"]
                    tool_use_id = tool_use["toolUseId"]
                    tool_input = _coerce_tool_input(tool_use.get("input", {}))

                    _log(f"[tool]  search_properties called")
                    _log(f"[tool]  input  → {tool_input}")

                    search_result = await search_properties(db, **tool_input)
                    trimmed = _trim_tool_result(search_result)
                    full_properties = trimmed["properties"]

                    _log(f"[tool]  result → total_found={search_result['total_found']}, returned={len(full_properties)}")
                    if full_properties:
                        p = full_properties[0]
                        _log(f"[tool]  top result: {p.get('address')}, {p.get('city')} — ${p.get('price'):,}")
                    tool_results.append({
                        "toolUseId": tool_use_id,
                        "content": [{"json": trimmed}],
                    })

                tool_result_content = [{"toolResult": tr} for tr in tool_results]
                session_store.append_message(session_id, "user", tool_result_content)
                _log(f"[agent] toolResult appended — looping back")

            else:
                reply_text = ""
                for block in output_message.get("content", []):
                    if "text" in block:
                        reply_text = _strip_thinking(block["text"])
                        break
                _log(f"[agent] unexpected stopReason={stop_reason} — returning")
                session_store.append_message(session_id, "assistant", output_message.get("content", []))
                return reply_text, full_properties


chat_agent = ChatAgent()
