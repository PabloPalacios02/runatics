from supabase import create_client
from config.settings import cargar_secrets


def get_supabase_client():
    secrets = cargar_secrets()

    print("URL:", secrets["SUPABASE_URL"])
    print("KEY:", secrets["SUPABASE_KEY"][:20])

    return create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_KEY"])
