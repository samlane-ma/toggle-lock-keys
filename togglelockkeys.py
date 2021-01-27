import gi.repository
gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, Gtk, Gio, Gdk
import subprocess

"""
Toggle Lock Keys provides an indicator for the Caps Lock / Num Lock keys, with
a popover menu to allow manual toggling of Caps / Num lock using xdotool

This applet is based heavily on the Budgie Lock Keys Applet 
Copyright © 2015-2020 Budgie Desktop Developers

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version. This
program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details. You
should have received a copy of the GNU General Public License along with this
program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Text for buttons in the popover
CAPS = "Verr Maj  "
NUM  = "Verr Num"

# Tooltip text
CAPS_ON  = "Verr maj marche"
CAPS_OFF = "Verr maj arrêt"
NUM_ON   = "Verr num marche"
NUM_OFF  = "Verr num arrêt"

class ToggleLockKeys(GObject.GObject, Budgie.Plugin):

    __gtype_name__ = "ToggleLockKeys"

    def __init__(self):
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):
        return ToggleLockKeysApplet(uuid)


class ToggleLockKeysApplet(Budgie.Applet):

    def __init__(self, uuid):

        Budgie.Applet.__init__(self)
        self.uuid = uuid

        self.key_map = Gdk.Keymap.get_default()
        self.key_map.connect('state-changed', self.on_state_changed)

        # the panel icons
        self.caps = Gtk.Image()
        self.caps.set_from_icon_name(
            "caps-lock-symbolic", Gtk.IconSize.MENU)
        self.num = Gtk.Image()    
        self.num.set_from_icon_name(
            "num-lock-symbolic", Gtk.IconSize.MENU)

        # the buttons in the popover
        self.caps_button = Gtk.ModelButton()
        self.caps_button.connect('clicked',self.change_caps)
        self.num_button = Gtk.ModelButton()
        self.num_button.connect('clicked',self.change_num)

        self.panel_box = Gtk.EventBox()
        self.icon_box = Gtk.Box()
        self.icon_box.pack_start(self.caps,True,True,0)
        self.icon_box.pack_end(self.num,True,True,0)
        self.panel_box.add(self.icon_box)
        self.add(self.panel_box)

        self.popover = Budgie.Popover.new(self.panel_box)

        # check for xdotool
        xdotool = True
        try:
            subprocess.run(['xdotool','--version'])
        except:
            xdotool = False

        # don't connect the popup menu if xdotool is not installed
        if xdotool:
            self.panel_box.connect("button-press-event", self.on_press)

        self.toggle_num()
        self.toggle_caps()

        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.caps_button, True, True, 0)
        self.vbox.pack_end(self.num_button, True, True, 0)

        self.popover.add(self.vbox)

        self.vbox.show_all()
        self.panel_box.show_all()
        self.show_all()


    def change_caps(self, b):
        try:
            subprocess.run(['xdotool','key', 'Caps_Lock'])
        except:
            print (_("Could not run xdotool"))
        
    def change_num(self, b):
        try:
            subprocess.run(['xdotool','key', 'Num_Lock'])
        except:
            print (_("Could not run xdotool"))


    def on_state_changed (self,changed):
        self.toggle_caps()     
        self.toggle_num()

    def toggle_num (self) :
        if self.key_map.get_num_lock_state():
            self.num.set_tooltip_text(_(NUM_ON))
            self.num.get_style_context().remove_class("dim-label")
            self.num_button.set_label(_("☑    {}  ").format(NUM))
        else:
            self.num.set_tooltip_text(_(NUM_OFF))
            self.num.get_style_context().add_class("dim-label")
            self.num_button.set_label(_("☐    {}  ").format(NUM))

    def toggle_caps (self) :
        if self.key_map.get_caps_lock_state():
            self.caps.set_tooltip_text(_(CAPS_ON))
            self.caps.get_style_context().remove_class("dim-label")
            self.caps_button.set_label(_("☑    {}  ").format(CAPS))
        else:
            self.caps.set_tooltip_text(_(CAPS_OFF))
            self.caps.get_style_context().add_class("dim-label")
            self.caps_button.set_label(_("☐    {}  ").format(CAPS))

    def on_press(self, panel_box, event):
        if event.button == 1:
            self.manager.show_popover(self.panel_box)

    def do_panel_position_changed(self, position):
        if (position == Budgie.PanelPosition.TOP or
                position == Budgie.PanelPosition.BOTTOM):
            self.icon_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        else:
            self.icon_box.set_orientation(Gtk.Orientation.VERTICAL)

    def do_update_popovers(self, manager):
        self.manager = manager
        self.manager.register_popover(self.panel_box, self.popover)

    def do_supports_settings(self):
        return False
