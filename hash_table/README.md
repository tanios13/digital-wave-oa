# Implementation explanation

This implementation recreates the functionality of Python's `OrderedDict` with a fixed size: a hash table that maintains insertion/update order for O(1) access to first and last entries.

## 1. Started by implementing a fixed size hash table without the get_first() and get_last().

**Main Logic:**

- **`_find_slot()`**: Uses linear probing to find a key or empty slot. If a slot is occupied, it checks the next slot `(idx + 1) % size` until finding the key or an empty space.

- **`_rehash_cluster()`**: After deletion, rehashes all entries in the subsequent cluster to maintain correct probe sequences. This prevents "holes" from breaking the linear probing chain.

**Why rehashing over tombstones:**

Tombstones accumulate over time and degrade search performance to O(n) in tables with many deletions. Rehashing keeps the table clean and maintains O(1) average case for `insert()` and `get()`, even though `remove()` becomes O(k) where k is the cluster size.

```python
class FixedHashTable:
    
    def __init__(self, size):
        self.size = size
        self.table = [None] * size  # Each entry: None or (key, value)
        self.count = 0
        
    def insert(self, key, value):
        if self.count >= self.size:
            raise Exception("Hash table is full")
        
        idx = self._find_slot(key)
        
        if self.table[idx] is None:
            # New key
            self.count += 1
        
        self.table[idx] = (key, value)
    
    def remove(self, key):
        idx = self._find_slot(key)
        
        if self.table[idx] is None or self.table[idx][0] != key:
            raise KeyError(f"Key '{key}' not found")
        
        self.table[idx] = None
        self.count -= 1
        
        # Rehash all entries in the cluster that follows
        self._rehash_cluster(idx)
    
    def get(self, key):
        idx = self._find_slot(key)
        
        if self.table[idx] is None or self.table[idx][0] != key:
            raise KeyError(f"Key '{key}' not found")
        
        return self.table[idx][1]
    
    
    # === Helper Methods ===
    
    def _hash(self, key):
        """Hash function."""
        return hash(key) % self.size
    
    def _find_slot(self, key):
        """Find slot for key using linear probing."""
        idx = self._hash(key)
        start_idx = idx
        
        while self.table[idx] is not None:
            if self.table[idx][0] == key:
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
            # Remove entry and reinsert it
            key, value = self.table[idx]
            self.table[idx] = None
            self.count -= 1
            
            # Reinsert (will find correct position)
            self.insert(key, value)
            
            idx = (idx + 1) % self.size
            
            if idx == start_idx:
                break
```

## 2. Add the get_first() and get_last() logic

To track insertion/update order in O(1), we add a doubly-linked list alongside the hash table. Each `Node` stores `prev` and `next` pointers. The hash table stores `Node` objects instead of tuples. `head` points to the oldest entry, `tail` to the newest.

**Key operations:**
- `_add_to_end()`: Appends new nodes to tail
- `_move_to_end()`: Moves updated nodes to tail (most recent)
- `_remove_node()`: Unlinks nodes during deletion

**Important:** During `_rehash_cluster()`, we collect all nodes first, clear their slots, then reinsert manually. This preserves their linked list positions while fixing hash table structure.

```python
    class Node:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None

    class FixedHashTable:
        ...

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
```