class GooglePhotosScope:
    """
    Google Photos API Scope:

    - "READ": Full read-only access to the user's photo library.
    - "WRITE": Upload-only access; allows adding media but not reading it.
    - "READ_APP_CREATED": Read-only access to media items created by your app.
    - "EDIT_APP_CREATED": Edit access (e.g., title, description) to media items your app created.
    - "SHARING": Permission to manage sharing, such as creating or joining shared albums.
    - "PICKER_READ": Read-only access to all media items, used with the Google Photos Picker API.
    """

    READ = "readonly"                               # Full-library read access
    WRITE = "appendonly"                            # Upload only — allows adding media, no read access
    READ_APP_CREATED = "readonly.appcreateddata"    # Read-only access to media items your app created
    EDIT_APP_CREATED = "edit.appcreateddata"        # Edit access to media items your app created (e.g., title, description)
    SHARING = "sharing"                             # Manage sharing (create/join shared albums)
    PICKER_READ = "mediaitems.readonly"             # Picker read-only access to all media (used with Google Photos Picker API)