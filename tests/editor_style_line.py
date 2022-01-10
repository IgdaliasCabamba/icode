# Styling Scintilla Line

import random 

x = random.randint(40,254)
print(x)

self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, x, QColor("purple"))
self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, x, QColor("yellow"))
line, col = self.getCursorPosition()
end_pos = self.SendScintilla(QsciScintilla.SCI_GETLINEENDPOSITION, line)
start_pos= self.SendScintilla(QsciScintilla.SCI_POSITIONFROMLINE, line)
len = end_pos-start_pos

self.SendScintilla(QsciScintilla.SCI_STARTSTYLING, start_pos, x)
self.SendScintilla(QsciScintilla.SCI_SETSTYLING, len, x)