class EmbedColor:
    ERROR = 14024704
    WARN = 16760064
    INFO = 31163
    SUCCESS = 2459904


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

    def __repr__(self):
        return f'<Node: {self.data}>'


class LinkedList:
    """A circular linked list implementation."""
    def __init__(self):
        self.head = self.tail = None
        self.length = 0
        self.data_types = set([int])
        self.cur = None
        self.looped = False

    @property
    def elements(self):
        """Returns all of the elements in the linked list."""
        elems = []
        node = self.head
        if node is None:
            return []
        elems.append(node.data)
        while node.next != self.head:
            node = node.next
            elems.append(node.data)
        return elems
    

    def add(self, node_data):
        """Adds a node to the tail of the linked list."""
        node = Node(node_data)
        if self.head is None or self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.tail.next = self.head
        self.length += 1

    def find(self, value, attr=None):
        """Finds an element with an attribute equal to key."""
        if self.head is None:
            return None
        for elem in self:
            if (attr is None and elem.data == value) or (attr is not None and getattr(elem.data, attr) == value):
                return elem
        return None

    def remove(self, node):
        """Removes a link from the list."""
        n = self.head
        prev = None
        while n != node:
            prev = n
            n = n.next
            if n == self.head:
                raise KeyError(f'Linked list does not contain {node}')
        if not prev:
            self.head = n.next
            self.tail.next = self.head
        else:
            prev.next = n.next
        self.length -= 1

    def __contains__(self, data):
        """Checks if an element is in the list."""
        if self.head is None:
            return False
        node = self.head
        while node.next is not self.head:
            if node.data == data:
                return True
            node = node.next
        return False

    def __getitem__(self, sliced):
        """Adds indexing support."""
        return self.elements[sliced]

    def __iter__(self):
        self.cur = self.head
        return self

    def __len__(self):
        return self.length

    def __next__(self):
        if self.looped:
            self.looped = False
            raise StopIteration
        cur = self.cur
        self.cur = cur.next
        if self.cur == self.head:
            self.looped = True
        return cur

    def __repr__(self):
        rep = ''
        if self.head is None:
            return '[]'
        n = self.head
        while n.next != self.head:
            rep += f'[{n.data}]'
            n = n.next
        rep += f'[{n.data}]'
        return rep