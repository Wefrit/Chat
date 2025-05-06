from email.message import Message
from flet.core.types import WEB_BROWSER
import flet as ft

# Classe que define a estrutura de uma mensagem
class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        # Atributos da mensagem: nome do usuário, conteúdo da mensagem, tipo de mensagem (chat ou login)
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

# Classe para gerar o componente visual da mensagem no chat
class ChatMessage(ft.Container):
    def __init__(self, message: Message, is_own: bool):
        super().__init__()

        # Alinha a mensagem à esquerda para o próprio usuário, ou à direita para outros usuários
        self.alignment = ft.alignment.center_left if is_own else ft.alignment.center_right

        # Cria o avatar com as iniciais do usuário e uma cor baseada no nome
        avatar = ft.CircleAvatar(
            content=ft.Text(self.get_initials(message.user_name)), # Iniciais do usuário
            color=ft.Colors.WHITE, # Cor do texto
            bgcolor=self.get_avatar_color(message.user_name), # Cor de fundo baseada no nome
        )

        # Cria o conteúdo da mensagem (nome do usuário e o texto da mensagem)
        user_info = ft.Column(
            [
                ft.Text(message.user_name, weight="bold"), # Nome do usuário em negrito
                ft.Container(
                    content=ft.Text(
                        message.text, # Texto da mensagem
                        selectable=True,
                        size=14,
                        no_wrap=False, #Quebra de linha da mensagem
                    ),
                    expand=False,
                    width=500 # Largura máxima do texto
                ),
            ],
            tight=True,
            spacing=5,
            expand=True,
        )

        # Alinha avatar e mensagem na horizontal
        content_row = ft.Row(
            controls=[avatar, user_info] if is_own else [user_info, avatar],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=10,
            tight=True
        )

        # Conteúdo do container da mensagem
        self.content = ft.Row(
            controls=[
                ft.Container(
                    content=content_row,
                    alignment=ft.alignment.center_left if is_own else ft.alignment.center_right,
                    bgcolor=ft.Colors.BLUE_100 if is_own else ft.Colors.GREEN_100,
                    padding=10,
                    border_radius=10,
                    expand=False,
                )
            ],
            alignment=ft.MainAxisAlignment.START if is_own else ft.MainAxisAlignment.END,
            expand=True,
        )

    # Função que pega a inicial do nome do usuário
    def get_initials(self, user_name: str):
        return user_name[:1].capitalize()

    # Função que gera a cor do avatar baseado no nome do usuário
    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        # Gera a cor a partir do hash do nome do usuário
        return colors_lookup[hash(user_name) % len(colors_lookup)]

# Função principal que controla a lógica da aplicação
def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH # Alinha os elementos na horizontal
    page.title = "Chat" # Título da página

    # Função chamada quando o usuário clica no botão "Entrar no chat"
    def join_chat_click(e):
        if not join_user_name.value.strip() or join_user_name.value.strip() == "":
            join_user_name.error_text = "O nome não pode estar vazio!"
            join_user_name.update()
        else:
            # Salva o nome do usuário na sessão
            page.session.set("user_name", join_user_name.value.strip())
            welcome_dlg.open = False

            # Mensagem do usuário entrou no chat
            page.pubsub.send_all(
                Message(
                    user_name=join_user_name.value,
                    text=f"{join_user_name.value} entrou no chat.",
                    message_type="login_message",
                )
            )
            page.update()

    # Função chamada quando o usuário envia uma mensagem
    def send_message_click(e):
        if new_message.value != "":

            # Envia a mensagem para chat
            page.pubsub.send_all(
                Message(
                    page.session.get("user_name"),
                    new_message.value,
                    message_type="chat_message",
                )
            )
            new_message.value = "" # Limpa a caixa de mensagem
            new_message.focus() # Foca na caixa de mensagem
            page.update()

    # Função chamada quando uma nova mensagem é recebida
    def on_message(message: Message):
        user_name = page.session.get("user_name")

        # Se for uma mensagem de chat
        if message.message_type == "chat_message":
            m = ChatMessage(message, is_own=(message.user_name == user_name))

            #Alinhamento a esquerda, se for de quem mandou e a direita se for de quem recebeu
            alignment = ft.MainAxisAlignment.START if message.user_name == user_name else ft.MainAxisAlignment.END

        # Se for uma mensagem de entrada (login)
        elif message.message_type == "login_message":
            m = ft.Container(
                content=ft.Text(
                    message.text, # Exibe o texto da mensagem de entrada
                    color=ft.Colors.BLACK,
                    size=14,
                    weight="bold",
                    text_align=ft.TextAlign.CENTER, # Centraliza o texto
                    no_wrap=False, # Quebra de linha
                ),
                alignment=ft.alignment.center,# Centraliza o container
                bgcolor=ft.colors.BLUE_GREY_100,
                padding=15,
                border_radius=20,
                margin=10,
            )
            alignment = ft.MainAxisAlignment.CENTER # Alinha a mensagem ao centro

        # Adiciona a mensagem ao chat com o alinhamento correto
        chat.controls.append(ft.Row([m], alignment=alignment))
        page.update()

    page.pubsub.subscribe(on_message)

    # Pop-up de Nick do chat
    join_user_name = ft.TextField(
        label="Digite seu nome",
        autofocus=True,
        on_submit=join_chat_click, # Enter para entrar no chat
    )

    welcome_dlg = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Bem vindo!"),
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Entrar no chat", on_click=join_chat_click)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Adiciona o pop-up na página
    page.overlay.append(welcome_dlg)

    # Área das mensagens do chat
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # Caixa de mensagem (onde digita as mensagens)
    new_message = ft.TextField(
        hint_text="Mensagem", # Label da caixa
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click, # Enviar com Enter
    )

    # Adicionar tudo na página
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.Colors.BLUE),
            border_radius=20,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.Icons.SEND_OUTLINED,
                    tooltip="Enviar",
                    on_click=send_message_click, # Enter para o botão enviar
                ),
            ]
        ),
    )

ft.app(target=main, view=WEB_BROWSER, port=8000)