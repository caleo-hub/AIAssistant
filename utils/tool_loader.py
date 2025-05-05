import importlib
import inspect
import logging
import yaml
from interfaces.tool_base import AssistantToolBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(handler)


def get_enabled_tools_from_config(path="config.yaml"):
    try:
        with open(path, "r") as file:
            config = yaml.safe_load(file)
        return config.get("tools", {}).get("enabled", []) or []
    except Exception as e:
        logger.error(f"Erro ao carregar config.yaml: {e}")
        return []


def load_tools_from_package(package):
    tools = []
    enabled_tools = get_enabled_tools_from_config()
    if not enabled_tools:
        logger.warning("Nenhuma ferramenta habilitada em config.yaml.")
        return tools

    successfully_loaded = set()

    # Itera na ordem exata em que aparecem no config
    for module_name in enabled_tools:
        try:
            module = importlib.import_module(f"{package.__name__}.{module_name}")
        except ImportError as e:
            logger.error(f"Erro ao importar módulo '{module_name}': {e}")
            continue  # NÃO interrompe o loop
        found = False
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, AssistantToolBase) and cls is not AssistantToolBase:
                try:
                    tools.append(cls())
                    logger.info(f"Tool carregada: {cls.__name__}")
                    successfully_loaded.add(module_name)
                    found = True
                except Exception as inst_e:
                    logger.error(f"Erro ao instanciar '{cls.__name__}': {inst_e}")
        if not found:
            logger.warning(f"Nenhuma classe válida encontrada em '{module_name}'.")

    # Reporta os que configurou mas não conseguiu carregar
    missing = set(enabled_tools) - successfully_loaded
    if missing:
        logger.warning(f"As seguintes ferramentas não foram carregadas: {', '.join(missing)}")

    return tools
