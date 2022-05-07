import os
from core.storer import CacheManager

def init():
    require_dirs = [
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "user"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "labs"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "april"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "editors"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "extensions"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "code"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "data"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "extensions"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "data", "user"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "data", "memory"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "data", "extensions"),
    ]
    require_files = [
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "labs", "notes.txt"),
        os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "data", "extensions", "ext.db")
    ]

    for require_dir in require_dirs:
        if not os.path.exists(require_dir):
            os.makedirs(require_dir)

    for require_file in require_files:
        with open(require_file, 'a'):
            pass
init()

CACHE_ROUTES = {
    "user_cache":CacheManager(os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "user", "user.idt")),
    "editor_cache":CacheManager(os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "editors", "cache.idt")),
    "april_cache":CacheManager(os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache","april", "cache.idt")),
    "assistant_cache":CacheManager(os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "april", "bot.idt")),
    "qt_cache":CacheManager(os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "user", "cache.idt")),
    "labels_cache":CacheManager(os.path.join(os.environ["SMARTCODE_SRC_PATH"], ".cache", "labs", "labels.idt"))
}
DATA_ROUTES ={
    "extensions_db":os.path.join(os.environ["SMARTCODE_SRC_PATH"], "smartcode", "data", "extensions", "ext.db")
}