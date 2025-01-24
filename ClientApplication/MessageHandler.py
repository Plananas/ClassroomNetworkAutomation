import uuid
from ClientApplication.MessageCipherHandler import MessageCipherHandler


class MessageHandler:
    FORMAT = 'utf-8'
    HEADER = 64
    BUFFER_SIZE = 1024

    def __init__(self, connection):
        self.connection = connection
        self.message_id = str(uuid.uuid4())[:8]
        self.message_cipher_handler = MessageCipherHandler()
        self.encryption_enabled = False  # Track if encryption is active

    def send_initial_message(self):
        """
        Sends an initial message to set up the encryption keys.
        """
        # Send the public key to the peer
        initial_message = self.message_cipher_handler.get_public_key()
        self.write_unencrypted(initial_message)  # Initial message is unencrypted

        # Receive the peer's public key and generate the encryption key
        peer_key = self.read_unencrypted()
        self.message_cipher_handler.set_peer_public_key(peer_key)
        self.encryption_enabled = True

    def read(self):
        """
        Read an encrypted message from the client.
        """
        message_length = self._read_header()
        if message_length is None:
            return None

        full_message = self._read_message_body(message_length)
        if not full_message:
            return None

        if self.encryption_enabled:
            full_message = self.message_cipher_handler.decrypt(full_message)

        sender_id, content = self._parse_message(full_message)
        if sender_id != self.message_id:
            return content
        return None

    def write(self, message):
        """
        Write an encrypted message to the client.
        """
        # Add message ID and prepare for encryption
        message = f"{self.message_id}:{message}"

        if self.encryption_enabled:
            message = self.message_cipher_handler.encrypt(message)

        # Ensure the message is encoded for transmission
        encoded_message = message.encode(self.FORMAT)
        message_length = len(encoded_message)

        self._send_header(message_length)  # Send the length of the message as a header

        # Send the entire message
        sent_bytes = 0
        while sent_bytes < message_length:
            sent = self.connection.send(encoded_message[sent_bytes:])
            if sent == 0:
                raise RuntimeError("Socket connection broken while sending data")
            sent_bytes += sent

    def read_unencrypted(self):
        """
        Read an unencrypted message (used for initial key exchange).
        """
        message_length = self._read_header()
        if message_length is None:
            return None

        full_message = self._read_message_body(message_length)
        if not full_message:
            return None

        sender_id, content = self._parse_message(full_message)
        if sender_id != self.message_id:
            return content

    def write_unencrypted(self, message):
        """
        Write an unencrypted message (used for initial key exchange).
        """
        full_message = f"{self.message_id}:{message}"
        encoded_message = full_message.encode(self.FORMAT)
        message_length = len(encoded_message)

        self._send_header(message_length)
        self.connection.sendall(encoded_message)

    def _read_header(self):
        """
        Read and parse the message length header.
        """
        try:
            header_data = self.connection.recv(self.HEADER).decode(self.FORMAT).strip()
            return int(header_data)
        except ValueError:
            return None

    def _read_message_body(self, message_length):
        """
        Read the full message body based on the given length.
        """
        received_bytes = 0
        message_parts = []

        while received_bytes < message_length:
            part = self.connection.recv(min(self.BUFFER_SIZE, message_length - received_bytes))
            if not part:
                return None
            message_parts.append(part)
            received_bytes += len(part)

        try:
            return b''.join(message_parts).decode(self.FORMAT)
        except UnicodeDecodeError:
            return None

    def _parse_message(self, full_message):
        """
        Parse the sender ID and content from the full message.
        """
        try:
            sender_id, content = full_message.split(":", 1)
            return sender_id, content
        except ValueError:
            return None, None

    def _send_header(self, message_length):
        """
        Send the message length header.
        """
        header = str(message_length).encode(self.FORMAT)
        padded_header = header + b' ' * (self.HEADER - len(header))
        self.connection.send(padded_header)