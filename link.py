class Link:
    """
    A class to represent a network link.

    Attributes:
    -----------
    source : str
        The source node of the link.
    destination : str
        The destination node of the link.
    bandwidth : float
        The bandwidth of the link in Gbps (Gigabits per second).

    Methods:
    --------
    __init__(source, destination, bandwidth):
        Constructs all the necessary attributes for the Link object.

    __repr__():
        Returns a string representation of the Link object.
    """

    def __init__(self, source, destination, bandwidth):
        """
        Constructs all the necessary attributes for the Link object.

        Parameters:
        -----------
        source : str
            The source node of the link.
        destination : str
            The destination node of the link.
        bandwidth : float
            The bandwidth of the link in Gbps.
        """
        self.source = source
        self.destination = destination
        self.bandwidth = bandwidth

    def __repr__(self):
        """
        Returns a string representation of the Link object.

        Returns:
        --------
        str
            A string representation of the Link object in the format 
            'Link(source -> destination, Bandwidth=bandwidth Gbps)'.
        """
        return f"Link({self.source} -> {self.destination}, Bandwidth={self.bandwidth} Gbps)"
