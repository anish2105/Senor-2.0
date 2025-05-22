class ChatHistoryManager:
    _instance = None
    chat_history = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatHistoryManager, cls).__new__(cls)
            cls.chat_history = []
        return cls._instance

    def add(self, user, system):
        self.chat_history.append({"user": user, "system": system})

    def get(self):
        return self.chat_history

    def clear(self):
        self.chat_history.clear()

chat_history_manager = ChatHistoryManager()
