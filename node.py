class Node:
    """
    A class to represent a node in the network.

    Attributes:
    -----------
    node_id : str
        The unique identifier for the node.
    name : str
        The name of the node.
    node_type : str, optional
        The type of the node (default is 'router').

    Methods:
    --------
    __init__(node_id, name, node_type='router'):
        Constructs all the necessary attributes for the Node object.

    __repr__():
        Returns a string representation of the Node object.
    """

    def __init__(self, node_id, name, node_type='router'):
        """
        Constructs all the necessary attributes for the Node object.

        Parameters:
        -----------
        node_id : str
            The unique identifier for the node.
        name : str
            The name of the node.
        node_type : str, optional
            The type of the node (default is 'router').
        """
        self.node_id = node_id
        self.name = name
        self.node_type = node_type

    def __repr__(self):
        """
        Returns a string representation of the Node object.

        Returns:
        --------
        str
            A string representation of the Node object in the format 
            'Node(name, ID=node_id, Type=node_type)'.
        """
        return f"Node({self.name}, ID={self.node_id}, Type={self.node_type})"
