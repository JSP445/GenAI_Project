class Node:
    """A helper Node class that stores key-value pairs and points to the next node in the sequence."""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class LinkedHashMap:
    """A hybrid data structure combining hash map and linked list properties with recursive capabilities."""
    
    def __init__(self):
        self.head = None
        self.tail = None
        self.map = {}

    def insert(self, key, value):
        """Inserts a key-value pair in the map and links it in the sequence."""
        # If key already exists, update value and return
        if key in self.map:
            self.map[key].value = value
            return
        
        # Create a new node
        new_node = Node(key, value)
        self.map[key] = new_node
        
        # Append node to the end of the list
        if not self.head:
            self.head = new_node
        else:
            self.tail.next = new_node
        
        # Move the tail pointer
        self.tail = new_node

    def get(self, key):
        """Retrieves the value associated with the key, raises KeyError if the key does not exist."""
        if key not in self.map:
            raise KeyError(f"Key '{key}' not found in LinkedHashMap.")
        return self.map[key].value

    def traverse(self):
        """Traverses the linked structure in insertion order and prints key-value pairs."""
        current = self.head
        while current:
            print(f"{current.key}: {current.value}")
            current = current.next

    def recursive_traverse(self, node=None, level=0):
        """Recursively traverses the structure, handling nested LinkedHashMaps."""
        if node is None:
            node = self.head
            
        while node:
            value = node.value
            if isinstance(value, LinkedHashMap):
                print("  " * level + f"{node.key}:")
                value.recursive_traverse(value.head, level + 1)  # Recursive call
            else:
                print("  " * level + f"{node.key}: {value}")
            node = node.next

    def __contains__(self, key):
        """Checks if a key exists in the map."""
        return key in self.map

    def __getitem__(self, key):
        """Gets the value for a given key, enabling bracket notation, raises KeyError if not found."""
        return self.get(key)

    def __setitem__(self, key, value):
        """Sets a key-value pair, enabling bracket notation."""
        self.insert(key, value)

# Create the main LinkedHashMap
lhm = LinkedHashMap()
lhm.insert("name", "Alice")
lhm.insert("age", 30)

# Create a nested LinkedHashMap for address
address = LinkedHashMap()
address.insert("city", "Wonderland")
address.insert("zip", "12345")

# Insert the nested LinkedHashMap as a value
lhm.insert("address", address)

# Insert another level of nesting
contacts = LinkedHashMap()
contacts.insert("email", "alice@example.com")
contacts.insert("phone", "555-1234")
lhm.insert("contacts", contacts)

# Regular traversal (non-recursive)
print("Non-recursive traversal:")
lhm.traverse()

# Recursive traversal
print("\nRecursive traversal:")
lhm.recursive_traverse()
