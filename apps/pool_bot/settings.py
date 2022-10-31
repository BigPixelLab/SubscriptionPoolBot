import datetime

NOTIFY_CUSTOMER_BEFORE_DAYS = datetime.timedelta(days=3)

# Files that will be updated by /updrs command
UPDATE_RESOURCES = [
    ('document', 'resources/NETFLIX-BOUGHT.mp4', 'NETFLIX-BOUGHT.mp4',
     """ update "Service" set bought = %(file_id)s where name = 'netflix' """),

    ('document', 'resources/SPOTIFY-BOUGHT.mp4', 'SPOTIFY-BOUGHT.mp4',
     """ update "Service" set bought = %(file_id)s where name = 'spotify' """),

    ('photo', 'resources/NETFLIX-BANNER.jpg', 'NETFLIX-BANNER.jpg',
     """ update "Service" set banner = %(file_id)s where name = 'netflix' """),

    ('photo', 'resources/SPOTIFY-BANNER.jpg', 'SPOTIFY-BANNER.jpg',
     """ update "Service" set banner = %(file_id)s where name = 'spotify' """)
]
