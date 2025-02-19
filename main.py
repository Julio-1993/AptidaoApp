from kivy.config import Config
from kivymd.app import MDApp

Config.set('graphics', 'width', '375')
Config.set('graphics', 'width', '665')

class MainApp(MDApp):
    def build(self):
        self.title = "AptidaoApp"
        
    def on_start(self):
        self.root.current = 'menu_screen'
        
if __name__ == "__main__":
    MainApp().run()
