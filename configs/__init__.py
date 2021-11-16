from os import path

DB_CONF_PATH = 'configs/db.conf'
JWT_CONF_PATH = 'configs/jwt.conf'

def load_conf(conf_path:str):
    conf = {}
    for line in open(path.join(path.abspath('.'), conf_path)).readlines():
        split_line = line.split('=', 1)
        conf[split_line[0]] = split_line[1].replace('\n', '')
    return conf

DB_CONF = load_conf(DB_CONF_PATH)
JWT_CONF = load_conf(JWT_CONF_PATH)
