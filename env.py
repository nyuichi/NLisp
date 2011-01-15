class Env(dict):
    def __init__(self, outer=None):
        self.outer = outer

    def find(self, var):
        if var in self:
            return self[var]
        elif self.outer is not None:
            return self.outer.find(var)
        else:
            raise Exception("Not found a symbol: "+str(var))



