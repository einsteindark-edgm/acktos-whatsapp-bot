# Este archivo proporciona una implementaciu00f3n falsa de la app para pruebas
# Ya no usamos Azure Functions
from blueprint import bp

class MockFunctionApp:
    def __init__(self):
        self.functions = []
    
    def register_functions(self, blueprint):
        self.functions.extend(getattr(blueprint, 'functions', []))

app = MockFunctionApp()
app.register_functions(bp)
