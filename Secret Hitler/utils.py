class EmbedColor:
    ERROR = 0
    WARN = 1
    INFO = 2
    SUCCESS = 3


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

    def __repr__(self):
        return f'<Node: {self.data}>'


class LinkedList:
    """
    A circular linked list implementation
    """
    def __init__(self):
        self.head = self.tail = None
        self.length = 0
        self.data_types = set([int])

    @property
    def elements(self):
        """
        Returns all of the elements in the linked list
        """
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
        """
        Adds a node to the tail of the linked list
        """
        node = Node(node_data)
        if self.head is None or self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.tail.next = self.head
        self.length += 1

    def find(self, key, attr=None):
        """
        Finds an element with an attribute equal to key
        """
        if self.head is None:
            return None
        elem = None
        for i in range(self.length):
            elem = self.head if elem is None else elem.next
            if i == key or (attr is not None and getattr(elem.data, attr) == key):
                return elem
        return None

    def remove(self, data):
        """
        Removes a link from the list
        """
        node = Node(data)
        n = self.head
        prev = None
        while n.data != node.data:
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
        """
        Checks if an element is in the list
        """
        if self.head is None:
            return False
        node = self.head
        while node.next is not self.head:
            if node.data == data:
                return True
            node = node.next
        return False

    def __getitem__(self, index):
        """
        Adds indexing support
        """
        if type(index) is not int:
            raise TypeError(f'Index for LinkedList must be of type int')
        if type(index) is int:
            if index < 0:
                index %= self.length
            if index >= self.length:
                raise IndexError(f'Index {index} out of range for LinkedList')
        return self.find(index)

    def __len__(self):
        return self.length

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