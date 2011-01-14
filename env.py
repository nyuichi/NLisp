class Env(dict):
    def __init__(self, outer=None):
        self.outer = outer

    def find(self, var):
        try:
            return self[var] if var in self else self.outer.find(var)
        except:
            raise Exception("Not found a symbol: "+str(var))
