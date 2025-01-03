# Azure Function Hello World

A simple HTTP-triggered Azure Function that responds with "Hello, {name}!".

## Local Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the function locally:
```bash
func start
```

4. Test the function:
```bash
curl "http://localhost:7071/api/webhook?name=YourName"
```

## Deployment

The function is automatically deployed to Azure using GitHub Actions when changes are pushed to the main branch.

## API Reference

### GET /api/webhook

Returns a greeting message.

Query Parameters:
- `name` (optional): The name to greet. Defaults to "World".
