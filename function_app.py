import azure.functions as func
import logging

app = func.FunctionApp()

@app.function_name(name="webhook")
@app.route(route="webhook", methods=["GET"])
def webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    name = req.params.get('name', "World")
    return func.HttpResponse(f"Hello, {name}!")