import yaml
import re
import os

if os.path.isfile(".env"):
    from dotenv import load_dotenv
    load_dotenv()

path_matcher = re.compile(r'\$\{([^}^{]+)\}')
def path_constructor(loader, node):
  ''' Extract the matched value, expand env variable, and replace the match '''
  value = node.value
  match = path_matcher.match(value)
  env_var = match.group()[2:-1]
  return os.environ.get(env_var) + value[match.end():]

yaml.add_implicit_resolver('!path', path_matcher)
yaml.add_constructor('!path', path_constructor)

with open("config.yml", "r", encoding='utf-8') as f:
    __config__ = yaml.load(f, Loader=yaml.FullLoader)

class DataHandler():
    config: dict = __config__
    database = config.get("database", {})
    mail = config.get("mail", {})
    register = config.get("register", {})
    server = config.get("server", {})

    def getenv(name: str):
        return os.getenv(name)