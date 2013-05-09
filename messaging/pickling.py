from pickle import loads, dumps


def serialize_message(message):
    '''Returns a serialized (pickled) message

    Returns:
        The message object serialized (pickled) as a string
    '''
    return dumps(message)


def deserialize_message(message):
    '''Deserialize string as message object

    Args:
        message (str): the message string to deserialize

    Returns:
        message (Message): the deserialized message object
    '''
    return loads(message)
