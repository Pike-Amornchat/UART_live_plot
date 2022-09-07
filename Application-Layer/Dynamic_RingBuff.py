class Dynamic_RingBuff:

    """
    A class for a list of a certain length - behaves like a list normally until specified size:
    can append data ana access data, with a dynamic length. After threshold is reached, buffer becomes ring buffer,
    but this is easy to use because you just need to do .add(_) to add data without caring about shifting stuff.

    To access the buffer, just do Dynamic_RingBuff.buffer
    To append, do Dynamic_RingBuff.add(_)
    """

    def __init__(self,length):

        # Length is the maximum length before it becomes a ring buffer
        self.length = length
        self.buffer = []

    def add(self,data):

        """
        Add data is like append - appends data to the back of the list. If the list is full it will auto shift the list.
        :param data: Any - whatever you want to append
        :return: None
        """

        # If the max length has been reached:
        if len(self.buffer) == self.length:

            # Delete the last element
            del self.buffer[0]

            # Append new data
            self.buffer.append(data)

        else:

            # Append new data without deleting
            self.buffer.append(data)

