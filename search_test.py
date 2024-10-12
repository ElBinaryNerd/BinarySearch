import time
import pickle

# Binary Tree for each individual 16-bit band
class BinaryTreeNode:
    def __init__(self):
        self.value = 0
        self.left = None
        self.right = None
        self.leaf = []

class BinaryTree:
    def __init__(self, height=16):  # Accept height as a parameter
        self.root = self._build_tree(height)  # Build tree dynamically based on the given height

    def _build_tree(self, height):
        if height == 0:
            return BinaryTreeNode()
        node = BinaryTreeNode()
        node.left = self._build_tree(height - 1)
        node.right = self._build_tree(height - 1)
        return node

    def insert(self, bit_sequence, id):
        current_node = self.root
        for bit in bit_sequence:
            current_node.value = 1  # Marking node as visited
            if bit == '0':
                current_node = current_node.left
            else:
                current_node = current_node.right
        current_node.value = 1  # Mark leaf as visited
        current_node.leaf.append(id)  # Add the ID to the leaf

    def traverse(self, bit_sequence):
        current_node = self.root
        for bit in bit_sequence:
            if current_node.value == 0:
                return []  # Stop if a node has a value of 0
            if bit == '0':
                current_node = current_node.left
            else:
                current_node = current_node.right
        return current_node.leaf if current_node else []

# Interface to manage 8 bands, creating 8 binary trees
class BinaryTreeManager:
    SEPARATOR = b'|TREE|'  # Define a separator for splitting tree data

    def __init__(self, tree_height=16, tree_range=8):
        # Create 8 trees, each with a specified height
        self.tree_range = tree_range
        self.trees = [BinaryTree(tree_height) for _ in range(tree_range)]

    def insert(self, id, band1, band2, band3, band4, band5, band6, band7, band8):
        bands = [band1, band2, band3, band4, band5, band6, band7, band8]
        # Insert into each tree for each band
        for i in range(self.tree_range):
            self.trees[i].insert(bands[i], id)

    def search(self, band1, band2, band3, band4, band5, band6, band7, band8):
        bands = [band1, band2, band3, band4, band5, band6, band7, band8]
        results = []
        # Traverse each tree with corresponding 16-bit sequence
        for i in range(self.tree_range):
            result = self.trees[i].traverse(bands[i])
            #if not result:
            #    results.append([])  # Stop if one of the trees doesn't contain the data
            results.append(result)
        return results
    
    def get_tree_binary(self):
        """Serialize the 8 binary trees into a single binary string with a separator."""
        serialized_trees = []
        for tree in self.trees:
            serialized_trees.append(pickle.dumps(tree))  # Serialize each tree
        return self.SEPARATOR.join(serialized_trees)  # Join them with the separator

    @staticmethod
    def load_tree_binary(data):
        """Deserialize the binary data back into a BinaryTreeManager object."""
        tree_data_list = data.split(BinaryTreeManager.SEPARATOR)  # Split by separator
        tree_manager = BinaryTreeManager()  # Create a new instance
        tree_manager.trees = [pickle.loads(tree_data) for tree_data in tree_data_list]  # Deserialize each tree
        return tree_manager

class BinaryTreeSearch:
    def __init__(self, tree_height=16, tree_sequences=8, threshold=2):
        # Create the BinaryTreeManager once
        self.tree_sequences = tree_sequences
        self.tree_height = tree_height
        self.tree_manager = BinaryTreeManager(tree_height)
        self.threshold = threshold

    def insert(self, id, *bit_sequences):
        if len(bit_sequences) != self.tree_sequences:
            raise ValueError("You must provide {self.tree_sequences} sequences of {self.tree_height}-bit binary strings for insertion.")
        self.tree_manager.insert(id, *bit_sequences)

    def search(self, *bit_sequences):
        if len(bit_sequences) != self.tree_sequences:
            raise ValueError("You must provide {self.tree_sequences} sequences of {self.tree_height}-bit binary strings for search.")

        # Perform search on the 8 binary trees
        results = self.tree_manager.search(*bit_sequences)

        # Count occurrences of each ID across all trees
        id_counts = {}

        for result in results:
            # Even if one result is empty, continue with the other trees
            for id_ in result:
                if id_ in id_counts:
                    id_counts[id_] += 1
                else:
                    id_counts[id_] = 1

        # Filter IDs that appear the required number of times (threshold)
        matches = [id_ for id_, count in id_counts.items() if count >= self.threshold]

        return matches
    
    def get_tree(self):
        return self.tree_manager.get_tree_binary()

    def load_tree(self, data):
        self.tree_manager = BinaryTreeManager.load_tree_binary(data)

# Instantiate BinaryTreeSearch with tree height of 16 and threshold of 4
bt_search = BinaryTreeSearch(tree_height=16, threshold=4)

# Insert data into the 8 trees
insert_start = time.time()
bt_search.insert(42, '1010101010101010', '0001000110101100', '1000001000000011', '0101100100110011',
                 '1100110010000000', '0110001101000000', '0011110001111010', '0111011010011101')
insert_end = time.time()

insert_time = (insert_end - insert_start) * 1000  # Convert to milliseconds
print(f"Time for insertion: {insert_time:.3f} ms")

# Benchmark tree serialization (save)
save_start = time.time()
tree_data = bt_search.get_tree()
save_end = time.time()

save_time = (save_end - save_start) * 1000  # Convert to milliseconds
print(f"Time for saving (serialization): {save_time:.3f} ms")

# Benchmark tree deserialization (load)
load_start = time.time()
bt_search.load_tree(tree_data)
load_end = time.time()

load_time = (load_end - load_start) * 1000  # Convert to milliseconds
print(f"Time for loading (deserialization): {load_time:.3f} ms")

# Search for data in the 8 trees
search_start = time.time()
search_result = bt_search.search('1010101010101010', '0001000110101100', '1000001000000011', '0101100100110011',
                                 '1100110010000000', '0110001101000000', '0011110001111010', '0111011010011101')
search_end = time.time()

search_time = (search_end - search_start) * 1000  # Convert to milliseconds
print(f"Time for search: {search_time:.3f} ms")

print(search_result)
