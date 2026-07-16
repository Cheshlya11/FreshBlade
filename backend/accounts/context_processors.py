import hashlib

AVATAR_COLORS = [
    "#c9a05c",
    "#8b3a3a",
    "#3b5166",
    "#5c7c5c",
    "#7c5c8b",
    "#8b6f3a",
    "#3a6f8b",
    "#8b3a6f",
]


def get_avatar_color(user):
    digest = hashlib.md5(user.email.encode()).hexdigest()
    index = int(digest, 16) % len(AVATAR_COLORS)
    return AVATAR_COLORS[index]


def avatar_context(request):
    if request.user.is_authenticated:
        if request.user.first_name:
            letter = request.user.first_name[0].upper()
        else:
            letter = request.user.email[0].upper()

        return {
            "avatar_color": get_avatar_color(request.user),
            "avatar_letter": letter,
        }
    return {}
