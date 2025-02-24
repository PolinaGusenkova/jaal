def wrap_text(text, max_length=15):
    """
    Wraps the input text to a given max line length without breaking words.
    """
    words = text.split()
    max_word_length = max(len(word) for word in words)
    line_length = max(max_length, max_word_length)

    wrapped_lines = []
    current_line = ""

    for word in words:
        # Check if the word fits in the current line
        if len(current_line + " " + word) <= line_length:
            current_line += (" " if current_line else "") + word
        else:
            wrapped_lines.append(current_line)
            current_line = word

    if current_line:
        wrapped_lines.append(current_line)

    return "\n".join(wrapped_lines)