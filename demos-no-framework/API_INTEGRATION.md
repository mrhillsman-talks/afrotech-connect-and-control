# RandomUser.me API Integration

## Overview

The MCP server now integrates with the free **randomuser.me API** to generate realistic fake user data. This replaces the previous LLM sampling approach with a faster, more reliable external API.

## What Changed

### Before (LLM Sampling)
- Used `server.request_context.session.create_message()` to ask the LLM to generate fake data
- Required complex prompt engineering
- Parsing issues with JSON formatting
- Slower and dependent on LLM availability
- Required sampling callback in client

### After (API Integration)
- Direct HTTP request to `https://randomuser.me/api/`
- Consistent, well-formatted JSON responses
- Faster and more reliable
- No LLM dependency for random user generation
- Returns real-looking international user data

## Implementation Details

### New Function: `fetch_random_user()`

```python
async def fetch_random_user() -> dict:
    """Fetch random user data from randomuser.me API"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://randomuser.me/api/")
        response.raise_for_status()
        data = response.json()

        # Extract user data from API response
        user_data = data["results"][0]

        # Map API data to our schema
        name = f"{user_data['name']['first']} {user_data['name']['last']}"
        email = user_data["email"]

        # Format address as a single string
        location = user_data["location"]
        address = f"{location['street']['number']} {location['street']['name']}, {location['city']}, {location['state']}, {location['country']} {location['postcode']}"

        phone = user_data["phone"]

        return {
            "name": name,
            "email": email,
            "address": address,
            "phone": phone
        }
```

### Updated Tool: `create-random-user`

The tool now:
1. Calls `fetch_random_user()` to get data from the API
2. Creates a user with the returned data
3. Returns a success message with user details

## API Response Mapping

| RandomUser.me API Field | Our Schema Field | Transformation |
|------------------------|------------------|----------------|
| `name.first` + `name.last` | `name` | Concatenated with space |
| `email` | `email` | Direct mapping |
| `location.*` | `address` | Formatted as full address string |
| `phone` | `phone` | Direct mapping |

## Example API Response

```json
{
  "results": [{
    "name": {
      "first": "Hervé",
      "last": "Menard"
    },
    "email": "herve.menard@example.com",
    "location": {
      "street": {
        "number": 8258,
        "name": "Place de L'Abbé-Georges-Hénocque"
      },
      "city": "La Baroche",
      "state": "Genève",
      "country": "Switzerland",
      "postcode": 8585
    },
    "phone": "078 977 74 40"
  }]
}
```

## Benefits

1. **Reliability**: Consistent data format, no parsing errors
2. **Performance**: Faster than LLM generation
3. **Diversity**: International names, addresses, and phone formats
4. **Simplicity**: No complex prompt engineering needed
5. **Cost**: Free API with no LLM costs for this operation

## Usage

### Via Tools Menu
```
? What would you like to do? Tools
? Select a tool: create-random-user
✓ User 3 created successfully: Hervé Menard (herve.menard@example.com)
```

### Via Query
```
? What would you like to do? Query
? Enter your query: Create a random user
✓ User 6 created successfully: Craig Terry (craig.terry@example.com)
💬 OK. I have created a random user...
```

### Programmatically
```python
result = await session.call_tool("create-random-user", {})
```

## Dependencies

- **httpx**: Already included as a dependency of the `mcp` package
- No additional installations required

## Error Handling

The implementation handles:
- HTTP errors (network issues, API downtime)
- JSON parsing errors
- Missing fields in API response
- Database write errors

## API Rate Limits

RandomUser.me has generous rate limits for free usage:
- No API key required
- Suitable for development and testing
- For production use, consider their [paid plans](https://randomuser.me/documentation#premium)

## Future Enhancements

Possible improvements:
- Add parameters to specify nationality, gender, etc.
- Cache API responses for offline testing
- Add bulk user creation endpoint
- Support multiple random users in one call
