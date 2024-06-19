#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
import os
import requests
import signal
import time

time.sleep(5)

# Visit http://api.open-notify.org for more info on the API service.
API_URL = 'http://api.open-notify.org/astros.json'

class SpaceIndicator:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "astronaut-toolbar", os.environ["HOME"] + "/git/astronaut_toolbar/icon_planet.svg",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())
        self.update_label()

    def create_menu(self):
        menu = Gtk.Menu()

        # Dynamic menu items for spacecrafts
        self.spacecraft_menu_items = {}
        menu = self.build_spacecraft_menu()

        # Separator
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)

        # Refresh item
        item_refresh = Gtk.MenuItem(label='Refresh')
        item_refresh.connect('activate', self.refresh)
        menu.append(item_refresh)

        # Quit item
        item_quit = Gtk.MenuItem(label='Quit')
        item_quit.connect('activate', Gtk.main_quit)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def build_spacecraft_menu(self):
        menu = Gtk.Menu()
        data = self.fetch_crew_data()
        if data:
            for spacecraft, members in data.items():
                item = Gtk.MenuItem(label=f'{spacecraft} ({len(members)})')
                submenu = Gtk.Menu()
                for member in members:
                    subitem = Gtk.MenuItem(label=member)
                    submenu.append(subitem)
                item.set_submenu(submenu)
                menu.append(item)
        return menu

    def update_label(self):
        number_in_space = self.fetch_number_in_space()
        if number_in_space is not None:
            label = f'{number_in_space}'
        else:
            label = 'Error'
        self.indicator.set_label(label, "SpaceIndicator")

    def fetch_number_in_space(self):
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            return len(data['people'])
        return None

    def fetch_crew_data(self):
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            spacecraft_dict = {}
            for person in data['people']:
                if person['craft'] in spacecraft_dict:
                    spacecraft_dict[person['craft']].append(person['name'])
                else:
                    spacecraft_dict[person['craft']] = [person['name']]
            return spacecraft_dict
        return None

    def refresh(self, widget):
        self.indicator.set_menu(self.create_menu())
        self.update_label()

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow Ctrl-C to close the app
    app = SpaceIndicator()
    Gtk.main()

if __name__ == "__main__":
    main()
