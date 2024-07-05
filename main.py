from jnius import autoclass
from kivy.app import App
from kivy.lang import Builder
from sjfirebase.jclass import SJFirebaseFirestore
from sjfirebase.jinterface import OnCompleteListener, EventListener
from serialize import serialize_dict_to_map, serialize_map_to_dict


class InspirationalQuoteApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quote_ref = SJFirebaseFirestore.get_db().document("inspiration/quotes")
        self.listener = None
        self.snapshot_listener = None

    def build(self):
        return Builder.load_file("inspire.kv")

    def on_start(self):
        self.snapshot_listener = EventListener(self.populate_quote_snapshot)
        self.quote_ref.addSnapshotListener(self.snapshot_listener)

    def save_quote(self, quote, author):
        self.listener = OnCompleteListener(lambda task: print(task.isSuccessful()))
        data = serialize_dict_to_map({"author": author, "quote": quote})
        (
            self.quote_ref
            .set(data)
            .addOnCompleteListener(self.listener)
        )

    def fetch_quote(self):
        self.listener = OnCompleteListener(self.populate_quote)
        (
            self.quote_ref
            .get()
            .addOnCompleteListener(self.listener)
        )

    def populate_quote(self, task):
        if task.isSuccessful():
            document = task.getResult()
            print(document.getString("quote"))
            print(document.getString("author"))
            data = serialize_map_to_dict(document.getData())
            print(data)
            self.root.ids.lbl.quote = data["quote"]
            self.root.ids.lbl.author = data["author"]

    def populate_quote_snapshot(self, snapshot, error):
        Objects = autoclass("java.util.Objects")
        # Type = autoclass("com.google.firebase.firestore.DocumentChange$Type")
        print(dir(snapshot))
        if not Objects.isNull(error):
            print(error.getLocalizedMessage())
            return

        if not Objects.isNull(snapshot) and snapshot.exists():
            self.root.ids.lbl.quote = snapshot.getString("quote")
            self.root.ids.lbl.author = snapshot.getString("author")


if __name__ == "__main__":
    InspirationalQuoteApp().run()
