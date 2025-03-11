from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Configuraciu00f3n de la aplicaciu00f3n basada en variables de entorno"""
    
    # Configuraciu00f3n general
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # WhatsApp API
    WHATSAPP_TOKEN: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_VERIFY_TOKEN_WEBHOOK: str
    
    # OpenAI API
    OPENAI_API_KEY: str
    
    # Base de datos
    COSMOSDB_CONNECTION_STRING: Optional[str] = None
    MONGO_CONNECTION_STRING: Optional[str] = None
    
    @field_validator('COSMOSDB_CONNECTION_STRING', 'MONGO_CONNECTION_STRING', mode='before')
    def check_db_connection(cls, v, info):
        # Validar que al menos una conexión esté definida
        field_name = info.field_name
        if field_name == 'COSMOSDB_CONNECTION_STRING' and not v:
            # Si COSMOSDB no está definido, no es error - verificaremos MONGO después
            return None
        if field_name == 'MONGO_CONNECTION_STRING' and not v:
            # Si MONGO no está definido, no es error - ya deberíamos tener COSMOSDB
            return None
        return v
    
    @computed_field
    @property
    def database_connection_string(self) -> str:
        """Obtiene la cadena de conexión a la base de datos disponible"""
        if self.MONGO_CONNECTION_STRING:
            return self.MONGO_CONNECTION_STRING
        if self.COSMOSDB_CONNECTION_STRING:
            return self.COSMOSDB_CONNECTION_STRING
        raise ValueError("No se ha configurado ninguna conexión a base de datos")
    
    # Modelos AI
    VISION_MODEL: str = "gpt-4-vision-preview"
    EXTRACTION_MODEL: str = "gpt-4"
    
    @computed_field
    @property
    def is_development(self) -> bool:
        """Indica si estamos en entorno de desarrollo"""
        return self.ENVIRONMENT.lower() == "development"
    
    @computed_field
    @property
    def is_production(self) -> bool:
        """Indica si estamos en entorno de producciu00f3n"""
        return self.ENVIRONMENT.lower() == "production"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instancia de configuraciu00f3n a nivel aplicaciu00f3n
settings = Settings()
