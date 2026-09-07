from a2ui.schema.manager import A2uiSchemaManager
from a2ui.schema.catalog import CatalogConfig
from a2ui.schema.catalog_provider import FileSystemCatalogProvider
from a2ui.schema.common_modifiers import remove_strict_validation
from a2ui.basic_catalog.provider import BasicCatalog

from a2ui.adk.send_a2ui_to_client_toolset import SendA2uiToClientToolset

A2UI_VERSION="0.8"


import os
import tempfile
from google.cloud import storage

def download_a2ui_assets_from_gcs(bucket_name: str, gcs_prefix: str, local_dest_dir: str):
    """
    Descarga el catálogo y los ejemplos de GCS a un directorio local temporal.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=gcs_prefix)
    
    for blob in blobs:
        # Extraer la ruta relativa quitando el prefijo de GCS
        relative_path = os.path.relpath(blob.name, gcs_prefix)
        local_path = os.path.join(local_dest_dir, relative_path)
        
        # Ignorar marcadores de carpeta
        if blob.name.endswith('/'):
            continue
            
        # Crear subdirectorios locales necesarios
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Descargar el archivo
        blob.download_to_filename(local_path)


# 1. Definir directorio temporal
TEMP_ROOT = tempfile.gettempdir()
LOCAL_A2UI_DIR = os.path.join(TEMP_ROOT, "mi_catalogo_a2ui")

download_a2ui_assets_from_gcs(
    bucket_name="agentes_224237244779", 
    gcs_prefix="a2ui/catalogos/", 
    local_dest_dir=LOCAL_A2UI_DIR
)

# 3. Construir las rutas temporales para A2UI
temp_catalog_path = os.path.join(LOCAL_A2UI_DIR, "catalog.json")
temp_examples_path = os.path.join(LOCAL_A2UI_DIR, "ejemplos")

schema_manager = A2uiSchemaManager(
    version=A2UI_VERSION,
    catalogs=[
        CatalogConfig(
            name="my_catalog",
            provider=FileSystemCatalogProvider(temp_catalog_path),
            examples_path=temp_examples_path,
        ),
        BasicCatalog.get_config(version=A2UI_VERSION),
    ],
    accepts_inline_catalogs=True,
    schema_modifiers=[remove_strict_validation],
)
instruction = schema_manager.generate_system_prompt(
    role_description="You are a helpful assistant that presents information with rich UI.",
    workflow_description="Analyze the user's request and return structured UI when appropriate.",
    ui_description="Use cards for summaries, tables for comparisons, and forms for user input.",
    include_schema=False,
    include_examples=False,
    validate_examples=False,
)

from google.adk.agents.llm_agent import LlmAgent

root_agent = LlmAgent(
    model="gemini-flash-latest",
    name="ui_agent",
    description="An agent that generates rich UI responses.",
    instruction=instruction,
    tools=[
        SendA2uiToClientToolset(
            a2ui_enabled=lambda ctx: ctx.state.get("system:a2ui_enabled", False),
            a2ui_catalog=lambda ctx: ctx.state.get("system:a2ui_catalog"),
            a2ui_examples=lambda ctx: ctx.state.get("system:a2ui_examples"),
        ),
    ]
)