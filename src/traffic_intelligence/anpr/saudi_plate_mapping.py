LATIN_TO_ARABIC = {
    "A": "ا", "B": "ب", "J": "ح", "D": "د",
    "R": "ر", "S": "س", "X": "ص", "T": "ط",
    "E": "ع", "G": "ق", "K": "ك", "L": "ل",
    "Z": "م", "N": "ن", "H": "ه", "U": "و",
    "V": "ي",
}

WESTERN_TO_ARABIC_DIGITS = {
    "0": "٠", "1": "١", "2": "٢", "3": "٣",
    "4": "٤", "5": "٥", "6": "٦", "7": "٧",
    "8": "٨", "9": "٩",
}

def latin_to_arabic(plate: str) -> str:
    """Convert a normalized Saudi plate such as 6251EJA."""
    plate = plate.upper().replace(" ", "")

    if len(plate) < 4:
        raise ValueError("Plate text is too short.")

    digits = plate[:-3]
    letters = plate[-3:]

    if not digits.isdigit():
        raise ValueError("Expected digits followed by three letters.")

    if any(char not in LATIN_TO_ARABIC for char in letters):
        raise ValueError("Unsupported Saudi plate letter.")

    arabic_digits = "".join(
        WESTERN_TO_ARABIC_DIGITS[char] for char in digits
    )

    arabic_letters = "".join(
        LATIN_TO_ARABIC[char] for char in letters[::-1]
    )

    return f"{arabic_letters} {arabic_digits}"


if __name__ == "__main__":
    sample = "6251EJA"
    print("Latin:", sample)
    print("Arabic:", latin_to_arabic(sample))
