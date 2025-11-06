from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.popup import Popup
from plyer import notification
import datetime, json, os

FILENAME = "medicine_data.json"


# ---------- Data Functions ----------
def load_data():
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_data(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)


# ---------- Popup Helper ----------
def show_popup(title, msg):
    popup = Popup(title=title,
                  content=Label(text=msg),
                  size_hint=(0.8, 0.4))
    popup.open()


# ---------- Dashboard Screen ----------
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        layout.add_widget(Label(text="💊 Healtrix Dashboard", font_size=26, size_hint_y=None, height=60))

        add_btn = Button(text="➕ Add Medicine", size_hint_y=None, height=60)
        view_btn = Button(text="📋 View Medicines", size_hint_y=None, height=60)
        ai_btn = Button(text="🤖 AI Chat Assistant", size_hint_y=None, height=60)

        add_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'add'))
        view_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'view'))
        ai_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'ai'))

        layout.add_widget(add_btn)
        layout.add_widget(view_btn)
        layout.add_widget(ai_btn)

        self.add_widget(layout)


# ---------- Add Medicine Screen ----------
class AddMedicineScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Label(text="➕ Add Medicine Details", font_size=22, size_hint_y=None, height=40))

        self.name_input = TextInput(hint_text="Medicine name", multiline=False)
        self.dosage_input = TextInput(hint_text="Dosage (e.g., 1 tablet)", multiline=False)
        self.time_input = TextInput(hint_text="Time (HH:MM 24hr)", multiline=False)
        self.duration_input = TextInput(hint_text="Duration (days)", multiline=False, input_filter="int")

        layout.add_widget(self.name_input)
        layout.add_widget(self.dosage_input)
        layout.add_widget(self.time_input)
        layout.add_widget(self.duration_input)

        save_btn = Button(text="💾 Save", size_hint_y=None, height=50)
        back_btn = Button(text="⬅ Back", size_hint_y=None, height=50)

        save_btn.bind(on_press=self.save_medicine)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))

        layout.add_widget(save_btn)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def save_medicine(self, instance):
        name = self.name_input.text.strip()
        dosage = self.dosage_input.text.strip()
        time_str = self.time_input.text.strip()
        duration = self.duration_input.text.strip()

        if not (name and dosage and time_str and duration):
            show_popup("Error", "⚠️ Please fill all fields!")
            return

        today = datetime.date.today().strftime("%Y-%m-%d")
        medicine = {
            "name": name,
            "dosage": dosage,
            "time": time_str,
            "start_date": today,
            "duration": int(duration)
        }

        data = load_data()
        data.append(medicine)
        save_data(data)

        # Toast-like popup instead of Android notification (no crash)
        show_popup("Saved", f"{name} at {time_str} added successfully!")

        self.name_input.text = ""
        self.dosage_input.text = ""
        self.time_input.text = ""
        self.duration_input.text = ""


# ---------- View Medicine Screen ----------
class ViewMedicineScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.layout.add_widget(Label(text="📋 Added Medicines", font_size=22, size_hint_y=None, height=40))

        self.scroll = ScrollView()
        self.list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        self.scroll.add_widget(self.list_box)

        self.layout.add_widget(self.scroll)
        back_btn = Button(text="⬅ Back", size_hint_y=None, height=50)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

        Clock.schedule_once(lambda dt: self.refresh())

    def refresh(self, *args):
        self.list_box.clear_widgets()
        data = load_data()
        if not data:
            self.list_box.add_widget(Label(text="No medicines added yet.", size_hint_y=None, height=40))
            return

        for i, med in enumerate(data):
            row = BoxLayout(size_hint_y=None, height=40, spacing=10)
            row.add_widget(Label(text=f"{i+1}. {med['name']} - {med['dosage']} at {med['time']} ({med['duration']} days)"))
            del_btn = Button(text="🗑 Delete", size_hint_x=None, width=100)
            del_btn.bind(on_press=lambda x, idx=i: self.delete_medicine(idx))
            row.add_widget(del_btn)
            self.list_box.add_widget(row)

    def delete_medicine(self, index):
        data = load_data()
        if 0 <= index < len(data):
            deleted = data.pop(index)
            save_data(data)
            show_popup("Deleted", f"{deleted['name']} removed.")
            self.refresh()


# ---------- AI Chat Screen (placeholder for API key) ----------
class AIChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        layout.add_widget(Label(text="🤖 AI Chat Assistant", font_size=22, size_hint_y=None, height=40))

        self.chat_history = Label(text="Chat will appear here...", halign="left", valign="top")
        self.chat_history.bind(size=self.chat_history.setter('text_size'))

        self.input = TextInput(hint_text="Ask something...", multiline=False)
        send_btn = Button(text="Send", size_hint_y=None, height=50)
        back_btn = Button(text="⬅ Back", size_hint_y=None, height=50)

        send_btn.bind(on_press=self.send_message)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))

        layout.add_widget(self.chat_history)
        layout.add_widget(self.input)
        layout.add_widget(send_btn)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def send_message(self, instance):
        user_msg = self.input.text.strip()
        if not user_msg:
            return
        self.chat_history.text += f"\n👤 You: {user_msg}\n🤖 AI: (Response here... API key to be added)"
        self.input.text = ""


# ---------- Main App ----------
class MedicineApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(AddMedicineScreen(name="add"))
        sm.add_widget(ViewMedicineScreen(name="view"))
        sm.add_widget(AIChatScreen(name="ai"))
        return sm


if __name__ == "__main__":
    MedicineApp().run()
    