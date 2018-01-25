class CategoryTree():
    def __init__(self):
        self.root = {}

    def add_category(self, category, parent):
        if parent is None:
            self.root[category] = []
        elif parent in self.root.keys():
            self.root[parent].append(category)
        else:
            raise(KeyError)

    def get_children(self, parent):
        if parent in self.root.keys():
            return self.root[parent]
        else:
            return []


c = CategoryTree()
c.add_category('A', None)
c.add_category('B', 'A')
c.add_category('C', 'A')
# c.add_category('C', 'A')

print(','.join(c.get_children('A')))
print(','.join(c.get_children('B')))
