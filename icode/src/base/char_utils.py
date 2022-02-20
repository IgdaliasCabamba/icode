_UNICODE_ICONS = {
    "custom": {
        "folder_git": "\ue5fb",
        "folder_config": "\ue5fc",
    },
    "dev": {
        "git": "\ue702",
        "git_branch": "\ue725",
        "git_commit": "\ue729",
        "git_compare": "\ue728",
        "git_merge": "\ue727",
        "git_pull_request": "\ue726",
    },
    "fa": {
        "external_link": "\uf08e",
    },
    "fae": {
        "bigger": "\ue285"
    }
}


def get_unicon(main: str, name: str):
    if main in _UNICODE_ICONS.keys():
        if name in _UNICODE_ICONS[main].keys():
            return _UNICODE_ICONS[main][name]

    return "\u25a1"
