import typing


class Post(typing.NamedTuple):
    index: str
    path: str


# Posts that can be later send by /post command or automatically
POSTS = [
    Post(
        index='opo_spotify_3h',
        path='posts/manual/one_plus_one_spotify/one_plus_one_spotify_3h.xml'
    ),
    Post(
        index='opo_spotify_10h',
        path='posts/manual/one_plus_one_spotify/one_plus_one_spotify_10h.xml'
    )
]

# For O(1) access by index
POSTS_INDEX_MAP = {p.index: p for p in POSTS}

DAILY_POSTS = [
    # POSTS_INDEX_MAP.get('')
]
