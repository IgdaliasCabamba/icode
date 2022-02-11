import gettext

# Set the local directory
localedir = './locale'

# Set up your magic function
translate = gettext.translation('appname', localedir, fallback=True)
_ = translate.gettext

# Translate message
print(_("Olá Mundo"))