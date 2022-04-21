WINDOW_STYLESHEET = """
#window-frame {
  background-color: palette(Window);
}

#lbl-title{
  margin: 0px 4px 4px 4px;
}

#btn-close, #btn-restore, #btn-maximize, #btn-minimize {
  min-width: 14px;
  min-height: 14px;
  max-width: 14px;
  max-height: 14px;
  border-radius: 7px;
  margin: 0px 4px 4px 4px;
}

#btn-restore, #btn-maximize {
  background-color: hsv(123, 204, 198);
}

#btn-restore::hover, #btn-maximize::hover {
  background-color: hsv(123, 204, 148);
}

#btn-restore::pressed, #btn-maximize::pressed {
  background-color: hsv(123, 204, 98);
}

#btn-minimize {
  background-color: hsv(38, 218, 253);
}

#btn-minimize::hover {
  background-color: hsv(38, 218, 203);
}

#btn-minimize::pressed {
  background-color: hsv(38, 218, 153);
}

#btn-close {
  background-color: hsv(0, 182, 252);
}

#btn-close::hover {
  background-color: hsv(0, 182, 202);
}

#btn-close::pressed {
  background-color: hsv(0, 182, 152);
}

#btn-close::disabled, #btn-restore::disabled, #btn-maximize::disabled, #btn-minimize::disabled {
  background-color: palette(midlight);
}

#btn-menu{
  margin: 4px 4px 4px 4px;
}
#btn-menu::menu-indicator
{
    image:none;
} 
"""
