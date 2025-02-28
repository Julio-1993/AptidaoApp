from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
import pymysql
import os

# Carregar o arquivo KV
Builder.load_file(os.path.join(os.path.dirname(__file__), "main.kv"))

class AptidaoApp(BoxLayout):
    def buscar_nome(self, instance, value):
        if value:
            nome = self.consultar_nome_banco(value)
            self.ids.nome_input.text = nome if nome else ""

    def deselecionar_outros(self, instance, value):
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
        try:
            return pymysql.connect(
                host="186.202.152.111",
                user="consorciofauna",
                password="cgF@1234",
                database="consorciofauna"
            )
        except pymysql.MySQLError as erro:  # Corrigido para MySQLError
            self.mostrar_popup("Erro", f"Erro ao conectar ao banco:\n{erro}")
            return None

    def consultar_nome_banco(self, ciic):
        conexao = self.conectar_banco()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("SELECT nome FROM f_animal WHERE ciic = %s", (ciic,))
                resultado = cursor.fetchone()
                return resultado[0] if resultado else None
            except pymysql.MySQLError as erro:
                self.mostrar_popup("Erro", f"Erro ao buscar o nome:\n{erro}")
            finally:
                cursor.close()
                conexao.close()
        return None

    def salvar_dados(self):
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
            except pymysql.MySQLError as erro:
                self.mostrar_popup("Erro", f"Erro ao salvar os dados:\n{erro}")
            finally:
                cursor.close()
                conexao.close()

    def mostrar_popup(self, titulo, mensagem):
        """Exibe um popup na tela com uma mensagem."""
        popup = Popup(
            title=titulo,
            content=Label(text=mensagem),
            size_hint=(None, None),
            size=(400, 200)
        )
        popup.open()

    def limpar_campos(self):
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

