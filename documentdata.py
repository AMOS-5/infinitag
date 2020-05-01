class DocumentData:

    def __init__(self, name, path, type, lang, size, createdAt):
        self.name = name
        self.path = path
        self.type = type
        self.lang = lang
        self.size = size
        self.createdAt = createdAt

    def asDict(self):
        return {
            "name" : self.name,
            "path" : self.path,
            "type" : self.type,
            "lang" : self.lang,
            "size" : self.size,
            "createdAt" : self.createdAt
        }