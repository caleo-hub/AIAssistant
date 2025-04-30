import importlib
import pkgutil
import inspect
import logging
import yaml
from interfaces.tool_base import AssistantToolBase

# Configura o logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Ou DEBUG para mais verbosidade
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_enabled_tools_from_config(path="config.yaml"):
    try:
        with open(path, "r") as file:
            config = yaml.safe_load(file)
        return config.get("tools", {}).get("enabled", [])
    except Exception as e:
        logger.error(f"Erro ao carregar config.yaml: {e}")
        return []


def load_tools_from_package(package):
    tools = []
    allowed_tools = (
        set(get_enabled_tools_from_config())
        if get_enabled_tools_from_config()
        else set()
    )
    successfully_loaded = set()

    if not allowed_tools:
        logger.warning("Nenhuma ferramenta habilitada em config.yaml.")
        return tools

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name not in allowed_tools:
            logger.debug(f"Ignorando módulo não permitido: {module_name}")
            continue

        try:
            module = importlib.import_module(f"{package.__name__}.{module_name}")
        except ImportError as e:
            logger.error(f"Erro ao importar módulo '{module_name}': {e}")
            continue

        found = False
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, AssistantToolBase) and obj is not AssistantToolBase:
                try:
                    tools.append(obj())
                    logger.info(f"Tool carregada: {name}")
                    found = True
                    successfully_loaded.add(module_name)
                except Exception as e:
                    logger.error(f"Erro ao instanciar '{name}' em '{module_name}': {e}")
        if not found:
            logger.warning(
                f"Nenhuma classe válida encontrada no módulo '{module_name}'."
            )

    # Verifica quais não foram carregadas
    failed_tools = allowed_tools - successfully_loaded
    if failed_tools:
        logger.warning(
            f"As seguintes ferramentas não foram carregadas: {', '.join(failed_tools)}"
        )

    return tools
