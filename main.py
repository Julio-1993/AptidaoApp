from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Color, Rectangle
import pymysql
import os

# Carregar o arquivo KV
Builder.load_file(os.path.join(os.path.dirname(__file__), "main.kv"))

class CustomCheckBox(CheckBox):
    def on_kv_post(self, base_widget):
        """Define a cor de fundo da checkbox após ser carregada no KV."""
        with self.canvas.before:
            Color(0.6, 0.6, 0.6, 1)  # Cinza
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, *args):
        """Mantém o fundo cinza ajustado ao tamanho da CheckBox."""
        self.rect.size = self.size
        self.rect.pos = self.pos

class AptidaoApp(BoxLayout):
    def buscar_nome(self, instance, value):
        value = value.upper()  # Garante que o valor seja maiúsculo
        self.ids.ciic_input.text = value
        if value:
            nome = self.consultar_nome_banco(value)
            self.ids.nome_input.text = nome if nome else ""

    def deselecionar_outros(self, instance, value):
        """Permite selecionar apenas uma opção de status de aptidão."""
        if value:
            checkboxes = [
                self.ids.status_apto,
                self.ids.status_inapto,
                self.ids.status_apto_especial,
                self.ids.status_controle
            ]
            for cb in checkboxes:
                if cb != instance:
                    cb.active = False

    def conectar_banco(self):
        """Realiza a conexão com o banco de dados."""
        try:
            return pymysql.connect(
                host="186.202.152.111",
                user="consorciofauna",
                password="cgF@1234",
                database="consorciofauna"
            )
        except pymysql.MySQLError as erro:
            self.mostrar_popup("Erro", f"Erro ao conectar ao banco:\n{erro}")
            return None

    def consultar_nome_banco(self, ciic):
        """Consulta o nome do animal no banco de dados pelo CIIC."""
        conexao = self.conectar_banco()
        if not conexao:
            return None

        cursor = None
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT nome FROM f_animal WHERE ciic = %s", (ciic,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        except pymysql.MySQLError as erro:
            self.mostrar_popup("Erro", f"Erro ao buscar o nome:\n{erro}")
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()
        return None

    def salvar_dados(self, instance):
        """Salva os dados no banco de dados."""
        ciic_animal = self.ids.ciic_input.text
        nome_animal = self.ids.nome_input.text
        taptidao = self.ids.tipo_aptidao.text

        status = None
        if self.ids.status_apto.active:
            status = "Apto"
        elif self.ids.status_inapto.active:
            status = "Inapto"
        elif self.ids.status_apto_especial.active:
            status = "Apto-Especial"
        elif self.ids.status_controle.active:
            status = "Controle de Espécie"

        motivos = self.ids.motivos_input.text
        if not ciic_animal or not nome_animal or not motivos:
            self.mostrar_popup("Atenção", "Todos os campos devem ser preenchidos!")
            return

        conexao = self.conectar_banco()
        if not conexao:
            return

        cursor = None
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
        except pymysql.MySQLError as erro:
            self.mostrar_popup("Erro", f"Erro ao salvar os dados:\n{erro}")
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    def mostrar_popup(self, titulo, mensagem):
        """Exibe um popup na tela com uma mensagem."""
        Clock.schedule_once(lambda dt: self._criar_popup(titulo, mensagem), 0)

    def _criar_popup(self, titulo, mensagem):
        """Função auxiliar para exibir o popup corretamente."""
        popup = Popup(
            title=titulo,
            content=Label(text=mensagem),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()

    def limpar_campos(self):
        """Limpa os campos do formulário."""
        self.ids.ciic_input.text = ""
        self.ids.nome_input.text = ""
        self.ids.tipo_aptidao.text = "Selecione"
        self.ids.status_apto.active = False
        self.ids.status_inapto.active = False
        self.ids.status_apto_especial.active = False
        self.ids.status_controle.active = False
        self.ids.motivos_input.text = ""

class AptidaoAppKivy(App):
    def build(self):
        return AptidaoApp()

if __name__ == "__main__":
    AptidaoAppKivy().run()

