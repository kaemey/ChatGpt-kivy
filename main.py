from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.uix.button import Button
from kivy.lang import Builder

import pyperclip
import asyncio
import g4f

g4f.check_version = False  # Disable automatic version checking

Builder.load_file("main.kv")

window_width = 800
window_height = 600

Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', window_width)
Config.set('graphics', 'height', window_height)


class Question(Label):
    pass

class Answer(Label):
    pass

class MainLayout(BoxLayout):
    pass

class chooseGPTWidget(AnchorLayout):
    pass

class MyApp(App):

    def build(self):
        self.response = None
        self.context = list()
        form = BoxLayout(orientation='horizontal', padding = 10)

        aside = AnchorLayout(size_hint=[0.2, 1], anchor_x='center', anchor_y='top')
        chooseChat = Label(text="New Chat", text_size=[window_width*0.2, window_height+50], valign="top", halign="center")
        aside.add_widget(chooseChat)
        form.add_widget(aside)
        
        chooseGPT = chooseGPTWidget(size_hint=[0.2, 1], anchor_x='center', anchor_y='top', padding = [35,35,0,0])
        chooseGPTButton = Button(size_hint=[1, 0.05], text="ChatGPT 3.5", font_size=14)
        chooseGPT.add_widget(chooseGPTButton)
        form.add_widget(chooseGPT)

        main = MainLayout(orientation='vertical', padding = 20)

        main.add_widget(Widget(size_hint_y=0.1))

        self.messengerWidget = AnchorLayout(size_hint=[1, 0.6], anchor_x='left', anchor_y='top')
        scroll = ScrollView(size_hint=[1,None], size=(500, 450))
        self.scrollBox = GridLayout(size_hint=[1,None], cols=1)
        self.scrollBox.bind(minimum_height=self.scrollBox.setter('height'))
        self.scrollBox.add_widget(Answer(text="ChatGPT:\nПривет! Чем могу помочь тебе сегодня?",color=[0,0,0,1]))
        scroll.add_widget(self.scrollBox)
        self.messengerWidget.add_widget(scroll)

        main.add_widget(self.messengerWidget)

        inputsWidget = AnchorLayout(size_hint=[1, 0.2], anchor_x='center', anchor_y='center')
        bl = BoxLayout(orientation='horizontal', size_hint=[0.8, 0.5])
        self.textInput = TextInput()
        bl.add_widget(self.textInput)
        sendMessageButton = Button(text="SEND", font_size=14,size_hint=[0.2, 1])
        sendMessageButton.bind(on_press=self.sendMesege)
        bl.add_widget(sendMessageButton)
        inputsWidget.add_widget(bl)

        main.add_widget(inputsWidget)

        # Нижняя кнопка Скопировать ответ
        copyButtonWidget = AnchorLayout(size_hint=[1, 0.05], anchor_x='center', anchor_y='center')
        copyButton = Button(text="Скопировать ответ",size_hint=[0.4, 1])
        copyButton.bind(on_press=self.copyResponse)
        copyButtonWidget.add_widget(copyButton)
        main.add_widget(copyButtonWidget)

        form.add_widget(main)

        # Привязываем обработчик событий нажатия на клаву к form
        TestKeyboard = Window.request_keyboard(None,form)

        TestKeyboard.bind(on_key_down = self._on_keyboard_down)

        return form

    def sendMesege(self, instance):
        if self.textInput.text == "":
            return
        
        inputText = self.textInput.text
        self.textInput.text = ""
        self.response = self.getResponse(inputText)

        self.scrollBox.add_widget(Widget())

        self.scrollBox.add_widget(Question(text="Вы:\n"+inputText,color=[0,0,0,1]))

        step = 150
        if len(self.response) > step: 
            self.splitAnswer(self.response, step)
        else:
            self.scrollBox.add_widget(Answer(text="ChatGPT:\n"+self.response,color=[0,0,0,1]))

    def splitAnswer(self, text, step, pos = 0):
        text = text.replace("\n"," ")
        text  = "ChatGPT:\n"+text
        print(text)

        i = pos + step        

        founded = False

        while i < len(text):
            
            i = i + 1
            founded = False

            if (text[i] == "."):

                if (len(text) < i+step):
                    self.scrollBox.add_widget(Answer(text=text[pos:i+1],color=[0,0,0,1]))
                    self.scrollBox.add_widget(Answer(text=text[i+1:len(text)],color=[0,0,0,1]))     
                    founded = True
                    break

                self.scrollBox.add_widget(Answer(text=text[pos:i+1],color=[0,0,0,1]))
                
                pos = i+2
                i = i + step
                founded = True

        if not founded:
            self.scrollBox.add_widget(Answer(text=text[pos+1:len(text)],color=[0,0,0,1]))

    def copyResponse(self, instance: Button):
        pyperclip.copy(self.response)

    def updateMessenger(self):
        self.messengerWidget.clear_widgets()

    def getResponse(self, content):
        self.context.append({"role": "user", "content": content})
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=self.context,
        )  # Alternative model setting
        self.context.append({"role": "assistant", "content": response})
        return response
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if (keycode[1] == 'enter'):
            self.sendMesege(None)

if __name__ == '__main__':
    MyApp().run()