
import threading
import requests
import math

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup


# ==========================================
# JARVIS CONFIGURATION
# ==========================================

API = "https://jarvis3-1.onrender.com"

JARVIS_OWNER = "Anant Kumar"

OWNER_QUESTIONS = [
    "who is your owner",
    "who is your creator",
    "who created you",
    "who made you",
    "who developed you",
    "who do you belong to",
    "who built you",
    "your owner",
    "your creator",
    "your developer",
    "who owns you",
    "who is your master",
    "tumhara malik kaun",
    "tumhara owner kaun",
    "tumhe kisne banaya",
    "tumko kisne banaya",
    "aapko kisne banaya",
    "jarvis ka owner",
    "jarvis ko kisne banaya",
    "jarvis kisne banaya",
    "jarvis ka creator",
    "jarvis ka malik",
]

BG = (0.027, 0.043, 0.078, 1)
PANEL = (0.051, 0.082, 0.137, 1)
PANEL2 = (0.067, 0.118, 0.188, 1)
CYAN = (0, 0.85, 1, 1)
BLUE = (0.08, 0.38, 1, 1)
WHITE = (0.91, 0.97, 1, 1)
MUTED = (0.48, 0.59, 0.70, 1)
GREEN = (0.1, 0.9, 0.55, 1)
RED = (1, 0.25, 0.3, 1)


# ==========================================
# UI HELPERS
# ==========================================

def rounded_background(widget, color, radius=16):
    with widget.canvas.before:
        Color(*color)
        widget.bg_rect = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[dp(radius)]
        )

    def update(*args):
        widget.bg_rect.pos = widget.pos
        widget.bg_rect.size = widget.size

    widget.bind(pos=update, size=update)


class Reactor(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.phase = 0

        self.bind(pos=self.draw, size=self.draw)

        Clock.schedule_interval(self.animate, 1 / 30)

    def animate(self, dt):
        self.phase += dt * 2
        self.draw()

    def draw(self, *args):
        self.canvas.clear()

        cx = self.center_x
        cy = self.center_y

        radius = min(self.width, self.height) * 0.43

        pulse = 1 + math.sin(self.phase * 2) * 0.04

        with self.canvas:

            Color(0, 0.5, 1, 0.12)

            Ellipse(
                pos=(cx-radius*1.3, cy-radius*1.3),
                size=(radius*2.6, radius*2.6)
            )

            Color(*CYAN)

            Line(
                circle=(cx, cy, radius*pulse),
                width=1.8
            )

            Color(0.05, 0.5, 1, 0.9)

            Line(
                circle=(cx, cy, radius*0.72),
                width=1.5
            )

            Color(0, 0.9, 1, 0.15)

            Ellipse(
                pos=(cx-radius*0.55, cy-radius*0.55),
                size=(radius*1.1, radius*1.1)
            )

            Color(*CYAN)

            Ellipse(
                pos=(cx-radius*0.27, cy-radius*0.27),
                size=(radius*0.54, radius*0.54)
            )

            Color(1, 1, 1, 0.9)

            Ellipse(
                pos=(cx-radius*0.09, cy-radius*0.09),
                size=(radius*0.18, radius*0.18)
            )


class ChatBubble(BoxLayout):

    def __init__(self, message, is_user=False, **kwargs):

        super().__init__(
            orientation="vertical",
            size_hint=(None, None),
            padding=[dp(13), dp(10)],
            **kwargs
        )

        self.width = Window.width * 0.82

        color = PANEL2 if is_user else PANEL

        with self.canvas.before:

            Color(*color)

            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )

        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )

        label = Label(
            text=str(message),
            color=WHITE,
            font_size=sp(14),
            halign="left",
            valign="middle",
            size_hint=(1, None),
            markup=False
        )

        label.bind(
            width=lambda instance, value:
            setattr(instance, "text_size", (value, None))
        )

        label.bind(
            texture_size=lambda instance, value:
            setattr(instance, "height", value[1] + dp(5))
        )

        self.add_widget(label)

        label.texture_update()

        self.height = max(
            dp(42),
            label.texture_size[1] + dp(25)
        )

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ChatRow(BoxLayout):

    def __init__(self, message, is_user=False, **kwargs):

        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            padding=[dp(8), dp(5)],
            spacing=dp(5),
            **kwargs
        )

        bubble = ChatBubble(message, is_user)

        self.height = bubble.height + dp(10)

        if is_user:
            self.add_widget(Widget())
            self.add_widget(bubble)
        else:
            self.add_widget(bubble)
            self.add_widget(Widget())


