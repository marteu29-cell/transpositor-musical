from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
import os
import re

NOTAS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTAS_PT = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
ENHARMONICOS = {'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B'}

def nota_para_index(nota):
    nota = ENHARMONICOS.get(nota, nota)
    if nota in NOTAS:
        return NOTAS.index(nota)
    return -1

def transpor_nota(nota, semitons):
    idx = nota_para_index(nota)
    if idx == -1:
        return nota
    novo_idx = (idx + semitons) % 12
    return NOTAS[novo_idx]

def transpor_texto(texto, semitons):
    padrao = r'\b([A-G][b#]?)(m|maj|min|aug|dim|sus|add|M)?\d*\b'
    def substituir(match):
        nota = match.group(1)
        resto = match.group(2) or ''
        nova_nota = transpor_nota(nota, semitons)
        return nova_nota + resto + match.string[match.start(2)+len(resto):match.end()] if False else nova_nota + match.group(0)[len(nota):]
    return re.sub(padrao, lambda m: transpor_nota(m.group(1), semitons) + m.group(0)[len(m.group(1)):], texto)

class TranspositorApp(App):
    def build(self):
        self.title = 'Transpositor Musical'
        self.arquivo_atual = None
        
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))
        
        # Barra de título
        titulo = Label(
            text='🎵 Transpositor Musical',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20),
            bold=True,
            color=(0.2, 0.6, 1, 1)
        )
        root.add_widget(titulo)
        
        # Barra de ferramentas - arquivos
        toolbar = GridLayout(cols=3, size_hint_y=None, height=dp(45), spacing=dp(4))
        
        btn_novo = Button(text='Novo', font_size=dp(14), background_color=(0.3, 0.7, 0.3, 1))
        btn_novo.bind(on_press=self.novo_arquivo)
        
        btn_abrir = Button(text='Abrir', font_size=dp(14), background_color=(0.3, 0.5, 0.9, 1))
        btn_abrir.bind(on_press=self.abrir_arquivo)
        
        btn_salvar = Button(text='Salvar', font_size=dp(14), background_color=(0.9, 0.6, 0.1, 1))
        btn_salvar.bind(on_press=self.salvar_arquivo)
        
        toolbar.add_widget(btn_novo)
        toolbar.add_widget(btn_abrir)
        toolbar.add_widget(btn_salvar)
        root.add_widget(toolbar)
        
        # Label do arquivo
        self.label_arquivo = Label(
            text='Novo documento',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            color=(0.7, 0.7, 0.7, 1)
        )
        root.add_widget(self.label_arquivo)
        
        # Editor de texto
        self.editor = TextInput(
            hint_text='Cole aqui a cifra ou letra com acordes...\nExemplo:\nAm  G  F  E\nVerse: Am G F E',
            font_size=dp(16),
            multiline=True,
            background_color=(0.1, 0.1, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.3, 0.7, 1, 1),
        )
        root.add_widget(self.editor)
        
        # Seção de transposição
        trans_label = Label(
            text='— Transpor Tons —',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            color=(0.8, 0.8, 0.2, 1)
        )
        root.add_widget(trans_label)
        
        # Botões de transposição
        trans_grid = GridLayout(cols=4, size_hint_y=None, height=dp(50), spacing=dp(4))
        
        btn_m2 = Button(text='-2', font_size=dp(16), background_color=(0.8, 0.2, 0.2, 1))
        btn_m2.bind(on_press=lambda x: self.transpor(-2))
        
        btn_m1 = Button(text='-1', font_size=dp(16), background_color=(0.9, 0.4, 0.1, 1))
        btn_m1.bind(on_press=lambda x: self.transpor(-1))
        
        btn_p1 = Button(text='+1', font_size=dp(16), background_color=(0.1, 0.6, 0.3, 1))
        btn_p1.bind(on_press=lambda x: self.transpor(1))
        
        btn_p2 = Button(text='+2', font_size=dp(16), background_color=(0.1, 0.4, 0.8, 1))
        btn_p2.bind(on_press=lambda x: self.transpor(2))
        
        trans_grid.add_widget(btn_m2)
        trans_grid.add_widget(btn_m1)
        trans_grid.add_widget(btn_p1)
        trans_grid.add_widget(btn_p2)
        root.add_widget(trans_grid)
        
        # Tom atual
        self.label_tom = Label(
            text='Tom original',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(13),
            color=(0.5, 0.9, 0.5, 1)
        )
        root.add_widget(self.label_tom)
        self.semitons_total = 0
        
        return root

    def transpor(self, semitons):
        texto = self.editor.text
        if not texto.strip():
            self.mostrar_msg('Atenção', 'Escreva ou cole uma cifra primeiro!')
            return
        novo_texto = transpor_texto(texto, semitons)
        self.editor.text = novo_texto
        self.semitons_total += semitons
        tons = self.semitons_total % 12
        self.label_tom.text = f'Deslocamento: {self.semitons_total:+d} semitons'

    def novo_arquivo(self, *args):
        self.editor.text = ''
        self.arquivo_atual = None
        self.label_arquivo.text = 'Novo documento'
        self.semitons_total = 0
        self.label_tom.text = 'Tom original'

    def salvar_arquivo(self, *args):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        
        content.add_widget(Label(text='Nome do arquivo:', size_hint_y=None, height=dp(30)))
        
        nome_input = TextInput(
            text=self.arquivo_atual or 'cifra.txt',
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16)
        )
        content.add_widget(nome_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        
        popup = Popup(title='Salvar arquivo', content=content, size_hint=(0.85, 0.4))
        
        def salvar_confirm(*args):
            nome = nome_input.text.strip()
            if not nome:
                return
            if not nome.endswith('.txt'):
                nome += '.txt'
            caminho = os.path.join(os.path.expanduser('~'), 'Documents', nome)
            try:
                os.makedirs(os.path.dirname(caminho), exist_ok=True)
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(self.editor.text)
                self.arquivo_atual = nome
                self.label_arquivo.text = f'📄 {nome}'
                popup.dismiss()
                self.mostrar_msg('Salvo!', f'Arquivo salvo em:\n{caminho}')
            except Exception as e:
                self.mostrar_msg('Erro', f'Não foi possível salvar:\n{str(e)}')
        
        btn_salvar = Button(text='Salvar', background_color=(0.2, 0.7, 0.2, 1))
        btn_salvar.bind(on_press=salvar_confirm)
        btn_cancelar = Button(text='Cancelar', background_color=(0.7, 0.2, 0.2, 1))
        btn_cancelar.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(btn_salvar)
        btn_layout.add_widget(btn_cancelar)
        content.add_widget(btn_layout)
        
        popup.open()

    def abrir_arquivo(self, *args):
        docs = os.path.expanduser('~/Documents')
        try:
            arquivos = [f for f in os.listdir(docs) if f.endswith('.txt')]
        except:
            arquivos = []
        
        if not arquivos:
            self.mostrar_msg('Info', 'Nenhum arquivo .txt encontrado em Documents.')
            return
        
        content = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))
        content.add_widget(Label(text='Selecione um arquivo:', size_hint_y=None, height=dp(30)))
        
        popup = Popup(title='Abrir arquivo', content=content, size_hint=(0.85, 0.7))
        
        scroll = ScrollView()
        lista = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        lista.bind(minimum_height=lista.setter('height'))
        
        for arq in arquivos:
            btn = Button(text=arq, size_hint_y=None, height=dp(44), font_size=dp(14))
            def abrir_este(instance, nome=arq):
                caminho = os.path.join(docs, nome)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        self.editor.text = f.read()
                    self.arquivo_atual = nome
                    self.label_arquivo.text = f'📄 {nome}'
                    self.semitons_total = 0
                    self.label_tom.text = 'Tom original'
                    popup.dismiss()
                except Exception as e:
                    self.mostrar_msg('Erro', str(e))
            btn.bind(on_press=abrir_este)
            lista.add_widget(btn)
        
        scroll.add_widget(lista)
        content.add_widget(scroll)
        
        btn_fechar = Button(text='Cancelar', size_hint_y=None, height=dp(40), background_color=(0.7, 0.2, 0.2, 1))
        btn_fechar.bind(on_press=popup.dismiss)
        content.add_widget(btn_fechar)
        
        popup.open()

    def mostrar_msg(self, titulo, msg):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        content.add_widget(Label(text=msg, text_size=(dp(260), None), halign='center'))
        btn = Button(text='OK', size_hint_y=None, height=dp(40))
        popup = Popup(title=titulo, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()

if __name__ == '__main__':
    TranspositorApp().run()
