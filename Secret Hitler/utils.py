class EmbedColor:
    ERROR = 0
    WARN = 1
    INFO = 2
    SUCCESS = 3


class Node:
	def __init__(self, data):
		self.data = data
		self._next = None

	def __repr__(self):
		return f'<Node: {self.data}>'


class LinkedList:
	def __init__(self, elements: list):
		self.head = self.tail = Node(elements[0])
		self.length = 1
		for e in elements[1:]:
			self.add(e)

	def add(self, node_data):
		node = Node(node_data)
		self.tail._next = node
		self.tail = node
		self.tail._next = self.head
		self.length += 1

	def remove(self, node_data):
		node = Node(node_data)
		n = self.head
		prev = None
		while n.data != node.data:
			prev = n
			n = n._next
			if n == self.head:
				raise IndexError(f'Linked list does not contain {node}')
		if not prev:
			self.head = n._next
			self.tail._next = self.head
		else:
			prev._next = n._next
		self.length -= 1

	def __len__(self):
		return self.length

	def __repr__(self):
		rep = ''
		n = self.head
		while n._next != self.head:
			rep += f'[{n.data}]'
			n = n._next
		rep += f'[{n.data}]'

		return rep


x = LinkedList([1,2,3,4,5])
print(x)
x.remove(-1)
print(x)
x.remove(4)
print(x)
x.remove(5)
print(x)