class AnchorBox(FloatLayout):
    pass


# ==========================================
# MAIN JARVIS APP
# ==========================================

class JARVISApp(App):

    def build(self):

        Window.clearcolor = BG

        self.token = None
        self.email = None

        self.history = []
        self.session_id = None

        self.busy = False

        self.root_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(7),
            padding=[dp(12), dp(10)]
        )

        self.build_header()
        self.build_reactor()
        self.build_chat()
        self.build_composer()

        self.add_message(
            "Hello! I am JARVIS.\n\n"
            "Your personal AI assistant is ready.\n"
            "Created by Anant Kumar.\n\n"
            "How may I help you today?",
            False
        )

        return self.root_layout

    # ======================================
    # HEADER
    # ======================================

    def build_header(self):

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(55),
            spacing=dp(5)
        )

        title = Label(
            text="[b]J.A.R.V.I.S[/b]",
            markup=True,
            color=CYAN,
            font_size=sp(22),
            halign="left"
        )

        title.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        header.add_widget(title)

        self.auth_button = Button(
            text="SIGN IN",
            size_hint=(None, None),
            size=(dp(90), dp(38)),
            background_normal="",
            background_color=PANEL2,
            color=CYAN,
            font_size=sp(11),
            bold=True
        )

        self.auth_button.bind(
            on_release=self.open_auth
        )

        header.add_widget(self.auth_button)

        new_button = Button(
            text="+ NEW",
            size_hint=(None, None),
            size=(dp(75), dp(38)),
            background_normal="",
            background_color=PANEL2,
            color=WHITE,
            font_size=sp(11)
        )

        new_button.bind(
            on_release=self.new_chat
        )

        header.add_widget(new_button)

        self.root_layout.add_widget(header)

    # ======================================
    # ARC REACTOR
    # ======================================

    def build_reactor(self):

        reactor_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(125),
            spacing=dp(2)
        )

        reactor = Reactor(
            size_hint=(None, None),
            size=(dp(85), dp(85))
        )

        center = AnchorBox()

        center.add_widget(reactor)

        reactor_box.add_widget(center)

        status = Label(
            text="● SYSTEM ONLINE",
            color=GREEN,
            font_size=sp(10),
            size_hint_y=None,
            height=dp(20)
        )

        reactor_box.add_widget(status)

        self.root_layout.add_widget(reactor_box)

    # ======================================
    # CHAT AREA
    # ======================================

    def build_chat(self):

        self.scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3),
            scroll_type=["bars", "content"]
        )

        self.messages = GridLayout(
            cols=1,
            spacing=dp(3),
            size_hint_y=None,
            padding=[0, dp(5)]
        )

        self.messages.bind(
            minimum_height=self.messages.setter("height")
        )

        self.scroll.add_widget(self.messages)

        self.root_layout.add_widget(self.scroll)

    # ======================================
    # MESSAGE INPUT
    # ======================================

    def build_composer(self):

        composer = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(55),
            spacing=dp(7)
        )

        self.message_input = TextInput(
            hint_text="Message JARVIS...",
            multiline=False,
            font_size=sp(14),
            foreground_color=WHITE,
            hint_text_color=MUTED,
            background_normal="",
            background_active="",
            background_color=PANEL,
            padding=[dp(12), dp(15)],
            cursor_color=CYAN
        )

        self.message_input.bind(
            on_text_validate=lambda instance:
            self.send_message()
        )

        send = Button(
            text="➤",
            size_hint=(None, 1),
            width=dp(55),
            background_normal="",
            background_color=(0, 0.45, 0.8, 1),
            color=WHITE,
            font_size=sp(22),
            bold=True
        )

        send.bind(
            on_release=lambda instance:
            self.send_message()
        )

        composer.add_widget(self.message_input)
        composer.add_widget(send)

        self.root_layout.add_widget(composer)

        footer = Label(
            text="JARVIS AI  •  CREATED BY ANANT KUMAR",
            color=MUTED,
            font_size=sp(9),
            size_hint_y=None,
            height=dp(20)
        )

        self.root_layout.add_widget(footer)

    # ======================================
    # CHAT MESSAGE
    # ======================================

    def add_message(self, message, is_user=False):

        row = ChatRow(str(message), is_user)

        self.messages.add_widget(row)

        Clock.schedule_once(
            lambda dt:
            setattr(self.scroll, "scroll_y", 0),
            0.1
        )

    # ======================================
    # NEW CHAT
    # ======================================

    def new_chat(self, *args):

        if self.busy:
            return

        self.history = []
        self.session_id = None

        self.messages.clear_widgets()

        self.add_message(
            "New conversation started.\n"
            "How can I help you?",
            False
        )

    # ======================================
    # OWNER QUESTION DETECTOR
    # ======================================

    def is_owner_question(self, message):

        normalized = message.lower().strip()

        for character in ["?", "!", ".", ","]:
            normalized = normalized.replace(character, "")

        normalized = " ".join(normalized.split())

        return any(
            question in normalized
            for question in OWNER_QUESTIONS
        )

    # ======================================
    # SEND MESSAGE
    # ======================================

    def send_message(self, *args):

        message = self.message_input.text.strip()

        if not message or self.busy:
            return

        self.message_input.text = ""

        self.add_message(message, True)

        # INSTANT OWNER RESPONSE

        if self.is_owner_question(message):

            answer = (
                "My owner and creator is Anant Kumar. "
                "I am JARVIS, his personal AI assistant."
            )

            self.add_message(answer, False)

            if not self.token:
                self.history.extend([
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": answer}
                ])

            return

        self.busy = True

        self.add_message("JARVIS is thinking...", False)

        threading.Thread(
            target=self.chat_request,
            args=(message,),
            daemon=True
        ).start()

    # ======================================
    # AI REQUEST
    # ======================================

    def chat_request(self, message):

        try:

            if self.token:

                headers = {
                    "Authorization": "Bearer " + self.token,
                    "Content-Type": "application/json"
                }

                payload = {
                    "message": message,
                    "session_id": self.session_id
                }

                response = requests.post(
                    API + "/chat",
                    json=payload,
                    headers=headers,
                    timeout=90
                )

            else:

                payload = {
                    "message": message,
                    "history": self.history
                }

                response = requests.post(
                    API + "/guest-chat",
                    json=payload,
                    timeout=90
                )

            if response.status_code >= 400:

                try:
                    error = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error = response.text

                raise Exception(str(error))

            data = response.json()

            answer = (
                data.get("assistant")
                or data.get("response")
                or data.get("reply")
                or data.get("answer")
                or "I could not generate a response."
            )

            if data.get("session_id"):
                self.session_id = data["session_id"]

            if not self.token:

                self.history.append({
                    "role": "user",
                    "content": message
                })

                self.history.append({
                    "role": "assistant",
                    "content": str(answer)
                })

            Clock.schedule_once(
                lambda dt:
                self.finish_response(str(answer)),
                0
            )

        except requests.exceptions.Timeout:

            Clock.schedule_once(
                lambda dt:
                self.finish_response(
                    "The AI server took too long to respond. "
                    "Please try again."
                ),
                0
            )

        except requests.exceptions.ConnectionError:

            Clock.schedule_once(
                lambda dt:
                self.finish_response(
                    "Unable to connect to JARVIS server. "
                    "Please check your internet connection."
                ),
                0
            )

        except Exception as error:

            Clock.schedule_once(
                lambda dt:
                self.finish_response(
                    "Error: " + str(error)
                ),
                0
            )

    # ======================================
    # RESPONSE DISPLAY
    # ======================================

    def finish_response(self, answer):

        # Remove the latest temporary thinking message.
        if self.messages.children:
            self.messages.remove_widget(
                self.messages.children[0]
            )

        self.add_message(answer, False)

        self.busy = False

    # ======================================
    # LOGIN / SIGNUP
    # ======================================

    def open_auth(self, *args):

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(15)
        )

        heading = Label(
            text="JARVIS ACCOUNT",
            color=CYAN,
            font_size=sp(19),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )

        content.add_widget(heading)

        email_input = TextInput(
            hint_text="Email address",
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            background_color=PANEL,
            foreground_color=WHITE,
            hint_text_color=MUTED,
            padding=dp(12)
        )

        password_input = TextInput(
            hint_text="Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            background_color=PANEL,
            foreground_color=WHITE,
            hint_text_color=MUTED,
            padding=dp(12)
        )

        content.add_widget(email_input)
        content.add_widget(password_input)

        status = Label(
            text="Sign in or create your account",
            color=MUTED,
            font_size=sp(11),
            size_hint_y=None,
            height=dp(35)
        )

        content.add_widget(status)

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        login_btn = Button(
            text="SIGN IN",
            background_normal="",
            background_color=(0, 0.4, 0.8, 1),
            color=WHITE
        )

        signup_btn = Button(
            text="SIGN UP",
            background_normal="",
            background_color=(0, 0.55, 0.5, 1),
            color=WHITE
        )

        buttons.add_widget(login_btn)
        buttons.add_widget(signup_btn)

        content.add_widget(buttons)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.9, None),
            height=dp(340),
            separator_color=CYAN,
            background_color=BG
        )

        login_btn.bind(
            on_release=lambda instance:
            self.authenticate(
                "login",
                email_input.text,
                password_input.text,
                status,
                popup
            )
        )

        signup_btn.bind(
            on_release=lambda instance:
            self.authenticate(
                "signup",
                email_input.text,
                password_input.text,
                status,
                popup
            )
        )

        popup.open()

    # ======================================
    # AUTHENTICATION
    # ======================================

    def authenticate(
        self,
        action,
        email,
        password,
        status,
        popup
    ):

        email = email.strip()
        password = password.strip()

        if not email or not password:

            status.text = "Enter email and password."

            return

        status.text = "Connecting to JARVIS server..."

        threading.Thread(
            target=self.auth_request,
            args=(
                action,
                email,
                password,
                status,
                popup
            ),
            daemon=True
        ).start()

    def auth_request(
        self,
        action,
        email,
        password,
        status,
        popup
    ):

        try:

            response = requests.post(
                API + "/auth/" + action,
                json={
                    "email": email,
                    "password": password
                },
                timeout=30
            )

            data = response.json()

            if response.status_code >= 400:

                raise Exception(
                    data.get(
                        "detail",
                        "Authentication failed"
                    )
                )

            token = (
                data.get("access_token")
                or data.get("token")
                or data.get("accessToken")
            )

            if not token:

                raise Exception(
                    "Account created. Please sign in."
                    if action == "signup"
                    else "Server did not return an access token."
                )

            self.token = token
            self.email = email

            Clock.schedule_once(
                lambda dt:
                self.auth_success(popup),
                0
            )

        except Exception as error:

            Clock.schedule_once(
                lambda dt:
                setattr(status, "text", str(error)),
                0
            )

    def auth_success(self, popup):

        popup.dismiss()

        self.auth_button.text = "ACCOUNT"

        self.add_message(
            "Welcome! You are signed in as " + self.email,
            False
        )

    # ======================================
    # APP CLOSE
    # ======================================

    def on_stop(self):
        self.busy = False


# ==========================================
# START APP
# ==========================================

if __name__ == "__main__":
    JARVISApp().run()
