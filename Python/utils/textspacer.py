# Here's a small script that justifies each line by adding spaces between words
# so every line becomes the same width (the width of the longest original line).
# It prints the resulting "square-ish" block. You can copy this script and run it yourself.
lines = [
    "This is a sample text",
    "that will be justified",
    "to create a square block",
    "of text by adding spaces",
    "between words.",
]


def justify_line(line, width):
    words = line.split()
    if len(words) == 1:
        # single word: pad at end
        return words[0] + " " * (width - len(words[0]))
    total_chars = sum(len(w) for w in words)
    gaps = len(words) - 1
    total_spaces_needed = width - total_chars
    base_space = total_spaces_needed // gaps
    extra = total_spaces_needed % gaps
    parts = []
    for i, w in enumerate(words):
        parts.append(w)
        if i < gaps:
            # distribute the extra spaces to the leftmost gaps
            space_count = base_space + (1 if i < extra else 0)
            parts.append(" " * space_count)
    return "".join(parts)


max_width = max(len(l) for l in lines)
justified = [justify_line(l, max_width) for l in lines]

print(f"Target width: {max_width} characters\n")
for l in justified:
    print(l)
# Also print a visual ruler for confirmation
print("\n" + "-" * max_width)
print("".join(str((i // 10) % 10) for i in range(max_width)))
print("".join(str(i % 10) for i in range(max_width)))
