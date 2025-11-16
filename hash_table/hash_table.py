class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class FixedHashTable:
    
    def __init__(self, size):
        self.size = size
        self.table = [None] * size  # Each entry: None or Node
        self.count = 0
        self.head = None  # Oldest (first inserted/updated)
        self.tail = None  # Newest (most recently inserted/updated)
        
    def insert(self, key, value):
        idx = self._find_slot(key)
        
        if self.table[idx] is not None and self.table[idx].key == key:
            # Update existing
            node = self.table[idx]
            node.value = value
            # Update history - move to end
            self._move_to_end(node)
        else:
            # New insertion
            if self.count >= self.size:
                raise Exception("Hash table is full")
            
            node = Node(key, value)
            self.table[idx] = node
            self._add_to_end(node)
            self.count += 1
    
    def remove(self, key):
        idx = self._find_slot(key)
        
        if self.table[idx] is None or self.table[idx].key != key:
            raise KeyError(f"Key '{key}' not found")
        
        node = self.table[idx]
        self._remove_node(node)
        self.table[idx] = None
        self.count -= 1
        
        # Rehash all entries in the cluster that follows
        self._rehash_cluster(idx)
    
    def get(self, key):
        idx = self._find_slot(key)
        
        if self.table[idx] is None or self.table[idx].key != key:
            raise KeyError(f"Key '{key}' not found")
        
        return self.table[idx].value
    
    def get_first(self):
        if self.head is None:
            return None
        return (self.head.key, self.head.value)

    def get_last(self):
        if self.tail is None:
            return None
        return (self.tail.key, self.tail.value)
    
    # === Helper Methods ============================================================
    
    def _hash(self, key):
        """Hash function."""
        return hash(key) % self.size
    
    def _find_slot(self, key):
        """Find slot for key using linear probing."""
        idx = self._hash(key)
        start_idx = idx
        
        while self.table[idx] is not None:
            if self.table[idx].key == key:
                return idx
            
            idx = (idx + 1) % self.size
            
            # Checked the whole table
            if idx == start_idx:
                break
        
        return idx
    
    def _rehash_cluster(self, start_idx):
        """Rehash entries after a deletion to maintain probe sequences."""
        idx = (start_idx + 1) % self.size
        
        while self.table[idx] is not None:
            # Save the node (don't touch linked list yet)
            node = self.table[idx]
            
            # Remove from table only
            self.table[idx] = None
            self.count -= 1
            
            # Find new slot and reinsert without changing linked list order
            new_idx = self._find_slot(node.key)
            self.table[new_idx] = node
            self.count += 1
            
            idx = (idx + 1) % self.size
            
            if idx == start_idx:
                break
    
    def _remove_node(self, node):
        """Remove node from linked list."""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
            
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
    
    def _add_to_end(self, node):
        """Add node to end of linked list."""
        if self.tail is None:
            # Empty list
            self.head = self.tail = node
        else:
            # Add to end
            self.tail.next = node
            node.prev = self.tail
            node.next = None
            self.tail = node
    
    def _move_to_end(self, node):
        """Move existing node to end of linked list."""
        if node == self.tail:
            return  # Already at end
        
        # Remove from current position
        self._remove_node(node)
        # Add to end
        self._add_to_end(node)