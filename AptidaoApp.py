from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
import mysql.connector

class AptidaoApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.add_widget(Label(text='CIIC do Animal:'))
        self.ciic_input = TextInput(multiline=False)
        self.ciic_input.bind(text=self.buscar_nome)
        self.add_widget(self.ciic_input)

        self.add_widget(Label(text='Nome do Animal:'))
        self.nome_input = TextInput(multiline=False, readonly=True)
        self.add_widget(self.nome_input)

        self.add_widget(Label(text='Tipo de Aptidão:'))
        self.tipo_aptidao = Spinner(text='Selecione', values=('Adoção', 'Reintegração'))
        self.add_widget(self.tipo_aptidao)
        
        self.add_widget(Label(text='Status de Aptidão:'))
        self.status_layout = BoxLayout()

        self.status_apto = CheckBox()
        self.status_apto_label = Label(text='Apto')
        self.status_layout.add_widget(self.status_apto)
        self.status_layout.add_widget(self.status_apto_label)

        self.status_inapto = CheckBox()
        self.status_inapto_label = Label(text='Inapto')
        self.status_layout.add_widget(self.status_inapto)
        self.status_layout.add_widget(self.status_inapto_label)

        self.status_apto_especial = CheckBox()
        self.status_apto_especial_label = Label(text='Apto-Especial')
        self.status_layout.add_widget(self.status_apto_especial)
        self.status_layout.add_widget(self.status_apto_especial_label)

        self.status_controle = CheckBox()
        self.status_controle_label = Label(text='Controle de Espécie')
        self.status_layout.add_widget(self.status_controle)
        self.status_layout.add_widget(self.status_controle_label)

        self.add_widget(self.status_layout)

        self.add_widget(Label(text='Motivos Aptidão:'))
        self.motivos_input = TextInput(size_hint_y=None, height=150, multiline=True)
        scroll = ScrollView(size_hint=(1, None), size=(400, 150))
        scroll.add_widget(self.motivos_input)
        self.add_widget(scroll)

        self.salvar_button = Button(text='Salvar')
        self.salvar_button.bind(on_press=self.salvar_dados)
        self.add_widget(self.salvar_button)

        # Bind the checkboxes to the deselect function
        self.status_apto.bind(active=self.deselecionar_outros)
        self.status_inapto.bind(active=self.deselecionar_outros)
        self.status_apto_especial.bind(active=self.deselecionar_outros)
        self.status_controle.bind(active=self.deselecionar_outros)
    
    def deselecionar_outros(self, instance, value):
        # If the checkbox is checked, uncheck the others
        if value:
            if instance == self.status_apto:
                self.status_inapto.active = False
                self.status_apto_especial.active = False
                self.status_controle.active = False
            elif instance == self.status_inapto:
                self.status_apto.active = False
                self.status_apto_especial.active = False
                self.status_controle.active = False
            elif instance == self.status_apto_especial:
                self.status_apto.active = False
                self.status_inapto.active = False
                self.status_controle.active = False
            elif instance == self.status_controle:
                self.status_apto.active = False
                self.status_inapto.active = False
                self.status_apto_especial.active = False

    def conectar_banco(self):
        try:
            conexao = mysql.connector.connect(
                host="186.202.152.111",
                user="consorciofauna",
                password="cgF@1234",
                database="consorciofauna"
            )
            return conexao
        except mysql.connector.Error as erro:
            self.mostrar_popup("Erro", f"Erro ao conectar ao banco: {erro}")
            return None
    
    def buscar_nome(self, instance, value):
        if value:
            nome = self.consultar_nome_banco(value)
            if nome:
                self.nome_input.text = nome
            else:
                self.nome_input.text = ""
    
    def consultar_nome_banco(self, ciic):
        conexao = self.conectar_banco()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT nome FROM animais WHERE ciic = %s", (ciic,))
                resultado = cursor.fetchone()
                return resultado[0] if resultado else None
            except mysql.connector.Error as erro:
                self.mostrar_popup("Erro", f"Erro ao buscar o nome: {erro}")
            finally:
                cursor.close()
                conexao.close()
        return None

    def salvar_dados(self, instance):
        ciic_animal = self.ciic_input.text
        nome_animal = self.nome_input.text
        taptidao = self.tipo_aptidao.text
        
        status = None
        if self.status_apto.active:
            status = "Apto"
        elif self.status_inapto.active:
            status = "Inapto"
        elif self.status_apto_especial.active:
            status = "Apto-Especial"
        elif self.status_controle.active:
            status = "Controle de Espécie"
        
        motivos = self.motivos_input.text
        if not ciic_animal or not nome_animal or not motivos:
            self.mostrar_popup("Atenção", "Todos os campos devem ser preenchidos!")
            return
        
        conexao = self.conectar_banco()
        if conexao:
            try:
                cursor = conexao.cursor()
                sql = """
                    INSERT INTO aptidao_animais (ciic, nome, tipo_aptidao, status_aptidao, motivos)
                    VALUES (%s, %s, %s, %s, %s)
                """
                valores = (ciic_animal, nome_animal, taptidao, status, motivos)
                cursor.execute(sql, valores)
                conexao.commit()
                self.mostrar_popup("Sucesso", "Dados salvos com sucesso!")
                self.limpar_campos()
            except mysql.connector.Error as erro:
                self.mostrar_popup("Erro", f"Erro ao salvar os dados: {erro}")
            finally:
                cursor.close()
                conexao.close()
    
    def mostrar_popup(self, titulo, mensagem):
        popup = Popup(title=titulo, content=Label(text=mensagem), size_hint=(None, None), size=(400, 200))
        popup.open()
    
    def limpar_campos(self):
        self.ciic_input.text = ""
        self.nome_input.text = ""
        self.tipo_aptidao.text = "Selecione"
        self.status_apto.active = False
        self.status_inapto.active = False
        self.status_apto_especial.active = False
        self.status_controle.active = False
        self.motivos_input.text = ""

class AptidaoAppKivy(App):
    def build(self):
        return AptidaoApp()

if __name__ == "__main__":
    AptidaoAppKivy().run()